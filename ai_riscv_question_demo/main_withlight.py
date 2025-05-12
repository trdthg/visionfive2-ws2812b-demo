# -*- coding: utf-8 -*-
import signal
import threading
import question_lib
import time
import ring

import lib.neopixel_spidev as np
from lib.pixelbuf import wheel

pixels = np.NeoPixelSpiDev(1, 0, n=24, pixel_order=np.GRB)

state = question_lib.State.INIT
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
        if state == question_lib.State.INIT:
            ring.load(pixels, check_notice)
        if state == question_lib.State.WAIT:
            ring.breath(pixels, check_notice, "yellow")
        elif state == question_lib.State.YES:
            if acc["yes_acc"] >= 3:
                ring.rainbow(pixels, check_notice, count)
                acc["yes_acc"] = 0
            else:
                ring.breath(pixels, check_notice, "green")
        elif state == question_lib.State.NO:
            ring.color(pixels, check_notice, "red")
        elif state == question_lib.State.END:
            ring.color(pixels, check_notice, "white")
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

    if state == question_lib.State.INIT:
        print("出题中.....")
    if state == question_lib.State.WAIT:
        print(question_info["question"])
        for option in question_info["options"]:
            print(option)
    elif state == question_lib.State.YES:
        print("结果：正确")
        time.sleep(1)
        if acc["yes_acc"] >= 3:
            input("按回车继续")
    elif state == question_lib.State.NO:
        print("结果：错误")
        time.sleep(1)
    elif state == question_lib.State.END:
        print("答案分析：" + question_info["more"])
        input("按回车继续")


if __name__ == "__main__":
    t1 = threading.Thread(target=ring_control, args=())

    def signal_handler():
        global t1
        global check_exit
        check_exit = True
        t1.join()
        exit(0)

    t1.start()
    signal.signal(signal.SIGINT, signal_handler)
    question_lib.main_loop(cb=cb)
