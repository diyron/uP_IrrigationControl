
import tinyweb
import network
import time
from machine import Pin, I2C, Timer
from sh1106 import SH1106_I2C

i2c = I2C(scl=Pin(22), sda=Pin(21))
oled = SH1106_I2C(128, 64, i2c)
onbled = Pin(2, Pin.OUT)  # onboard led (blue)
onbled.on()  # on

oled.fill(0)  # Clear the display
oled.text('REST Test ', 20, 25)
oled.text('Irrigation', 20, 40)
oled.show()

#######################################################
wlan = None
SSID = "Cookie"
PASSWORD = "An35fP89htDw"

class RestControl:

    t_li = 0
    t_mi = 0
    t_re = 0
    t_st = 0
    run = False
    s = 0
    tick_timer = Timer(0)

    valve_li = Pin(25, Pin.OUT)
    valve_mi = Pin(26, Pin.OUT)
    valve_re = Pin(27, Pin.OUT)
    valve_st = Pin(14, Pin.OUT)

    def stop(self):
        self.valve_li.value(0)
        self.valve_mi.value(0)
        self.valve_re.value(0)
        self.valve_st.value(0)
        self.tick_timer.deinit()
        self.s = 0
        self.run = False

        oled.fill(0)  # Clear the display
        oled.text("stop", 20, 25)
        oled.show()


    def start(self ,range):
        print("sek ", str(self.s))
        print("range", range)
        self.run = True
        tmp = ""

        oled.fill(0)  # Clear the display
        oled.text(str(self.s), 20, 25)
        oled.text(range, 20, 35)

        if self.s == 0:
            if range == "bed":
                self.valve_st(1)
                tmp = "ST"
            else:
                self.valve_li(1)
                tmp = "LI"

        if self.s == self.t_li:
            if range == "bed":
                self.stop()
            else:
                self.valve_li(0)
                self.valve_mi(1)
                tmp = "MI"

        if self.s == self.t_li + self.t_mi:
            self.valve_mi(0)
            self.valve_re(1)

            tmp = "RE"

        if self.s == self.t_li + self.t_mi + self.t_re:
            if range == "all":
                self.valve_re(0)
                self.valve_st(1)
                tmp = "ST"
            else:
                self.stop()

        if self.s == self.t_li + self.t_mi + self.t_re + self.t_st:
            self.stop()

        oled.text(tmp, 20, 45)
        oled.show()

        self.s += 1

    def get(self, data):
        print('get: ', data)

        if onbled.value() == 1:
            onbled.off()

            tmp = "off"
        else:
            onbled.on()
            tmp = "on"

        oled.fill(0)  # Clear the display
        oled.text(tmp, 20, 25)
        oled.show()

        if "t_li" in data:
            self.t_li = int(data["t_li"])

        if "t_mi" in data:
            self.t_mi = int(data["t_mi"])

        if "t_re" in data:
            self.t_re = int(data["t_re"])

        if "t_st" in data:
            self.t_st = int(data["t_st"])

        if "seq" in data:
            if data["seq"] == "stop":
                self.stop()

            if (data["seq"] == "all" or data["seq"] == "bed" or data["seq"] == "green") and not self.run:
                self.tick_timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.start(data["seq"]))

        print("t_li", self.t_li)
        print("t_mi", self.t_mi)
        print("t_re", self.t_re)
        print("t_st", self.t_st)

        return {'message': "get_success"}


######################################################################


def rest_server_start():
    # Create web server application
    app = tinyweb.webserver()
    # Add our resources
    app.add_resource(RestControl, '/irrigation')
    app.run(host='0.0.0.0', port=8081)


def connect_wifi(ssid, passwd):
    global wlan
    wlan = network.WLAN(network.STA_IF)  # create a wlan object
    wlan.active(True)  # Activate the network interface
    wlan.disconnect()  # Disconnect the last connected WiFi
    wlan.connect(ssid, passwd)  # connect wifi
    while wlan.ifconfig()[0] == '0.0.0.0':
        time.sleep(1)


print("conneting to wifi...")

try:
    connect_wifi(SSID, PASSWORD)
    onbled.off()
    print("ready")
    print("starting REST-Webserver...")
    rest_server_start()

except Exception as e:
    print(e)
    wlan.disconnect()
    wlan.active(False)


