import json


import requests

vender = {
    "siliconflow": {
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "api_key": "sk-inxddldqxbduuhoofjnxdtkbmeiufbspdcaypwsyatuhovsw",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "extend_data": {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "math_response",
                    "schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "title": "math_response",
                        "description": "A schema for math questions with multiple choices",
                        "type": "object",
                        "properties": {
                            "question": {
                                "description": "The math question text",
                                "type": "string",
                            },
                            "options": {
                                "description": "Array of answer options with labels",
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "pattern": "^[A-Z]: .+$",
                                },
                                "minItems": 4,
                                "uniqueItems": True,
                            },
                            "answer": {
                                "description": "The correct answer label",
                                "type": "string",
                                "pattern": "^[A-Z]$",
                            },
                            "more": {
                                "description": "Explanation for the correct answer",
                                "type": "string",
                            },
                        },
                        "required": ["question", "options", "answer", "more"],
                        "additionalProperties": False,
                    },
                },
            },
        },
        # "model": "Qwen/QwQ-32B",
        "response_key": "content",
    },
    "ali": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key": "sk-0e30fec1f64a475db175f6864c15ff5c",
        # "model": "deepseek-r1-distill-qwen-7b",
        "model": "qwen-max-latest",
        "extend_data": {"response_format": {"type": "json_object"}},
        # "response_key": "reasoning_content",
        "response_key": "content",
    },
}
vender_info = vender["ali"]
api_key = vender_info["api_key"]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

questions = []

def gen_rv_summary(summary):
    msgs = [
        {
            "role": "user",
            "content": """下面是用户的 RISC-V 小问题答题记录，请总结用户的答题结果，并给出学习建议
            - 以纯文本形式返回，禁止使用 markdown
            - 分段回答
            """
            + str(summary)
        }
    ]
    payload = {
        "model": vender_info["model"],
        # "model": "Qwen/QwQ-32B",
        "stream": False,
        "max_tokens": 512,
        # "enable_thinking": False,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": msgs,
    }
    response = requests.post(vender_info["url"], json=payload, headers=headers)
    response_data = response.json()
    answer = response_data["choices"][0]["message"][vender_info["response_key"]].strip()
    return answer


def gen_rv_question(debug):
    global questions
    if len(questions) > 30:
        questions = []
    msgs = [
        {
            "role": "user",
            "content": """随机输出一个 RISC-V 小问题，有以下要求
1. 简单一点，适合对 RISC-V 仅仅有初步了解的用户
2. 只有 4 个选项
3. 给出对应的答案
4. 给出背后的知识，需要通俗易懂
5. 问题可以涉及到具体的指令，扩展，体系结构等所有内容
6. 不要说多余的话
7. 问题不要和下面这些重复："""
            + str(questions)
            + """

请按照 json 格式输出：

{
    "question": "",
    "options": ["A: xxxxx", "B: xxxxx", ... ],
    "answer": "A" # 只保留第一个字母，
    "more": "选择 A 是因为 XXX"
}
""",
        }
    ]
    payload = {
        "model": vender_info["model"],
        # "model": "Qwen/QwQ-32B",
        "stream": False,
        "max_tokens": 512,
        # "enable_thinking": False,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": msgs,
        **vender_info["extend_data"],
    }
    response = requests.post(vender_info["url"], json=payload, headers=headers)
    response_data = response.json()
    if debug:
        print("*" * 50)
        print(response_data)
        print("*" * 50)
    answer = response_data["choices"][0]["message"][vender_info["response_key"]].strip()
    res = json.loads(answer)
    questions.append(res["question"])
    return res
