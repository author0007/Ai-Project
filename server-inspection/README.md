# 服务器巡检报告任务

一个基于 Python 的服务器自动化巡检脚本，用于检测本机 CPU、内存、磁盘使用率，并通过飞书机器人发送卡片形式的巡检报告。

## 功能特性

- 📊 **系统监控**: 实时检测 CPU、内存、磁盘使用率
- 🚨 **告警机制**: 当使用率超过设定阈值（默认 80%）时，卡片会标红警示
- 💬 **飞书卡片**: 以美观的飞书交互卡片形式发送巡检报告
- ⏰ **定时任务**: 支持每天定时（默认 19:00）自动发送巡检报告
- 🖥️ **跨平台**: 支持 Windows 和 Linux 系统

## 依赖安装

```bash
pip install psutil lark-oapi
```

## 配置说明

编辑 `inspection.py` 文件，修改以下配置：

```python
# 飞书应用凭证（必填）
APP_ID = "your_app_id_here"      # 替换为你的飞书 App ID
APP_SECRET = "your_app_secret_here"  # 替换为你的飞书 App Secret

# 巡检报告群的会话ID（必填）
CHAT_ID = "your_chat_id_here"  # 替换为你的飞书群会话 ID

# 告警阈值（可选，默认 80%）
ALERT_THRESHOLD = 80

# 定时任务执行时间（可选，默认 19:00）
SCHEDULE_TIME = "19:00"
```

### 如何获取飞书 App ID 和 App Secret？

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建一个企业自建应用
3. 在「凭证与基础信息」页面获取 App ID 和 App Secret
4. 开启机器人能力，并添加到目标群组

### 如何获取群会话 ID (Chat ID)？

1. 在飞书中打开目标群聊
2. 点击群设置 → 群信息
3. 查看 Chat ID 或使用 [飞书 API 调试台](https://open.feishu.cn/api-explorer/) 获取

## 使用方法

### 1. 启动定时巡检服务

```bash
python inspection.py
```

启动后，脚本会在后台持续运行，每天指定时间（默认 19:00）自动执行巡检任务。

### 2. 立即执行一次巡检

```bash
python inspection.py now
```

立即执行一次巡检并发送报告，无需等待定时任务。

### 3. 测试模式（仅检测，不发送消息）

```bash
python inspection.py test
```

仅获取系统状态并在控制台打印，不向飞书发送任何消息。用于调试配置是否正确。

## 飞书卡片效果示例

### ✅ 正常状态
- 卡片头部为绿色
- 各项指标正常显示

### 🚨 告警状态
- 卡片头部为红色
- 超阈值指标的进度条和文字变为红色
- 便于快速识别问题

## 目录结构

```
server-inspection/
├── inspection.py    # 巡检脚本主文件
└── README.md        # 说明文档
```

## 注意事项

1. **飞书应用权限**: 确保飞书机器人已加入到目标群组
2. **网络访问**: 运行环境需要能访问飞书 API（`open.feishu.cn`）
3. **系统权限**: 脚本需要读取系统信息的权限（通常默认即可）
4. **开机自启**: 如需开机自启，可将脚本配置为系统服务或使用 Windows 任务计划程序 / Linux crontab

## Linux crontab 配置示例

如果不想使用 Python 内置的定时任务，可以使用系统 crontab：

```bash
# 编辑 crontab
crontab -e

# 添加以下行，表示每天 19:00 执行
0 19 * * * /usr/bin/python3 /path/to/inspection.py now >> /var/log/inspection.log 2>&1
```

## Windows 任务计划程序配置

1. 打开「任务计划程序」
2. 创建基本任务 → 触发器设置为每天 19:00
3. 操作设置为启动程序，程序路径为 `python.exe`，参数为 `inspection.py now`
4. 起始位置设置为脚本所在目录

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError: No module named 'psutil'` | 运行 `pip install psutil` |
| 消息发送失败 | 检查 APP_ID、APP_SECRET、CHAT_ID 是否正确 |
| 机器人无法发送消息 | 确保机器人已加入群聊，并具有发送消息权限 |
| 磁盘检测失败 | Windows 下检查是否为 C 盘，Linux 下检查 `/` 目录 |

## 许可证

MIT License
