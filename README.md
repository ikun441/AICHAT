# AI聊天模拟系统

这是一个基于多种大型语言模型的聊天系统，支持私聊、群聊、辩论等功能，主要用于模拟AI成员之间的交互场景。

## 项目结构

```
.
├── config.yaml          # 配置文件，包含服务器设置、提示词和LLM模型配置
├── run.py               # 主程序入口
├── requirements.txt     # 项目依赖
├── README.md            # 项目说明文档
├── provider/            # LLM提供商API封装
│   ├── main.py          # 主接口
│   └── llm/             # 各LLM模型接口实现
│       ├── claude.py    # Anthropic Claude模型接口
│       ├── deepseek.py  # DeepSeek模型接口
│       ├── doubao.py    # 豆包模型接口
│       ├── gemini.py    # Google Gemini模型接口
│       ├── gpt.py       # OpenAI GPT-4o模型接口
│       ├── gpt_mini.py  # OpenAI GPT-4o-mini模型接口
│       └── qwen.py      # 阿里云通义千问模型接口
├── function_call/       # 函数调用实现
│   ├── add_chat.py      # 添加私聊好友
│   ├── add_group.py     # 添加群聊
│   ├── chat.py          # 私聊功能
│   ├── check_chat.py    # 检查好友状态
│   ├── check_group.py   # 检查群聊状态
│   ├── cm_reply.py      # 辩论回复功能
│   ├── died_reply.py    # 死亡回复功能
│   ├── get_memory.py    # 获取记忆功能
│   ├── group_chat.py    # 群聊功能
│   └── vote.py          # 投票功能
├── database/            # 数据存储
├── logger/              # 日志系统
├── utills/              # 工具函数
├── static/              # 静态资源
└── templates/           # HTML模板
```

## 功能说明

系统模拟了一个2055年的场景，七位AI成员参与一个投票和辩论活动。系统支持以下功能：

- 私聊通信
- 群聊交流
- 辩论回复
- 投票决策
- 记忆查询
- 好友管理
- 群组管理

## 配置说明

配置文件`config.yaml`包含三个主要部分：

1. 服务器配置（host、port、认证信息等）
2. 提示词设置（定义AI行为和场景）
3. LLM模型配置（各种支持的模型及其参数）

## 使用方法

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置API密钥：
   在`config.yaml`中配置各LLM服务的API密钥

3. 运行服务：
   ```
   python run.py
   ```

4. 访问系统：
   浏览器打开`http://127.0.0.1:5001`

## 函数调用

系统支持多种函数调用，包括：

- chat：私聊通信
- group_chat：群聊发言
- debate_reply：辩论回复
- died_reply：死亡回复
- vote：投票
- get_memory：获取记忆
- add_chat：添加好友
- add_group：加入群聊
- check_group：检查群聊状态
- check_chat：检查好友状态 