# SDK 使用说明 SDK user guide：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development

#1. 创建一个飞书机器人，接收员工发给机器人的消息，打印到控制台【done】
#2. 飞书机器人回复员工消息，根据员工输入的消息内容进行处理后，回复给员工。例如将员工发的消息加一个当前时间，然后回复给员工。

import lark_oapi as lark
from datetime import datetime
import json
from lark_oapi.api.im.v1 import *

app_id = "xxx"
app_secret = "xxx"

def send_message(chat_id: str,content: str):
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": content}))
            .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')

    #获取消息事件
    event = data.event
    if not event:
        print('event is empty')
        return

    message = event.message
    if not message:
        print("message is empty")
        return

    sender_id = event.sender.sender_id.open_id
    chat_id = message.chat_id
    content = message.content
    print(f'收到消息 - 发送者: {sender_id}, 会话ID: {chat_id}, 内容: {content}')

    #处理消息内容
    # 步骤1：解析JSON，提取text字段的值,原始内容 {"text":"@_user_1 你好呀"}
    data = json.loads(content)
    text_content = data.get('text', '')  # 得到："@_user_1 你好呀"

    # 步骤2：按空格分隔字符串，提取后面的部分
    # split(' ') 按单个空格分隔，filter(None, ...) 过滤空字符串（避免多个空格的情况）
    parts = list(filter(None, text_content.split(' ')))

    replay= parts[1]

    # 回复消息
    send_message(chat_id, f"你说的是: {replay} 吗")



#SDK标准写法
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


def main():
    cli = lark.ws.Client(app_id, app_secret,
                        event_handler=event_handler, log_level=lark.LogLevel.DEBUG)
    cli.start()

if __name__ == "__main__":
    main()