from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/api/bids', methods=['GET'])
def get_bids():
    df = pd.read_csv("filtered_bids_data.csv")
    bids = df.to_dict(orient='records')
    return jsonify(bids)

@app.route('/api/prebids', methods=['GET'])
def get_prebids():
    df = pd.read_csv("filtered_prebids_data.csv")
    prebids = df.to_dict(orient='records')
    return jsonify(prebids)

@app.route('/api/bidwins', methods=['GET'])
def get_bidwins():
    df = pd.read_csv("filtered_bidwin_data.csv")
    bidwins = df.to_dict(orient='records')
    return jsonify(bidwins)

if __name__ == '__main__':
    app.run(debug=True)
