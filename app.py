from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from utils.email_service import SendPostEmailService

load_dotenv()

app = Flask(__name__)
app.config['SENDPOST_API_KEY'] = os.getenv('SENDPOST_API_KEY')
app.config['SENDPOST_FROM_EMAIL'] = os.getenv('SENDPOST_FROM_EMAIL', 'hello@playwithsendpost.io')
app.config['SENDPOST_FROM_NAME'] = os.getenv('SENDPOST_FROM_NAME', 'SendPost')

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'SendPost Flask Example API'})

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        to = data.get('to')
        subject = data.get('subject')
        html_body = data.get('htmlBody')
        
        if not all([to, subject, html_body]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, subject, htmlBody'
            }), 400
        
        result = SendPostEmailService.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=data.get('textBody')
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'messageId': result['message_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
