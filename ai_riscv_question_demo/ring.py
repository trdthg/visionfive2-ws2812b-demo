# -*- coding: utf-8 -*-
import time
from lib.pixelbuf import wheel
import random

# 配置参数
LED_COUNT = 24  # LED 数量
BRIGHTNESS = 0.8  # 亮度 (0-1)
SPEED = 1.0  # 全局速度系数

colors = {
    "red": (255, 0, 0),  # 红
    "green": (0, 255, 0),  # 绿
    "blue": (0, 0, 255),  # 蓝
    "lightblue": (173, 216, 230),
    "yellow": (255, 255, 0),  # 黄
    "qing": (0, 255, 255),  # 青
    "purple": (255, 0, 255),  # 紫
    "orange": (255, 165, 0),  # 橙
    "white": (255, 255, 255),  # 白
}


def clear(pixels):
    pixels.fill((0, 0, 0))  # 清空所有 LED


def color(pixels, check_exit, color, brightness=0.5):
    color = colors[color]
    pixels.fill((
                int(color[0] * brightness),
                int(color[1] * brightness),
                int(color[2] * brightness),
            ))
    pixels.show()
    time.sleep(0.05 / SPEED)

def rainbow(pixels, check_exit, cycle):
    # print("=== 彩虹波浪效果 ===")
    for i in range(LED_COUNT):
        # 计算每个 LED 的颜色偏移
        color_pos = int((i * 256 / LED_COUNT) + cycle * 10)
        pixels[i] = wheel(color_pos & 255)
        if check_exit():
            return
    pixels.show()
    time.sleep(0.05 / SPEED)


def load(pixels, check_exit):
    # print("=== 流星效果 ===")
    trail_length = random.randint(4, 8)
    for i in range(LED_COUNT + trail_length):
        pixels.fill((0, 0, 0))  # 清空所有 LED
        # 绘制流星主体
        for j in range(trail_length):
            pos = i - j
            if 0 <= pos < LED_COUNT:
                # 流星尾部渐暗效果
                brightness = 1.0 - (j / trail_length)
                pixels[pos] = (
                    int(255 * brightness),
                    int(100 * brightness),
                    int(50 * brightness),
                )
            if check_exit():
                return
        pixels.show()
        time.sleep(0.05 / SPEED)


def load2(pixels):
    # print("=== 色彩追逐效果 ===")
    for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]:
        for i in range(LED_COUNT * 2):
            pixels.fill((0, 0, 0))
            # 绘制 3 个追逐的点
            for j in range(3):
                pos = (i - j * (LED_COUNT // 3)) % LED_COUNT
                pixels[pos] = color
            pixels.show()
            time.sleep(0.05 / SPEED)


def breath(pixels, exit_check, color="lightblue", speed=0.5):
    """呼吸灯效果"""
    color = colors[color]
    for brightness in range(0, 101, 5):
        r = int(color[0] * brightness / 100)
        g = int(color[1] * brightness / 100)
        b = int(color[2] * brightness / 100)
        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(0.03 / speed)
        if exit_check():
            return
    for brightness in range(100, -1, -5):
        r = int(color[0] * brightness / 100)
        g = int(color[1] * brightness / 100)
        b = int(color[2] * brightness / 100)
        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(0.03 / speed)
        if exit_check():
            break


def heartbeat(pixels, check_exit, color="red"):
    # print("=== 心跳效果 ===")
    # 心跳膨胀
    for brightness in [x * 0.01 for x in range(20, 100, 5)]:
        pixels.fill(
            (
                int(colors[color][0] * brightness),
                int(colors[color][1] * brightness),
                int(colors[color][2] * brightness),
            )
        )
        pixels.show()
        time.sleep(0.01 / SPEED)
        if check_exit():
            return
    # 心跳收缩
    for brightness in [x * 0.01 for x in range(100, 20, -10)]:
        pixels.fill((int(255 * brightness), 0, 0))
        pixels.show()
        time.sleep(0.01 / SPEED)
        if check_exit():
            return


def boom(pixels):
    # print("=== 爆炸效果 ===")
    for center in [LED_COUNT // 4, LED_COUNT // 2, 3 * LED_COUNT // 4]:
        for radius in range(1, LED_COUNT // 2 + 1):
            pixels.fill((0, 0, 0))
            # 绘制爆炸波
            for i in range(LED_COUNT):
                distance = min(abs(i - center), LED_COUNT - abs(i - center))
                if distance <= radius:
                    # 爆炸波颜色从中心向外渐变
                    fade = 1.0 - (distance / radius)
                    pixels[i] = (int(255 * fade), int(150 * fade), 0)
            pixels.show()
            time.sleep(0.03 / SPEED)
