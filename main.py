##########################
# irrigation-controller - offline version
# by André Lange
#
##########################

from machine import Pin, I2C, Timer
import utime
import ssd1306
import micropython

i2c = I2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
onbled = Pin(2, Pin.OUT)  # onboard led (blue)
onbled.on()  # on

icon = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
]
oled.fill(0)  # Clear the display
for y, row in enumerate(icon):

    for x, c in enumerate(row):
        oled.pixel(x + 93, y + 23, c)

oled.text('IoT with ', 20, 25)
oled.text('Irrigation', 20, 40)
oled.show()

utime.sleep(2)  # 2s
onbled.off()  # off

#######################################################

v1_pin = Pin(15, Pin.OUT)
v1_pin.value(1)  # close
t_v1 = 720
text_v1 = "LINKS   zu"

v2_pin = Pin(4, Pin.OUT)
v2_pin.value(1)  # close
t_v2 = 720
text_v2 = "MITTE   zu"

v3_pin = Pin(5, Pin.OUT)
v3_pin.value(1)  # close
t_v3 = 720
text_v3 = "RECHTS  zu"

t_wait = 15
run = False
i = 0
t_next = 0
sel_i = 0
status = "stop"


def update_display(*args):
    global oled, run
    oled.fill(0)

    if not run:
        if sel_i == 1:
            oled.text("<", 120, 20)
        if sel_i == 2:
            oled.text("<", 120, 35)
        if sel_i == 3:
            oled.text("<", 120, 50)
    # update display
    oled.text(status, 0, 0)
    oled.text(str(t_next - i), 85, 0)
    oled.hline(0, 13, 127, 1)
    oled.text(text_v1, 0, 20)
    oled.text(str(t_v1), 85, 20)
    oled.text(text_v2, 0, 35)
    oled.text(str(t_v2), 85, 35)
    oled.text(text_v3, 0, 50)
    oled.text(str(t_v3), 85, 50)
    oled.show()


update_display()

#######################################################
# button RUN / STOP
timer_run = Timer(1)  # Register a new hardware timer.


def runstop(t):
    global run, status, i, t_next, sel_i, button

    if not button.value():
        run = not run
        print("run button", run)
        if run:
            status = "run"
        else:
            status = "stop"
            i = 0
            t_next = 0
            sel_i = 0
        micropython.schedule(update_display, 0)
    button.irq(handler=run_debounce)


def run_debounce(pin):
    global timer_run, button

    print("run - debounce")
    button.irq(handler=None)
    timer_run.init(mode=Timer.ONE_SHOT, period=100, callback=runstop)


button = Pin(16, Pin.IN, Pin.PULL_UP)  # run / stop
button.irq(trigger=Pin.IRQ_FALLING, handler=run_debounce)
#######################################################
# button SELECT
timer_sel = Timer(2)  # Register a new hardware timer.


def select(t):
    global sel_i, run, btn_sel

    if not btn_sel.value() and not run:
        print("sel button")
        sel_i = (sel_i + 1) % 4
        micropython.schedule(update_display, 0)
    btn_sel.irq(handler=sel_debounce)


def sel_debounce(pin):
    global btn_sel, timer_sel
    print("sel - debounce")
    btn_sel.irq(handler=None)
    timer_sel.init(mode=Timer.ONE_SHOT, period=100, callback=select)


btn_sel = Pin(17, Pin.IN, Pin.PULL_UP)
btn_sel.irq(trigger=Pin.IRQ_FALLING, handler=sel_debounce)
#######################################################
# button UP
timer_up = Timer(3)  # Register a new hardware timer.


def upvalue(t):
    global sel_i, t_v1, t_v2, t_v3, btn_up, run

    if not btn_up.value() and not run:
        print("up button")
        if sel_i == 1:
            t_v1 += 60
            if t_v1 == 1260:
                t_v1 = 300
        if sel_i == 2:
            t_v2 += 60
            if t_v2 == 1260:
                t_v2 = 300
        if sel_i == 3:
            t_v3 += 60
            if t_v3 == 1260:
                t_v3 = 300
        micropython.schedule(update_display, 0)
    btn_up.irq(handler=up_debounce)


def up_debounce(pin):
    global btn_up, timer_up

    print("up - debounce")
    btn_up.irq(handler=None)
    timer_up.init(mode=Timer.ONE_SHOT, period=100, callback=upvalue)


btn_up = Pin(19, Pin.IN, Pin.PULL_UP)
btn_up.irq(trigger=Pin.IRQ_FALLING, handler=up_debounce)
#######################################################

while True:
    utime.sleep_ms(990)  #
    micropython.schedule(update_display, 0)

    if run:
        sel_i = 0

        if i == 0:
            t_next = t_wait
        if i == (t_wait + 0):
            v1_pin.value(0)  # open
            text_v1 = "LINKS  auf"
            t_next = t_wait + t_v1
        if i == (t_wait + t_v1):
            v1_pin.value(1)  # close
            text_v1 = "LINKS   zu"
            t_next = (t_wait + t_v1 + t_wait)
        if i == (t_wait + t_v1 + t_wait):
            v2_pin.value(0)  # open
            text_v2 = "MITTE  auf"
            t_next = (t_wait + t_v1 + t_wait + t_v2)
        if i == (t_wait + t_v1 + t_wait + t_v2):
            v2_pin.value(1)  # close
            text_v2 = "MITTE   zu"
            t_next = (t_wait + t_v1 + t_wait + t_v2 + t_wait)
        if i == (t_wait + t_v1 + t_wait + t_v2 + t_wait):
            v3_pin.value(0)  # open
            text_v3 = "RECHTS auf"
            t_next = (t_wait + t_v1 + t_wait + t_v2 + t_wait + t_v3)
        if i == (t_wait + t_v1 + t_wait + t_v2 + t_wait + t_v3):
            v3_pin.value(1)  # close
            text_v3 = "RECHTS  zu"
            t_next = (t_wait + t_v1 + t_wait + t_v2 + t_wait + t_v3 + t_wait)

        i += 1

        if i == (t_wait + t_v1 + t_wait + t_v2 + t_wait + t_v3 + t_wait):
            run = False
            i = 0
            t_next = 0

    if not run:
        status = "stop"
        v1_pin.value(1)  # close
        v2_pin.value(1)  # close
        v3_pin.value(1)  # close
        text_v1 = "LINKS   zu"
        text_v2 = "MITTE   zu"
        text_v3 = "RECHTS  zu"
        i = 0
        t_next = 0
