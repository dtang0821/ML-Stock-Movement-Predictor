from alpaca_py.client import AlpacaClient
from pandas_py.client import PandasClient
import numpy as np
from sklearn.model_selection import train_test_split
from models_py.randomforest import RandomForest
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

def main():
    alpaca_client = AlpacaClient()
    pandas_client = PandasClient()

    account = alpaca_client.get_account()
    # print("Account:", account)

    bars = alpaca_client.get_bars("AAPL", timeframe="1Min", limit=3, sort = "asc")
    # print("Bars:", bars)
    # print(pandas_client.json_to_table(bars))

    quote = alpaca_client.get_quote("TSLA", feed = "iex", currency = "USD")
    # print("Quote", quote)
    quote_table = (pandas_client.json_to_table(quote))
    indices = quote_table.index
    X = quote_table.drop(columns=["label"]).values
    y = quote_table["label"].astype(int).values
    #X: shape (n_samples, n_features) - all numeric boolean features
    #y: shape (n_samples, ) 0 or 1

    #test size 20% of data 
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, indices, test_size = 0.2, random_state = 42
    )

    clf = RandomForest(n_trees=20, max_depth = 10)
    clf.fit(X_train, y_train)

    def accuracy(y_true, y_pred):
        return np.sum(y_true == y_pred) / len(y_true)
    
    predictions = clf.predict(X_test)

    #first 100 test indices
    sample_indices = idx_test[:100]

    #extract relevant columns from the original dataframe
    sample_data = quote_table.loc[sample_indices, ['t', 'ap', 'label']].copy()
    sample_data['predicted'] = predictions[:100]

    #sort by timestamp
    sample_data_sorted = sample_data.sort_values('t')

    # #extract sorted columns
    timestamps_sorted = sample_data_sorted['t'].values
    ap_sorted = sample_data_sorted['ap'].values
    pred_sorted = sample_data_sorted['predicted'].values

    # Fix: Get true labels for the sample indices, then sort them alongside predictions
    true_labels = y_test[:100]  # Not sorted
    true_labels_sorted = quote_table.loc[sample_indices, 'label'].values  # From original df
    true_labels_sorted = sample_data.sort_values('t')['label'].values  # Sorted

    #compute accuracy at each point
    is_correct = pred_sorted == true_labels_sorted
    colors = ['green' if correct else 'red' for correct in is_correct]

    plt.figure(figsize = (14,6))
    plt.plot(timestamps_sorted, ap_sorted, label = 'Actual Ask Price', color = 'blue', linewidth = 2)
    plt.scatter(timestamps_sorted, ap_sorted, c = colors, alpha = 0.6, label = "Prediction Accuracy (green = correct, red = wrong)")
    plt.title("Ask Price Movement with Predicted Accuracy Highlighted")
    plt.xlabel("Time")
    plt.ylabel("Ask Price")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    print(quote_table)
    print("Accuracy:", accuracy(y_test, predictions))
    print(classification_report(y_test, predictions))
    print(confusion_matrix(y_test, predictions))
    plt.show()




if __name__ == "__main__":
    main()

# Random Forest is an ensemble model made up of many decision trees. Here's how it would approach your data:

'''
Input Features:
You'd typically feed in:

['ap', 'as', 'bp', 'bs', 'time_sec']
Possibly drop or exclude:

t (timestamp string — not directly usable unless engineered into features like hour/min/sec).

next_ap (leaks the label since it's post-action).

Boolean columns (ax_V, etc.) may not help if always True.

Target:

label: 1 = future price goes up, 0 = no increase or decrease.

How it works:

Each tree randomly selects a subset of features and samples.

It builds decision rules like:

"if bp > 197.2 and ap - bp < 0.05, then label = 1"

Final prediction = majority vote across all trees.'''