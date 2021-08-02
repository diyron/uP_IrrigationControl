# uP_IrrigationControl

ESP32 and MicroPython based irrigation controller

### features

- REST-Webserver on ESP32 (based on TinyWeb https://github.com/belyalov/tinyweb)
- control of 4 valves (by eg. 4 relais switching electic valves)

### current limitations

- no SSL/TLS support (use this code only for testing or in otherwise secured networks)

### example

- GET http://HOST:8081/irrigation?t_li=10&t_mi=10&t_re=10&t_st=10&seq=green

