# -*- coding: utf-8 -*-
import time
from lib import neopixel_spidev as np
import ring

# 配置参数
LED_COUNT = 24  # LED 数量
BRIGHTNESS = 0.8  # 亮度 (0-1)
SPEED = 1.0  # 全局速度系数

with np.NeoPixelSpiDev(
    1, 0, n=LED_COUNT, pixel_order=np.GRB, brightness=BRIGHTNESS
) as pixels:
    try:
        count = 0
        while True:
            count += 1
            time.sleep(1)
            ring.rainbow(pixels, count)
            ring.load(pixels)
            ring.load2(pixels)
            ring.boom(pixels)
            ring.heartbeat(pixels)

    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
