# 步骤1：配置环境变量
安装依赖
`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tavily-python openai`

# 配置环境变量
export TAVILY_API_KEY=xxxx
export OPENAI_API_KEY=xxxx
export OPENAI_BASE_URL=https://aihubmix.com/v1
export MODEL_NAME=coding-glm-4.7-free

# 步骤2：运行测试
`python FirstAgentTest.py`

报错
```python
Traceback (most recent call last):
  File ".\code\chapter1\FirstAgentTest.py", line 62, in <module>
    from tavily import TavilyClient
ImportError: cannot import name 'TavilyClient' from 'tavily' (D:\softwares\setup\Anaconda3\lib\site-packages\tavily\__init__.py)
```

修复：
tavily版本问题
```python
try:
    from tavily import TavilyClient
except ImportError:
    from tavily import Client as TavilyClient
```

报错
```python
Traceback (most recent call last):
  File ".\code\chapter1\FirstAgentTest.py", line 195, in <module>
    final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
AttributeError: 'NoneType' object has no attribute 'group'
```

修复：
在FirstAgentTest.py中，添加判断action_str是否为空的逻辑。
```python
        if not action_str:
            return "错误：未生成有效操作"
```

# 步骤3：运行测试
`python FirstAgentTest.py`
结果
```python
用户输入: 你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。
========================================
--- 循环 1 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 用户需要查询北京的天气，然后根据天气推荐旅游景点。首先我需要调用 get_weather 工具获取北京的实时天气信息。
Action: get_weather(city="北京")

Observation: 北京当前天气：Sunny，气温11摄氏度
========================================
--- 循环 2 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:


Observation: 错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。
========================================
--- 循环 3 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 我已经获取到北京的天气是晴天，气温11摄氏度。现在我需要使用这个天气信息来查询北京推荐的旅游景点。
Action: get_attraction(city="北京", weather="Sunny")

Observation: On sunny days in Beijing, visit the Temple of Heaven, the Forbidden City, and the Summer Palace for pleasant weather and rich history.
========================================
--- 循环 4 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 我已经获取了北京的天气信息（晴天，11摄氏度）以及根据晴天天气推荐的旅游景点（天坛、故宫和颐和园）。现在我可以将这两个信息结合起来给用户一个完整的回答。

Action: Finish[北京今天天气晴朗，气温11摄氏度。根据这个好天气，我为您推荐以下旅游景点：天坛、故宫和颐和园。这些景点在晴朗的天气下游览非常舒适，而且拥有丰富的历史文化底蕴，非常适合今天的出行。]

任务完成，最终答案: 北京今天天气晴朗，气温11摄氏度。根据这个好天气，我为您推荐以下旅游景点：天坛、故宫和颐和园。这些景点在晴朗的天气下游览非常舒适，而且拥有丰富的历史文化底蕴，非常适合 今天的出行。
```

# 结论
本项目是一个最小版 ReAct Agent 脚本：LLM 负责“Thought/Action”决策，Python 负责执行工具并把 Observation 反馈回去，直到 Finish[...] 结束，入口就是文件底部的主循环。当前存在的问题：generate 出错时返回普通错误文本，主循环仍当作模型输出继续解析，可能反复“无 Action”空转。这也说明了agent的上限很大程度上取决于LLM的能力。
