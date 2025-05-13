from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import question_lib
import ring
import lib.neopixel_spidev as np

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# 全局状态
pixels = np.NeoPixelSpiDev(1, 0, n=24, pixel_order=np.GRB)
state = question_lib.State.INIT
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
    """LED 控制线程"""
    global pixels, state, notice_flag
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
            if request.get_json().get('combo', 0) >= 3:
                ring.rainbow(pixels, check_notice, count)
            else:
                ring.breath(pixels, check_notice, "green")
        elif state == question_lib.State.NO:
            ring.color(pixels, check_notice, "red")
        elif state == question_lib.State.END:
            ring.color(pixels, check_notice, "white", 0.6)
        notice_flag = False

# API 路由
@app.route('/api/question/start', methods=['POST'])
def start_question():
    """开始新的问答"""
    try:
        res = question_lib.ask_ai(debug=False)
        return jsonify({
            'status': 'success',
            'data': res
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 灯效控制路由
@app.route('/api/light/init', methods=['POST'])
def light_init():
    global state, notice_flag
    state = question_lib.State.INIT
    notice_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/light/wait', methods=['POST'])
def light_wait():
    global state, notice_flag
    state = question_lib.State.WAIT
    notice_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/light/correct', methods=['POST'])
def light_correct():
    global state, notice_flag
    state = question_lib.State.YES
    notice_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/light/wrong', methods=['POST'])
def light_wrong():
    global state, notice_flag
    state = question_lib.State.NO
    notice_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/light/end', methods=['POST'])
def light_end():
    global state, notice_flag
    state = question_lib.State.END
    notice_flag = True
    return jsonify({'status': 'success'})

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

def start_server():
    """启动服务器"""
    global check_exit
    try:
        led_thread = threading.Thread(target=ring_control)
        led_thread.daemon = True
        led_thread.start()
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        check_exit = True
        led_thread.join()
    finally:
        pixels.fill((0, 0, 0))
        pixels.show()

if __name__ == '__main__':
    start_server()