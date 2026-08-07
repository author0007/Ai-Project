# 服务器巡检脚本
# 功能：检测本机 CPU、内存、磁盘使用率，当超过 80% 时发送告警，并每天定时发送巡检报告到飞书群

import psutil
import json
import time
import socket
import platform
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from datetime import datetime

# ================= 配置信息（请自行替换） =================
APP_ID = "xxx"
APP_SECRET = "xxx"
CHAT_ID = "xxx"  # 巡检报告群的会话ID
# 告警阈值
ALERT_THRESHOLD = 80

# 定时任务执行时间 (24小时制)
SCHEDULE_TIME = "19:00"


# ================= 飞书客户端初始化 =================
def get_lark_client():
    """创建飞书客户端"""
    return lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.WARNING) \
        .build()


# ================= 系统状态获取 =================
def get_system_status():
    """获取系统 CPU、内存、磁盘使用率"""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')  # Windows 下通常用 'C:\\' 或 '/'

    # 如果是 Windows 系统，获取 C 盘状态
    import platform
    if platform.system() == 'Windows':
        disk = psutil.disk_usage('C:\\')
    else:
        disk = psutil.disk_usage('/')

    return {
        'cpu': {
            'usage': cpu_usage,
            'alert': cpu_usage > ALERT_THRESHOLD
        },
        'memory': {
            'usage': memory.percent,
            'total_gb': round(memory.total / (1024 ** 3), 2),
            'used_gb': round(memory.used / (1024 ** 3), 2),
            'alert': memory.percent > ALERT_THRESHOLD
        },
        'disk': {
            'usage': disk.percent,
            'total_gb': round(disk.total / (1024 ** 3), 2),
            'used_gb': round(disk.used / (1024 ** 3), 2),
            'alert': disk.percent > ALERT_THRESHOLD
        }
    }


# ================= 飞书卡片消息构造 =================
def build_alert_card(status, report_time):
    """构造告警卡片（如果有指标超过阈值）"""
    alerts = []
    if status['cpu']['alert']:
        alerts.append(f"⚠️ **CPU 使用率过高**: {status['cpu']['usage']}% (阈值: {ALERT_THRESHOLD}%)")
    if status['memory']['alert']:
        alerts.append(f"⚠️ **内存使用率过高**: {status['memory']['usage']}% (阈值: {ALERT_THRESHOLD}%)")
    if status['disk']['alert']:
        alerts.append(f"⚠️ **磁盘使用率过高**: {status['disk']['usage']}% (阈值: {ALERT_THRESHOLD}%)")

    alert_text = "\n".join(alerts)

    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🚨 服务器巡检告警"
            },
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**巡检时间**: {report_time}"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": alert_text
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**CPU 使用率**\n{status['cpu']['usage']}%"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**内存使用率**\n{status['memory']['usage']}%\n({status['memory']['used_gb']}GB / {status['memory']['total_gb']}GB)"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**磁盘使用率**\n{status['disk']['usage']}%\n({status['disk']['used_gb']}GB / {status['disk']['total_gb']}GB)"
                        }
                    }
                ]
            }
        ]
    }
    return card


def build_report_card(status, report_time, has_alert):
    """构造巡检报告卡片"""
    template = "red" if has_alert else "green"
    title = "🚨 服务器巡检报告 (存在告警)" if has_alert else "✅ 服务器巡检报告 (一切正常)"

    # 用文字进度条模拟可视化（飞书卡片不支持 progress block）
    def progress_bar(usage):
        bar_length = 20
        filled = int(usage / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        return bar

    # 告警标识
    cpu_alert = " 🔴告警" if status['cpu']['alert'] else ""
    mem_alert = " 🔴告警" if status['memory']['alert'] else ""
    disk_alert = " 🔴告警" if status['disk']['alert'] else ""

    hostname = socket.gethostname()

    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**巡检时间**: {report_time}\n**主机名称**: {hostname}"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**🖥️ CPU 使用率**{cpu_alert}\n{progress_bar(status['cpu']['usage'])} {status['cpu']['usage']}%"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💾 内存使用率**{mem_alert}\n{progress_bar(status['memory']['usage'])} {status['memory']['usage']}%\n({status['memory']['used_gb']}GB / {status['memory']['total_gb']}GB)"
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": False,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📀 磁盘使用率**{disk_alert}\n{progress_bar(status['disk']['usage'])} {status['disk']['usage']}%\n({status['disk']['used_gb']}GB / {status['disk']['total_gb']}GB)"
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"阈值设置: {ALERT_THRESHOLD}% | 巡检脚本 v1.0"
                    }
                ]
            }
        ]
    }
    return card


# ================= 消息发送 =================
def send_feishu_message(chat_id, content, msg_type="interactive"):
    """发送飞书消息到指定会话"""
    client = get_lark_client()

    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type(msg_type)
            .content(json.dumps(content) if msg_type == "interactive" else json.dumps({"text": content}))
            .build()) \
        .build()

    response: CreateMessageResponse = client.im.v1.message.create(request)

    if not response.success():
        lark.logger.error(
            f"发送消息失败, code: {response.code}, msg: {response.msg}, "
            f"log_id: {response.get_log_id()}, "
            f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return False
    
    lark.logger.info(f"消息发送成功, message_id: {response.data.message_id}")
    return True


# ================= 主巡检任务 =================
def run_inspection():
    """执行巡检任务"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行巡检任务...")
    
    try:
        # 1. 获取系统状态
        status = get_system_status()
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 2. 判断是否有告警
        has_alert = status['cpu']['alert'] or status['memory']['alert'] or status['disk']['alert']

        # 3. 发送巡检报告卡片
        print(f"  - CPU: {status['cpu']['usage']}% {'⚠️ 告警!' if status['cpu']['alert'] else '✅'}")
        print(f"  - 内存: {status['memory']['usage']}% {'⚠️ 告警!' if status['memory']['alert'] else '✅'}")
        print(f"  - 磁盘: {status['disk']['usage']}% {'⚠️ 告警!' if status['disk']['alert'] else '✅'}")

        # 构建并发送巡检报告
        report_card = build_report_card(status, report_time, has_alert)
        send_feishu_message(CHAT_ID, report_card)

        # 如果有告警，额外发送一个告警消息（可选，飞书卡片已包含告警信息）
        # if has_alert:
        #     alert_card = build_alert_card(status, report_time)
        #     send_feishu_message(CHAT_ID, alert_card)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 巡检任务完成")
        
    except Exception as e:
        error_msg = f"巡检任务执行失败: {str(e)}"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}")
        # 尝试发送错误通知
        try:
            send_feishu_message(CHAT_ID, f"❌ {error_msg}")
        except Exception:
            pass


# ================= 定时任务调度 =================
def run_scheduler():
    """运行定时任务调度器"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 巡检服务已启动")
    print(f"  - 定时任务时间: 每天 {SCHEDULE_TIME}")
    print(f"  - 目标会话ID: {CHAT_ID}")
    print(f"  - 告警阈值: {ALERT_THRESHOLD}%")
    print("  按 Ctrl+C 停止服务\n")

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        if current_time == SCHEDULE_TIME:
            run_inspection()
            # 等待1分钟避免重复执行
            time.sleep(60)
        else:
            # 计算到下次执行的剩余时间
            target_time = now.replace(hour=int(SCHEDULE_TIME.split(':')[0]), 
                                      minute=int(SCHEDULE_TIME.split(':')[1]), 
                                      second=0, microsecond=0)
            if target_time < now:
                target_time = target_time.replace(day=now.day + 1)
            
            time_diff = (target_time - now).total_seconds()
            # 每30秒检查一次
            sleep_time = min(time_diff, 30)
            time.sleep(sleep_time)


# ================= 入口 =================
if __name__ == "__main__":
    import sys
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "now":
            # 立即执行一次巡检
            run_inspection()
        elif sys.argv[1] == "test":
            # 测试模式：获取状态并打印，不发送消息
            print("=== 系统状态检测 ===")
            status = get_system_status()
            print(f"CPU: {status['cpu']['usage']}% (告警: {status['cpu']['alert']})")
            print(f"内存: {status['memory']['usage']}% (告警: {status['memory']['alert']})")
            print(f"磁盘: {status['disk']['usage']}% (告警: {status['disk']['alert']})")
            print("====================")
    else:
        # 默认启动定时任务
        run_scheduler()

