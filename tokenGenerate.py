import time
import jwt
import requests
import os
from dotenv import load_dotenv
load_dotenv()


service_account_id = os.environ.get('SERCICE_ACCOUNT_ID')
key_id = os.environ.get('KEY_ID')
private_key = os.environ.get('PRIVATE_KEY')



def get_iam_token():
    # Получаем IAM-токен
    now = int(time.time())
    payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': service_account_id,
            'iat': now,
            'exp': now + 360}

    # Формирование JWT
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id})

    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    x = requests.post(url,  
                    headers={'Content-Type': 'application/json'},
                    json = {'jwt': encoded_token}).json()
    token = x['iamToken']
    # print(token)
    return token
#https://github.com/yandex-cloud-examples/yc-yandexgpt-qa-bot-for-docs/blob/main/YandexGPT_OpenSearch.ipynb
# a = get_iam_token()
# print(a)