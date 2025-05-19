# -*- coding: utf-8 -*-
# file: ~/projects/spi/ws2812b_test.py
from enum import Enum
import ai

def empty_cb(question_info, debug, acc, acc_next):
    pass


class State(Enum):
    load = 0
    yes = 1
    no = 2
    wait = 3
    sleep = 4


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
            cb(None, State.load, acc)

            res = ai.gen_rv_question(debug)
            # 出题后，等待用户回答
            cb(res, State.wait, acc)
            user_input = input("请输入答案：")

            # 回答后
            if user_input == res["answer"]:
                acc["yes_count"] += 1
                acc["yes_acc"] += 1
                acc["no_acc"] = 0
                cb(res, State.yes, acc)
            else:
                acc["no_count"] += 1
                acc["no_acc"] += 1
                acc["yes_acc"] = 0
                cb(res, State.no, acc)

            # 结束
            cb(res, State.sleep, acc)
            acc["excpt_acc_count"] = 0
        except Exception as e:
            if debug:
                print(e)
            acc["excpt_count"] += 1
            acc["excpt_acc_count"] += 1
