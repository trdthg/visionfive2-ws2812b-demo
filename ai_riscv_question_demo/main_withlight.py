# -*- coding: utf-8 -*-
import os
import signal
import threading
import question_lib
import ring

import lib.neopixel_spidev as np

pixels = np.NeoPixelSpiDev(1, 0, n=24, pixel_order=np.GRB)

state = question_lib.State.load
question_info = {}
acc = {}

check_exit = False

notice_flag = False


def check_notice():
    global check_exit
    if check_exit:
        return True
    global notice_flag
    if notice_flag:
        notice_flag = False
        return True
    return False


def ring_control():
    global pixels
    global state
    global notice_flag
    count = 0
    while True:
        if check_exit:
            ring.clear(pixels)
            break
        count += 1
        if state == question_lib.State.load:
            ring.load(pixels, check_notice)
        if state == question_lib.State.wait:
            ring.breath(pixels, check_notice, "yellow")
        elif state == question_lib.State.yes:
            if acc["yes_acc"] >= 3:
                ring.rainbow(pixels, check_notice, count)
            else:
                ring.breath(pixels, check_notice, "green")
        elif state == question_lib.State.no:
            ring.color(pixels, check_notice, "red")
        elif state == question_lib.State.sleep:
            ring.color(pixels, check_notice, "white", 0.6)
        notice_flag = False


def cb(new_question_info, new_state, new_acc):
    global pixels
    # 状态改变
    global state
    state = new_state
    global question_info
    question_info = new_question_info
    global acc
    acc = new_acc

    # 灯停止当前任务
    global notice_flag
    notice_flag = True

    if state == question_lib.State.load:
        print("出题中.....")
    if state == question_lib.State.wait:
        print(question_info["question"])
        for option in question_info["options"]:
            print(option)
    elif state == question_lib.State.yes:
        print("结果：正确")
        input("按回车继续")
        if acc["yes_acc"] >= 3:
            acc["yes_acc"] = 0
    elif state == question_lib.State.no:
        print("结果：错误")
        input("按回车查看答案解析")
    elif state == question_lib.State.sleep:
        print("答案分析：" + question_info["more"])
        input("按回车继续")


if __name__ == "__main__":
    t1 = threading.Thread(target=ring_control, args=())
    t2 = threading.Thread(
        target=question_lib.main_loop, kwargs={"cb": cb, "check_exit": check_notice}
    )

    def signal_handler(signum, frame):
        global t1
        global check_exit
        check_exit = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    t1.start()
    t2.start()

    t1.join()
    os._exit(0)
