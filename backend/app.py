from flask import Flask, jsonify, request, make_response, g
from flask_cors import CORS
from lib import neopixel_spidev as np


# Run something after app starts
def deinit_light():
    np.NeoPixelSpiDev(bus, chipselect, LEDCount, pixel_order=np.GRB).deinit()


class Flask(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug:
            with self.app_context():
                deinit_light()
        super(Flask, self).run(
            host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options
        )


app = Flask(__name__)
CORS(app)

# Device
# You should use ls -l /dev/spi* to see which SPI device is available
# Assume your SPI device is /dev/spidevB.C
# Then you should set bus = B and chipselect = C
bus = 1
chipselect = 0
LEDCount = 24

# 初始化灯光
# pixels = np.NeoPixelSpiDev(bus, chipselect, LEDCount, pixel_order=np.GRB)
pixels = None
pixels_is_init = False

# 灯光状态，默认为关闭
light_status = False

# 灯光亮度，默认为最大亮度
light_brightness = 1.0

# 灯光颜色
light_color = (255, 255, 255)


def light_control(status, brightness, color):
    global light_status
    global light_brightness
    global light_color
    global pixels_is_init
    global pixels

    if pixels_is_init is False:
        pixels = np.NeoPixelSpiDev(bus, chipselect, LEDCount, pixel_order=np.GRB)
        pixels_is_init = True

    light_status = status
    light_brightness = brightness
    light_color = color
    if status:
        pixels.fill(color)
    else:
        pixels.fill(0)
    pixels.brightness = brightness
    pixels.show()


# 获取灯光状态
@app.route("/lightstatus", methods=["GET"])
def get_light_status():
    status = light_status
    response = make_response(jsonify({"status": status}), 200)
    return response


# 控制灯光开关
# /setlight?switch=on
@app.route("/setlight", methods=["POST"])
def set_light():
    global light_status
    switch = request.args.get("switch")
    if switch == "on":
        if not light_status:
            # 打开灯光
            light_status = True
            light_control(light_status, light_brightness, light_color)
            return make_response(jsonify({"result": "success", "status": "on"}), 200)
        else:
            # 灯光已经是开启状态
            return make_response(jsonify({"result": "failed", "status": "on"}), 400)
    if switch == "off":
        if light_status:
            # 关闭灯光
            light_status = False
            light_control(light_status, light_brightness, light_color)
            return make_response(jsonify({"result": "success", "status": "off"}), 200)
        else:
            # 灯光已经是关闭状态
            return make_response(jsonify({"result": "failed", "status": "off"}), 400)
    else:
        # 参数错误
        return make_response(
            jsonify({"result": "error", "message": "Invalid parameter"}), 400
        )


# 控制灯光颜色
# /setcolor?value=006eff
@app.route("/setcolor", methods=["POST"])
def set_color():
    value = request.args.get("value")
    rgb = tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    try:
        if len(rgb) != 3:
            raise ValueError
    except ValueError:
        return make_response(
            jsonify({"result": "error", "message": "Invalid value"}), 400
        )
    light_color = rgb
    light_control(light_status, light_brightness, light_color)
    return make_response(
        jsonify(
            {
                "result": "success",
                "color": str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]),
            }
        ),
        200,
    )


# 控制灯光亮度
# /setbrightness?value=0.75
@app.route("/setbrightness", methods=["POST"])
def set_brightness():
    value = request.args.get("value")
    try:
        value = float(value)
        if value < 0 or value > 1:
            raise ValueError
    except ValueError:
        return make_response(
            jsonify({"result": "error", "message": "Invalid value"}), 400
        )
    light_brightness = value
    light_control(light_status, light_brightness, light_color)
    return make_response(
        jsonify({"result": "success", "brightness": light_brightness}), 200
    )


if __name__ == "__main__":
    app.run()
