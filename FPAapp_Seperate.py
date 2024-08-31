from flask import Flask, render_template, request, jsonify
import threading
from validation import validate_application, log_file_path
from email_sender import send_email

app = Flask(__name__)

validation_status = {'status': 'Not Started', 'results': []}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_validation', methods=['POST'])
def start_validation():
    data = request.json
    environment = data.get('environment')
    validation_status['status'] = 'Running'
    validation_status['results'] = []

    def validate_environment():
        results, success = validate_application(environment)
        validation_status['status'] = 'Completed' if success else 'Failed'
        validation_status['results'] = results
        subject = f"FPA {environment.upper()} Environment Validation Results"
        send_email(subject, results, success, log_file_path)

    thread = threading.Thread(target=validate_environment)
    thread.start()
    return jsonify({"message": "Validation started"}), 202

@app.route('/status')
def status():
    return jsonify(validation_status)

if __name__ == '__main__':
    app.run(debug=True)
