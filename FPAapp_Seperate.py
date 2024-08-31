import os
import json
import time
import logging
from flask import Flask, render_template, request, jsonify
import threading
from validation_logic import validate_application
from email_sender import send_email
import pythoncom

app = Flask(__name__)

# Load JSON configuration
with open('validation_config.json') as config_file:
    config = json.load(config_file)

# Set up logging
log_file_path = os.path.join(os.getcwd(), 'validation.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

validation_status = {'status': 'Not Started', 'results': []}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_validation', methods=['POST'])
def start_validation():
    data = request.json
    environment = data.get('environment')

    # Find the appropriate environment key in the JSON
    environment_key = next((key for key in config['environments'] if environment in key), None)
    if not environment_key:
        return jsonify({"error": "Invalid environment selected"}), 400

    validation_status['status'] = 'Running'
    validation_status['results'] = []

    def validate_environment():
        pythoncom.CoInitialize()
        results, success = validate_application(environment_key, config)
        validation_status['status'] = 'Completed' if success else 'Failed'
        validation_status['results'] = results
        subject = f"{environment_key} Environment Validation Results"
        send_email(subject, results, success, log_file_path)
        pythoncom.CoUninitialize()

    thread = threading.Thread(target=validate_environment)
    thread.start()
    return jsonify({"message": "Validation started"}), 202

@app.route('/status')
def status():
    return jsonify(validation_status)

if __name__ == '__main__':
    app.run(debug=True)
