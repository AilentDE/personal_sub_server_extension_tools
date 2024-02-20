import requests
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
    r = requests.post(url, headers=headers, json=data, timeout=30)
    return r