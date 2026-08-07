# SDK 使用说明 SDK user guide：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development

#使用应用飞书机器人，接收飞书用户发给机器人的消息，打印到控制台

import lark_oapi as lark


#这是飞书SDK约定的消息接收事件处理函数，当机器人接收到消息时，会调用此函数, 它将接收到的消息数据以格式化的JSON形式打印到控制台
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')

# 固定写法, 飞书机器人注册事件 Register event
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


def main():
    # 构建 client Build client
    cli = lark.ws.Client("your-key", "your-secret",
                        event_handler=event_handler, log_level=lark.LogLevel.DEBUG)
    # 建立长连接 Establish persistent connection
    cli.start()

if __name__ == "__main__":
    main()