from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from config.setting import settings

def send_message(messages=[{"type": "TextBlock",'text': '**content.**'}], actions=None, mention=None, token=settings.teams_channel_url):
    url = token
    headers = {
        'Content-type': 'application/json'
    }
    data = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": messages,
                    "actions": actions,
                    "msteams": {
                        "width": "Full"
                    }
                }
            }
        ]
    }
    if mention:
        messages.append({"type": "TextBlock",'text': '<at>mention</at>'})
        match mention:
            case 'DE':
                data['attachments'][0]['content']['msteams']['entities'] = [
                    {
                        "type": "mention",
                        "text": "<at>mention</at>",
                        "mentioned": {
                            "id": "de@distantnova.com",
                            "name": "DE活下去"
                        }
                    }
                ]
            case 'BR':
                data['attachments'][0]['content']['msteams']['entities'] = [
                    {
                        "type": "mention",
                        "text": "<at>mention</at>",
                        "mentioned": {
                            "id": "barlin@clusters.tw",
                            "name": "Barlin"
                        }
                    }
                ]
    
    retry_policy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[400, 429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_policy)
    with Session() as session:
        session.mount('https://', adapter)
        r = session.post(url, headers=headers, json=data, timeout=30)
    return r