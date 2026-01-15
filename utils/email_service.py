import sendpost_python_sdk
from sendpost_python_sdk.api import EmailApi
from sendpost_python_sdk.models import EmailMessageObject, EmailAddress, Recipient
import os
import re

class SendPostEmailService:
    @staticmethod
    def send_email(
        to,
        subject,
        html_body,
        text_body=None,
        from_email=None,
        from_name=None,
        groups=None,
        track_opens=True,
        track_clicks=True,
        custom_fields=None,
    ):
        try:
            configuration = sendpost_python_sdk.Configuration(
                host="https://api.sendpost.io/api/v1"
            )
            configuration.api_key['subAccountAuth'] = os.getenv('SENDPOST_API_KEY')
            
            with sendpost_python_sdk.ApiClient(configuration) as api_client:
                email_message = EmailMessageObject()
                
                email_message.var_from = EmailAddress(
                    email=from_email or os.getenv('SENDPOST_FROM_EMAIL', 'hello@playwithsendpost.io'),
                    name=from_name or os.getenv('SENDPOST_FROM_NAME', 'SendPost')
                )
                
                if isinstance(to, str):
                    recipients = [Recipient(email=to)]
                elif isinstance(to, list):
                    recipients = []
                    for recipient in to:
                        if isinstance(recipient, str):
                            recipients.append(Recipient(email=recipient))
                        elif isinstance(recipient, dict):
                            recipients.append(Recipient(
                                email=recipient.get('email'),
                                name=recipient.get('name'),
                                custom_fields=recipient.get('customFields') or custom_fields
                            ))
                        else:
                            recipients.append(recipient)
                else:
                    recipients = [Recipient(email=to)]
                
                email_message.to = recipients
                email_message.subject = subject
                email_message.html_body = html_body
                email_message.text_body = text_body or SendPostEmailService._html_to_text(html_body)
                email_message.track_opens = track_opens
                email_message.track_clicks = track_clicks
                
                if groups:
                    email_message.groups = groups if isinstance(groups, list) else [groups]
                
                response = EmailApi(api_client).send_email(email_message)[0]
                
                return {
                    'success': True,
                    'message_id': response.message_id,
                    'data': response
                }
        except sendpost_python_sdk.exceptions.ApiException as e:
            return {
                'success': False,
                'message_id': None,
                'error': f"API Error {e.status}: {e.body}"
            }
        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }
    
    @staticmethod
    def _html_to_text(html):
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()
