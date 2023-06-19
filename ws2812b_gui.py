from tkinter import *
from tkinter import ttk
from tkinter import colorchooser

import time
from lib import neopixel_spidev as np
from lib.pixelbuf import wheel

# SPI devices: ls -al /dev/spidev*

window = Tk()

# Device
# You should use ls -l /dev/spi* to see which SPI device is available
# Assume your SPI device is /dev/spidevB.C
# Then you should set bus = B and chipselect = C
bus = 1
chipselect = 0
LEDCount = 24

# 全局
lightStatus = StringVar()
sentmsg = StringVar()
color = (255,255,255)
colorStatus = StringVar()
colormsg = StringVar()
brightness = 1.00
brightnessmsg = StringVar()

pixels = np.NeoPixelSpiDev(bus, chipselect, LEDCount, pixel_order=np.GRB)

# manual deinit()
pixels.fill(0)
pixels.show()

# ========== 硬件相关代码 ==========

def pickColor(*args):
    global color
    color_code = colorchooser.askcolor(title="Choose color")
    color = color_code[0]
    if lightStatus.get() == "switchon":
        pixels.fill(color)
        pixels.show()

def switchBrightness(*args):
    # 修改全局变量，这样可以记住灯的亮度
    global brightness
    brightnessmsg.set("Change Brightness: " + str(brightnessSlider.get()))
    brightness = brightnessSlider.get()
    pixels.brightness = brightness
    pixels.show()

def switchColor(*args):
    # 修改全局变量，这样可以记住灯的颜色
    global color
    colormsg.set("Change Color: " + colorStatus.get())
    if colorStatus.get() == "redlight":
        color = (255,0,0)
        pixels.fill(color)
        pixels.show()
    if colorStatus.get() == "greenlight":
        color = (0,255,0)
        pixels.fill(color)
        pixels.show()
    if colorStatus.get() == "yellowlight":
        color = (255,255,0)
        pixels.fill(color)
        pixels.show()
    if colorStatus.get() == "bluelight":
        color = (0,0,255)
        pixels.fill(color)
        pixels.show()
    if colorStatus.get() == "whitelight":
        color = (255,255,255)
        pixels.fill(color)
        pixels.show()

def switchOnOff(*args):
    sentmsg.set("Sent signal: " + lightStatus.get())
    if lightStatus.get() == "switchon":
        pixels.fill(color)
        pixels.show()
    if lightStatus.get() == "switchoff":
        pixels.fill(0)
        pixels.show()

# ========== 窗口相关代码 ==========

# Set title
window.title("WS2812B GUI")

# 上方空隙
frame1 = Frame(master=window, width=600, height=50)
frame1.pack(fill=BOTH, side=TOP, expand=True)

# 这里有三个选项
# 第一个控制灯的开关
frame2 = Frame(master=window, width=600, height=600)

maintext = Label(frame2, text="Turn the light on & off")
onswitch = Radiobutton(frame2, text="On", variable=lightStatus, value='switchon', command=switchOnOff)
offswitch = Radiobutton(frame2, text="Off", variable=lightStatus, value='switchoff', command=switchOnOff)
#send = ttk.Button(frame2, text='Send Signal', command=switchOnOff, default='active')
sentMsgDisplay = ttk.Label(frame2, textvariable=sentmsg, anchor='center')

# 第二个控制灯的颜色
colortext = Label(frame2, text="Change the color of the light")
# redswitch = Radiobutton(frame2, text="Red", variable=colorStatus, value='redlight')
# greenswitch = Radiobutton(frame2, text="Green", variable=colorStatus, value='greenlight')
# yellowswitch = Radiobutton(frame2, text="Yellow", variable=colorStatus, value='yellowlight')
# blueswitch = Radiobutton(frame2, text="Blue", variable=colorStatus, value='bluelight')
# whiteswitch = Radiobutton(frame2, text="White", variable=colorStatus, value='whitelight')
# sendcolor = ttk.Button(frame2, text='Change Color', command=switchColor)
# sentColorMsgDisplay = ttk.Label(frame2, textvariable=colormsg, anchor='center')
colorPickerButton = Button(frame2, text="Color Picker", command=pickColor)

# 第三个控制灯的亮度
brightnesstext = Label(frame2, text="Change the brightness of the light")
brightnessSlider = Scale(frame2, from_=0, to=1, resolution=0.01, orient=HORIZONTAL)
#sendbrightness = ttk.Button(frame2, text='Change Brightness', command=switchBrightness)
sentBrightnessMsgDisplay = ttk.Label(frame2, textvariable=brightnessmsg, anchor='center')

# 然后我们对其进行布局
# 第一个控制灯的开关
maintext.grid(column=1, row=0)
onswitch.grid(column=1, row=1,sticky=W)
offswitch.grid(column=1,row=2,sticky=W)
# Default selection
offswitch.invoke()
#send.grid(column=1, row=3, sticky=S)
sentMsgDisplay.grid(column=1, row=3, sticky=N)

# # 第二个控制灯的颜色
colortext.grid(column=2, row=0)
# redswitch.grid(column=2, row=1,sticky=W)
# greenswitch.grid(column=2, row=2,sticky=W)
# yellowswitch.grid(column=2, row=3,sticky=W)
# blueswitch.grid(column=2, row=4,sticky=W)
# whiteswitch.grid(column=2, row=5,sticky=W)
# # Default selection
# whiteswitch.invoke()
# sendcolor.grid(column=2, row=6, sticky=S)
# sentColorMsgDisplay.grid(column=2, row=7, sticky=N)
# 用酷炫新方法
colorPickerButton.grid(column=2, row=1)

# 第三个控制灯的亮度
brightnesstext.grid(column=3, row=0)
brightnessSlider.grid(column=3, row=1)
# 将 Scale 组件的值设置为 1
brightnessSlider.set(1)
#sendbrightness.grid(column=3, row=2, sticky=S)
sentBrightnessMsgDisplay.grid(column=3, row=3, sticky=N)

# 将 switchBrightness 函数绑定到 Scale 组件的值变化事件上
brightnessSlider.bind("<ButtonRelease-1>", switchBrightness)

frame2.pack(anchor='center')

# 下方空隙
frame3 = Frame(master=window, width=600, height=50)
frame3.pack(fill=BOTH, side=TOP, expand=True)

window.mainloop()
