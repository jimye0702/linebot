from flask import Flask, request, abort
import requests, json, os
import sqlite3

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, RichMenuRequest, MessagingApiBlob,
    RichMenuArea, RichMenuSize, RichMenuBounds, URIAction, MessageAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

config = Configuration(access_token='F6j/vI07g63ColyEjSZABfSqrxUfd0S7c2KOwtCa0VvVJmN7oYtwOHmUrFRWL54svPWex5N7mWtGYtI2owgACLlENIT5nM3vR0QDw/pVEi51LuSzkzc4WTbcH7wUipI1hz4VZbQ2acPEX3AtmdoOYgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c5c89c172e454a13de0ee692c5d603f4')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK', body

def rm_object_json():
    return {
        "size":{"width":2500, "height":1686},
        "selected":False,
        "name":"richmenu-a",
        "chatBarText":"功能表單",
        "areas":[
            {
                "bounds":{"x":0, "y":0, "width":1250, "height":1686},
                "action":{"type":"uri", "uri":"https://www.petsmall.com.tw/petsmall/index.php"}
            },
            {
                "bounds":{"x":1251, "y":0, "width":1250, "height":1686},
                "action":{"type":"message", "text":"會員登入"}
            }
            ]
    }

def create_action(action):
    if action['type'] == 'uri':
        return URIAction(uri=action.get('uri'))
    else:
        return MessageAction(test=action.get('text'))

def main(config=config):
    with ApiClient(config) as api_client:
        linebot_api = MessagingApi(api_client)
        #linebot_blob_api = MessagingApiBlob(api_client)
        rm_object_a = rm_object_json()
        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action']))
            for info in rm_object_a['areas'] 
        ]

        #https://developers.line.biz/en/reference/messaging-api/#create-rich-menu
        #Get RichMenu List
        header = {'Authorization':f'Bearer {config.access_token}'}
        req_ls = requests.request('GET', 'https://api.line.me/v2/bot/richmenu/list',
                                   headers=header)

        #Delete RichMenu All
        if len(req_ls.json()['richmenus']) == 0:
            pass
        else:
            header = {'Authorization':f'Bearer {config.access_token}'}
            for n in range(len(req_ls.json()['richmenus'])):
                req_id = req_ls.json()['richmenus'][n]['richMenuId']
                req_del = requests.request('DELETE', f'https://api.line.me/v2/bot/richmenu/{req_id}',
                                            headers=header)
        
        #Create RichMenu        
        header = {'Authorization':f'Bearer {config.access_token}','Content-Type':'application/json'}
        req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                                headers=header,data=json.dumps(rm_object_json()).encode('UTF-8'))

        #Upload image for RichMenu
        header = {'Authorization':f'Bearer {config.access_token}'}
        req_ls = requests.request('GET', 'https://api.line.me/v2/bot/richmenu/list',
                                   headers=header)   
        rm_id = req_ls.json()['richmenus'][0]['richMenuId']
        path = os.getcwd()
        with open(path+'/richmenu-a.png', 'rb') as f:
            header = {'Authorization':f'Bearer {config.access_token}','Content-Type':'image/png'}
            req = requests.request('POST', f'https://api-data.line.me/v2/bot/richmenu/{rm_id}/content',
                                    headers=header, data=f)
        #Set Default RichMenu                                    
        header = {'Authorization':f'Bearer {config.access_token}'}
        req = requests.request('POST', f'https://api.line.me/v2/bot/user/all/richmenu/{rm_id}',
                                headers=header)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event, body):
    with ApiClient(config) as api_client:
        #body = json(request.get_data(as_text=True))
        event = body['events'][0]
        user_id = event['source']['userId']
        linebot_api = MessagingApi(api_client)
        linebot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=user_id)]
            )
        )

main()

if __name__ == "__main__":
    app.run()
