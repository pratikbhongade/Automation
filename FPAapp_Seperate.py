import os
import json
import logging
import threading
from flask import Flask, render_template, request, jsonify
from validation import validate_application
from email_sender import send_email

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
    environment_url = data.get('environment')
    
    # Find the environment key (e.g., "FPA IT", "FPA QV", etc.) corresponding to the URL
    environment_name = next((name for name, url in config['environments'].items() if url == environment_url), None)
    
    if not environment_name:
        return jsonify({"error": "Invalid environment selected"}), 400
    
    validation_status['status'] = 'Running'
    validation_status['results'] = []

    def validate_environment():
        results, success = validate_application(environment_url)
        validation_status['status'] = 'Completed' if success else 'Failed'
        validation_status['results'] = results
        subject = f"{environment_name} Environment Validation Results"
        send_email(subject, results, success, log_file_path)

    thread = threading.Thread(target=validate_environment)
    thread.start()
    return jsonify({"message": "Validation started"}), 202

@app.route('/status')
def status():
    return jsonify(validation_status)

if __name__ == '__main__':
    app.run(debug=True)
