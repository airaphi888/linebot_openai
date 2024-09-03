from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


def GPT_response(text):
    # 接收回應
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[
                {"role": "system", "content": "你是一個有用的助手。"},
                {"role": "user", "content": text}
            ], temperature=0.2, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['message']['content'].replace('。','')
    return answer


# 監聽所有來自 /callback 的 Post Request
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
        abort(400)
    return 'OK'


from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    
    # 获取机器人的用户 ID
    bot_user_id = '阿榮慢慢來(Aron2)'  # 将此替换为你实际的 Bot 的 user ID
    
    # 检查是否包含机器人 ID（被 @）
    if bot_user_id in msg:
        try:
            # 调用 GPT-4 API 获取回复
            GPT_answer = GPT_response(msg)
            print(GPT_answer)  # 调试信息
            # 将回复发送回用户
            line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
        except Exception as e:
            # 捕获所有异常并处理
            print(traceback.format_exc())  # 打印完整的错误堆栈信息
            # 回复错误信息给用户
            error_message = '串接有點問題啦 阿榮QQ，你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(error_message))
    else:
        # 如果没有 @ 到机器人，可以选择不做任何操作
        pass

        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
