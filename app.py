# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import os
import pandas as pd
from dotenv import load_dotenv
import subprocess
import json
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.route('/')
def home():
    return "I'm alive"

@app.route('/update_sendOK', methods=['POST'])
def update_sendOK():
    data = request.json
    bid_no = data.get('bidNtceNo')
    file_path_key = data.get('filePathKey')
    file_path = {
        'bids': 'filtered_bids_data.csv',
        'prebids': 'filtered_prebids_data.csv',
        'bidwin': 'filtered_bidwin_data.csv'
    }.get(file_path_key)

    if not bid_no or not file_path:
        return jsonify({'status': 'error', 'message': 'Missing bid number or file path'}), 400

    script_path = os.path.join(os.path.dirname(__file__), "update_sendOK.py")
    command = f'python {script_path} {file_path} {bid_no}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to update item'}), 500

@app.route('/send_discord_message', methods=['POST'])
def send_discord_message():
    data = request.json
    bid_no = data.get('bidNtceNo')
    if not bid_no:
        return jsonify({'status': 'error', 'message': 'Missing bid number'}), 400

    message = f"등록번호 {bid_no} 이(가) 체크되었습니다."
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    if response.status_code == 204:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send Discord message'}), 500

@app.route('/data.json', methods=['GET'])
def get_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        content_type='application/json; charset=utf-8'
    )
    return response

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), use_reloader=False)

if __name__ == "__main__":
    run_flask()

# .\\.venv\\Scripts\\activate
# python app.py