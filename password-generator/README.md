# 密码生成器

一个基于 Flask 的网页版密码生成器，本地运行，密码学安全，支持批量生成。

## 功能特性

- **随机密码生成**：使用 Python `secrets` 模块，保证密码学安全的随机性
- **自定义密码长度**：支持 4-128 位长度，滑动条实时调节
- **字符类型选择**：
  - 小写字母（a-z）
  - 大写字母（A-Z）
  - 数字（0-9）
  - 特殊字符（!@#$%^&* 等）
- **批量生成**：一次生成 1-100 个密码
- **强度指示器**：根据长度和字符类型实时显示密码强度
- **一键复制**：单个复制或批量复制到剪贴板
- **保证覆盖**：每种选中的字符类型至少在密码中出现一次

## 技术栈

- **后端**：Python + Flask
- **前端**：原生 HTML / CSS / JavaScript（无第三方依赖）
- **安全**：`secrets` 模块（基于操作系统的密码学安全随机源）

## 项目结构

```
password-generator/
├── app.py              # Flask 后端与密码生成逻辑
├── requirements.txt    # Python 依赖
├── README.md           # 项目文档
└── templates/
    └── index.html      # 前端页面
```

## 快速开始

### 1. 安装依赖

```bash
cd password-generator
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

### 3. 访问页面

在浏览器中打开：

```
http://127.0.0.1:5000
```

## 使用方法

1. **设置长度**：拖动滑块调整密码长度（4-128 位）
2. **选择字符类型**：勾选需要包含的字符类型（至少选一种）
3. **设置数量**：输入需要生成的密码数量（1-100）
4. **生成**：点击"生成密码"按钮
5. **复制**：点击单个密码右侧的 📋 图标复制，或点击"复制全部"批量复制

## API 接口

### `POST /generate`

批量生成密码。

**请求参数（JSON）**：

| 参数 | 类型 | 说明 | 范围 |
|------|------|------|------|
| length | int | 密码长度 | 4-128 |
| char_types | string[] | 字符类型 | lowercase / uppercase / digits / special |
| count | int | 生成数量 | 1-100 |

**请求示例**：

```bash
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 16, "char_types": ["lowercase","uppercase","digits","special"], "count": 3}'
```

**响应示例**：

```json
{
  "count": 3,
  "passwords": ["aB3$kL9#mN2@pQ7%", "xY5&tR8^wV1*cU4#", "zT6#bE2@nM9$kL3&"]
}
```

## 安全说明

- 所有密码均通过 `secrets.SystemRandom()` 生成，比 `random` 模块更安全
- 每种选中的字符类型保证至少出现一次，避免字符集缺失
- 生成后会在内存中打乱顺序，避免前几位固定为某类字符
- 服务仅监听 `127.0.0.1`，不对外网暴露

## 配置说明

如需修改默认配置，编辑 [app.py](app.py) 顶部的常量：

- `MAX_LENGTH`：最大密码长度（默认 128）
- `MAX_COUNT`：最大批量生成数量（默认 100）
- `CHARACTER_SETS`：可自定义各类字符集内容

## 浏览器兼容性

支持所有现代浏览器（Chrome / Firefox / Edge / Safari 最新版本）。
