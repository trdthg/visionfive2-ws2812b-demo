import question_lib


def cb(question_info, state, acc):
    if state == question_lib.State.INIT:
        print("*" * 50)
        print("出题中.....")
    if state == question_lib.State.WAIT:
        print(question_info["question"])
        for option in question_info["options"]:
            print(option)
    elif state == question_lib.State.YES:
        print("结果：正确")
    elif state == question_lib.State.NO:
        print("结果：错误")
    elif state == question_lib.State.END:
        print("答案分析：" + question_info["more"])
        print("得分：", acc)


question_lib.main_loop(cb=cb, debug=True)
