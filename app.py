from flask import Flask, request, abort

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

configuration = Configuration(access_token='F6j/vI07g63ColyEjSZABfSqrxUfd0S7c2KOwtCa0VvVJmN7oYtwOHmUrFRWL54svPWex5N7mWtGYtI2owgACLlENIT5nM3vR0QDw/pVEi51LuSzkzc4WTbcH7wUipI1hz4VZbQ2acPEX3AtmdoOYgdB04t89/1O/w1cDnyilFU=')
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
    return 'OK'

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

def main():
    with ApiClient(configuration) as api_client:
        linebot_api = MessagingApi(api_client)
        linebot_blob_api = MessagingApiBlob(api_client)
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

        rm_to_create = RichMenuRequest(
            size=RichMenuSize(width=rm_object_a['size']['width'],
                              height=rm_object_a['size']['height']),
            selected=rm_object_a['selected'],
            name=rm_object_a['name'],
            chat_bar_text=rm_object_a['chatBarText'],
            areas=areas
        )

        rm_id = linebot_api.create_rich_menu(rich_menu_request=rm_to_create).rich_menu_id
        print (rm_id)
        
        with open('./richmenu-a.png', 'rb') as image:
            linebot_blob_api.set_rich_menu_image(
                rich_menu_id=rm_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        linebot_api = MessagingApi(api_client)
        linebot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

if __name__ == "__main__":
    app.run()
