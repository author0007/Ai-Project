# ai-send-in-second

一个基于飞书（Lark）开放平台 SDK 的简单机器人示例，使用 WebSocket 长连接接收员工发送给机器人的消息，并将处理后的内容回复给员工。

## 功能说明

本项目对应飞书 SDK 教程的两个练习目标：

1. **接收消息**：创建一个飞书机器人，接收员工发给机器人的消息，并打印到控制台。
2. **回复消息**：根据员工输入的消息内容进行处理后，回复给员工。例如：解析员工消息中 `@机器人` 后的文本，并回复 "你说的是: xxx 吗"。

## 环境依赖

- Python 3.7+
- [lark-oapi](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development) （飞书官方 Python SDK）

## 安装依赖

```bash
pip install lark-oapi
```

## 使用前准备

1. 在 [飞书开放平台](https://open.feishu.cn/) 创建一个企业自建应用。
2. 为应用添加「机器人」能力。
3. 在「事件与回调」中订阅 `im.message.receive_v1` 事件。
4. 获取应用的 `App ID` 和 `App Secret`。
5. 将 [app.py](app.py) 中的占位符替换为真实凭证：

   ```python
   app_id = "你的 App ID"
   app_secret = "你的 App Secret"
   ```

## 运行方式

```bash
python app.py
```

启动后，机器人会通过 WebSocket 与飞书服务端建立长连接，并监听员工发送的消息。

## 工作流程

1. 员工在飞书中 `@机器人` 并发送一条消息，例如：`@机器人 你好呀`。
2. 机器人接收到 `P2ImMessageReceiveV1` 事件，打印日志到控制台。
3. 解析消息内容：
   - 从原始 JSON `{"text":"@_user_1 你好呀"}` 中提取 `text` 字段。
   - 按空格分隔，取 `@_user_1` 之后的部分作为有效内容。
4. 机器人调用 `send_message` 向当前会话回复：`你说的是: 你好呀 吗`。

## 关键代码说明

- [send_message(chat_id, content)](app.py#L14-L42)：创建飞书 client，构造 `CreateMessageRequest`，向指定会话发送文本消息。
- [do_p2_im_message_receive_v1(data)](app.py#L45-L76)：消息接收事件处理函数，负责解析消息内容并触发回复。
- [main()](app.py#L86-L89)：使用 `lark.ws.Client` 建立 WebSocket 长连接并启动事件监听。

## 参考资料

- [飞书开放平台 SDK 使用说明（Python）](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development)
- [发送消息 API 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
