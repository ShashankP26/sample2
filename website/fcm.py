# website/fcm.py
import requests
from .models import FCMToken
from .fcm_utils import get_access_token

def send_push_fcm(user, title, body):
    access_token = get_access_token()
    print("🔥 ACCESS TOKEN GENERATED")

    project_id = "xentrix-ed813"

    tokens = FCMToken.objects.filter(user=user).values_list("token", flat=True)

    print("🔥 TOKENS:", list(tokens))

    for token in tokens:
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

        payload = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "android": {"priority": "HIGH"}
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=payload)

        print("🔥 STATUS:", response.status_code)
        print("🔥 RESPONSE:", response.text)
