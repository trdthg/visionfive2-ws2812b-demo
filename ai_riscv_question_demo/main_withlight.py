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


def ring_control():
    global pixels
    global state
    count = 0
    while True:
        count += 1
        if state == question_lib.State.INIT:
            ring.load(pixels)
        if state == question_lib.State.WAIT:
            ring.heartbeat(pixels, "yellow")
        elif state == question_lib.State.YES:
            if acc["yes_acc"] >= 3:
                ring.rainbow(pixels, count)
            else:
                ring.color(pixels, "green")
        elif state == question_lib.State.NO:
            ring.color(pixels, "red")
        elif state == question_lib.State.END:
            ring.color(pixels, "white")
            pass


def cb(new_question_info, new_state, new_acc):
    global pixels
    global state
    state = new_state
    global question_info
    question_info = new_question_info
    global acc
    acc = new_acc

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
        time.sleep(1)


t1 = threading.Thread(target=ring_control, args=())
t1.start()

question_lib.main_loop(cb=cb)
