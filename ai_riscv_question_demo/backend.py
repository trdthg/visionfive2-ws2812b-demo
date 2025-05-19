from enum import Enum
import threading
import sys
import ai
import ring
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# 全局状态

class State(Enum):
    loading = 0
    yes = 1
    no = 2
    wait = 3
    sleep = 4
    rainbow = 5


light_state = State.sleep
notice_flag = False
check_exit = False


def check_notice():
    """检查是否需要切换灯效"""
    global check_exit, notice_flag
    if check_exit:
        return True
    if notice_flag:
        notice_flag = False
        return True
    return False


def ring_control():
    pixels = None
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        print("灯光禁用")
        return
    import lib.neopixel_spidev as np
    with np.NeoPixelSpiDev(1, 0, n=24, pixel_order=np.GRB) as pixels:
        global light_state, notice_flag
        """LED 控制线程"""
        count = 0
        while True:
            if check_exit:
                ring.clear(pixels)
                break
            count += 1
            if light_state == State.loading:
                ring.load(pixels, check_notice)
            elif light_state == State.sleep:
                ring.color(pixels, check_notice, "white", 0.6)
            elif light_state == State.wait:
                ring.breath(pixels, check_notice, "blue")
            elif light_state == State.yes:
                ring.color(pixels, check_notice, "green")
            elif light_state == State.no:
                ring.color(pixels, check_notice, "red")
            elif light_state == State.rainbow:
                ring.rainbow(pixels, check_notice, count)
            notice_flag = False
        ring.clear(pixels)


# API 路由
@app.post("/api/question/start")
def start_question():
    """开始新的问答"""
    try:
        res = ai.gen_rv_question(debug=False)
        return jsonify({"status": "success", "data": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 灯效控制路由
@app.post("/api/light/change/<new_state>")
def light_change(new_state: str):
    global light_state, notice_flag
    light_state = State[new_state]
    notice_flag = True
    return jsonify({"status": "success"})

@app.post("/api/summary")
def ai_summary():
    summary = request.json.get("summary")
    return jsonify({"status": "success", "summary": ai.gen_rv_summary(summary)})

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


def start_server():
    """启动服务器"""
    global check_exit
    try:
        led_thread = threading.Thread(target=ring_control)
        led_thread.start()
        app.run(host="0.0.0.0", port=5001)
    except KeyboardInterrupt:
        check_exit = True
        led_thread.join()


if __name__ == "__main__":
    start_server()
