from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import question_lib
import ring
import lib.neopixel_spidev as np
from lib.pixelbuf import wheel

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# 添加根路由，返回前端页面
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# 全局状态
pixels = np.NeoPixelSpiDev(1, 0, n=24, pixel_order=np.GRB)
state = question_lib.State.INIT
question_info = {}
acc = {
    "excpt_count": 0,
    "excpt_acc_count": 0,
    "yes_count": 0,
    "yes_acc": 0,
    "no_count": 0,
    "no_acc": 0,
}
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
            if acc["yes_acc"] >= 3:
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
    global state, question_info
    try:
        res = question_lib.ask_ai(debug=False)
        state = question_lib.State.WAIT
        question_info = res
        return jsonify({
            'status': 'success',
            'data': {
                'question': res['question'],
                'options': res['options']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/question/answer', methods=['POST'])
def submit_answer():
    """提交答案"""
    global state, acc, notice_flag
    try:
        data = request.get_json()
        user_answer = data.get('answer')
        
        if not question_info:
            return jsonify({
                'status': 'error',
                'message': '请先开始问答'
            }), 400
            
        if user_answer == question_info['answer']:
            acc['yes_count'] += 1
            acc['yes_acc'] += 1
            acc['no_acc'] = 0
            state = question_lib.State.YES
        else:
            acc['no_count'] += 1
            acc['no_acc'] += 1
            acc['yes_acc'] = 0
            state = question_lib.State.NO
            
        notice_flag = True
        
        return jsonify({
            'status': 'success',
            'data': {
                'correct': user_answer == question_info['answer'],
                'explanation': question_info['more'],
                'score': acc
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/question/next', methods=['POST'])
def next_question():
    """进入下一题"""
    global state, notice_flag
    try:
        state = question_lib.State.END
        notice_flag = True
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    return jsonify({
        'status': 'success',
        'data': {
            'state': state.name,
            'score': acc
        }
    })

def start_server():
    """启动服务器"""
    global check_exit
    try:
        # 启动 LED 控制线程
        led_thread = threading.Thread(target=ring_control)
        led_thread.daemon = True
        led_thread.start()
        
        # 启动 Flask 服务
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        check_exit = True
        led_thread.join()
    finally:
        pixels.fill((0, 0, 0))
        pixels.show()

# 添加根路由，返回前端页面
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    start_server()