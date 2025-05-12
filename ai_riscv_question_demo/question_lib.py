# -*- coding: utf-8 -*-
# file: ~/projects/spi/ws2812b_test.py
import json
from enum import Enum
import requests


questions = []


def ask_ai(debug):
    global questions
    if len(questions) > 30:
        questions = []
    msgs = [
        {
            "role": "user",
            "content": """随机输出一个 RISC-V 小问题，有以下要求
1. 简单一点，适合对 RISC-V 仅仅有初步了解的用户
2. 只有两个选项
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
    "options": ["A: xxxxx", "B: xxxxx"],
    "answer": "A" # 或者 B,
    "more": "选择 A 是因为 XXX"
}
""",
        }
    ]
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
                                    "minItems": 2,
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
    api_key = vender_info["api_key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
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


def empty_cb(question_info, debug, acc, acc_next):
    pass


class State(Enum):
    INIT = 0
    YES = 1
    NO = 2
    WAIT = 3
    END = 4


def main_loop(cb=empty_cb, debug=False, check_exit=None):
    acc = {
        "excpt_count": 0,
        "excpt_acc_count": 0,
        "yes_count": 0,
        "yes_acc": 0,
        "no_count": 0,
        "no_acc": 0,
    }
    while True:
        if (check_exit and check_exit()) or acc["excpt_acc_count"] > 10:
            break
        try:
            # 出题前
            cb(None, State.INIT, acc)

            res = ask_ai(debug)
            # 出题后，等待用户回答
            cb(res, State.WAIT, acc)
            user_input = input("请输入答案：")

            # 回答后
            if user_input == res["answer"]:
                acc["yes_count"] += 1
                acc["yes_acc"] += 1
                acc["no_acc"] = 0
                cb(res, State.YES, acc)
            else:
                acc["no_count"] += 1
                acc["no_acc"] += 1
                acc["yes_acc"] = 0
                cb(res, State.NO, acc)

            # 结束
            cb(res, State.END, acc)
            acc["excpt_acc_count"] = 0
        except Exception as e:
            if debug:
                print(e)
            acc["excpt_count"] += 1
            acc["excpt_acc_count"] += 1
