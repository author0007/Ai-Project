# Weather Answerbook Bot

一个基于飞书（Lark）开放平台 SDK 的智能机器人，支持天气查询和答案之书功能。

## 功能说明

本项目实现一个飞书机器人，具备以下功能：

1. **天气查询**：用户输入 `1+城市名`，机器人调用 UAPI 天气接口查询天气信息，支持多城市连续查询。
2. **答案之书**：用户输入 `2+问题`，机器人调用 UAPI 答案之书接口获取神秘答案。
3. **规则提示**：用户发送非指令消息时，机器人会回复使用规则说明。

## 使用规则

在飞书中 `@机器人` 发送消息：

| 指令 | 格式 | 示例 |
|------|------|------|
| 查询天气 | `1+城市名` | `1北京` 或 `1北京,上海,广州` |
| 查询答案之书 | `2+问题` | `2我今天运气如何？` |
| 其他消息 | 任意内容 | 机器人会回复使用规则 |

### 天气查询示例

- 单城市：`@机器人 1北京`
- 多城市（逗号分隔）：`@机器人 1北京,上海,广州`

天气信息包括：温度、体感温度、天气状况、风力、湿度、空气质量、紫外线指数等。

### 答案之书示例

- `@机器人 2我应该接受这份工作吗？`
- `@机器人 2今天适合出门吗？`

## 环境依赖

- Python 3.7+
- [lark-oapi](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development) （飞书官方 Python SDK）
- [requests](https://requests.readthedocs.io/) （HTTP 请求库）

## 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install lark-oapi requests
```

## 使用前准备

### 1. 飞书开放平台配置

1. 在 [飞书开放平台](https://open.feishu.cn/) 创建一个企业自建应用。
2. 为应用添加「机器人」能力。
3. 在「事件与回调」中订阅 `im.message.receive_v1` 事件。
4. 获取应用的 `App ID` 和 `App Secret`。

### 2. 修改配置

打开 [app.py](app.py)，替换以下占位符：

```python
# 飞书应用凭证
app_id = "你的 App ID"
app_secret = "你的 App Secret"

# UAPI 配置（可选）
UAPI_KEY = ""  # 如需认证，填入你的 UAPI Key
```

### 3. 获取 UAPI Key（可选）

访问 [UAPI 开发者平台](https://uapis.cn/) 注册账号并获取免费 API Key。大部分接口可使用免费访客积分，无需 Key 也能调用。

## 运行方式

```bash
python app.py
```

启动后，机器人会通过 WebSocket 与飞书服务端建立长连接，并监听员工发送的消息。

## 工作流程

### 天气查询流程

1. 员工在飞书中 `@机器人` 发送消息，例如：`@机器人 1北京`
2. 机器人解析消息，识别指令 `1` 和城市名 `北京`
3. 调用 UAPI 天气接口：`GET https://uapis.cn/api/v1/misc/weather?city=北京&extended=true`
4. 格式化天气信息并回复用户

### 答案之书流程

1. 员工在飞书中 `@机器人` 发送消息，例如：`@机器人 2我今天运气如何？`
2. 机器人解析消息，识别指令 `2` 和问题 `我今天运气如何？`
3. 调用 UAPI 答案之书接口：`POST https://uapis.cn/api/v1/answerbook/ask`
4. 获取答案并回复用户

## API 接口说明

### 天气查询 API

- **接口地址**：`https://uapis.cn/api/v1/misc/weather`
- **请求方式**：GET
- **请求参数**：
  - `city`：城市名称（支持中文/英文）
  - `extended=true`：返回扩展气象字段（温度、湿度、空气质量等）
- **文档**：[https://uapis.cn/docs/api-reference/get-misc-weather](https://uapis.cn/docs/api-reference/get-misc-weather)

### 答案之书 API

- **接口地址**：`https://uapis.cn/api/v1/answerbook/ask`
- **请求方式**：POST
- **请求体**：
  ```json
  {
    "question": "你想要提问的问题"
  }
  ```
- **文档**：[https://uapis.cn/docs/api-reference/post-answerbook-ask](https://uapis.cn/docs/api-reference/post-answerbook-ask)

## 关键代码说明

- [send_message(chat_id, content)](app.py#L20-L42)：创建飞书 client，构造消息请求，向指定会话发送文本消息。
- [get_weather(city)](app.py#L45-L67)：调用 UAPI 天气接口，包含异常处理（超时、网络错误、HTTP错误等）。
- [format_weather_info(weather_data)](app.py#L70-L127)：格式化天气信息，包括位置、温度、天气状况、风力、湿度、空气质量等。
- [query_weather(cities_text)](app.py#L130-L142)：支持多城市查询，按逗号/顿号分隔城市名。
- [ask_answerbook(question)](app.py#L145-L165)：调用 UAPI 答案之书 POST 接口。
- [do_p2_im_message_receive_v1(data)](app.py#L178-L247)：消息接收事件处理函数，解析指令并分发到对应功能。
- [main()](app.py#L261-L265)：使用 `lark.ws.Client` 建立 WebSocket 长连接并启动事件监听。

## 异常处理

程序已添加完整的异常处理：

- **天气查询异常**：
  - 请求超时（10秒）
  - 网络连接失败
  - HTTP 错误
  - 城市不存在（API 返回错误信息）
- **答案之书异常**：
  - 请求超时（10秒）
  - 网络连接失败
  - HTTP 错误
  - 问题为空

## 技术架构

```
用户 → 飞书消息 → 机器人 → 指令解析 → 功能分发
                                    ├── 1 → 天气查询 → UAPI天气API
                                    └── 2 → 答案之书 → UAPI答案之书API
                                                    ↓
                                              格式化输出 → 回复用户
```

## 参考资料

- [飞书开放平台 SDK 使用说明（Python）](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development)
- [发送消息 API 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
- [UAPI 天气查询接口文档](https://uapis.cn/docs/api-reference/get-misc-weather)
- [UAPI 答案之书接口文档](https://uapis.cn/docs/api-reference/post-answerbook-ask)
