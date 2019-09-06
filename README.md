# MicroPython ESP8266/ESP32 Driver for TEA5767 FM Radio Module

![FQTC302J70QTXEA MEDIUM](https://user-images.githubusercontent.com/44191076/64347645-d7d66f00-d026-11e9-87b5-4ae21e6115e9.jpg)

[TEA5767 modules](https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf) are one of the cheaper FM radio receiver modules, which allow you to build DIY FM radios real quick.

This is the driver for MicroPython on ESP8266/ESP32 boards. I've tested it on my NodeMCU V2, WeMos D1 mini (ESP8266s running firmware esp8266-20190529-v1.11) and BPI:bit (ESP32 running esp32-20190906-v1.11).

## Wiring

* +5V -> power (both 3.3V and 5V works)
* SDA -> SDA
* SLC -> SCL
* GND -> GND

## Import on ESP8266

The simplest way is as below:

```python
import TEA5767

radio = TEA5767.Radio(freq=99.7)
```

The module would immediately tune to the frequency. If you did not specify a frequency here, the TEA5767 would not do anything.

There are also some other options:

```python
radio = TEA5767.Radio(freq=99.7, scl=5, sda=4, addr=0x60, debug=True, band="US", 
                      stereo=True, soft_mute=True, noise_cancel=True, high_cut=True)
```

* freq = FM frequency
* scl = SCL pin (default 5 of ESP8266 boards)
* sda = SDA pin (default 4 of ESP8266 boards)
* addr = I2C address (default 0x60)
* debug = output some info text via REPL/serial port window whenever you read data from the module. Default False.
* band = band limits; "US" (default) = US/Europe band (87.5-108 MHz), "JP" = Japan band (76-91 MHz)
* stereo = stereo mode (default True; set as False = forced mono)
* soft_mute = soft mute (default True)
* noise_cancel = stereo noise cancelling (default True)
* high_cut = high cut control (default True)

## Import on ESP32

It's basic the same as ESP8266, however you'll have to specify the SCL and SDA pins as 22 and 21:

```python
radio = TEA5767.Radio(freq=99.7, scl=22, sda=21)
```
## Set/change frequency

Directly tuning to a specific frequency:

```python
radio.set_frequency(freq=104.9)
```

The TEA5767 would tune to the new frequency immediately.

Or you can change the frequency bit by bit, like turning a knob on radios:

```python
radio.change_freqency(change=0.1)
radio.change_freqency(change=-0.1)
```

## Search mode

You can set the TEA5756 to auto-select a possible working station near a specific frequency:

```python
radio.search(True)
radio.search(mode=True, dir=1, adc=5)
radio.search(mode=True, freq=90.0)
```

When the search mode is on (True), the actual frequency may change after you selected the frequency. It may take a little while, so remember to use radio.read() (see below) to update frequency info.

* dir = search direction; 1 means go up (default), 0 means go down on frequency.
* adc = signal ADC resolution, default 5. The adc level can be set as 0 (no search), 5, 7 or 10.
* freq = set a new frequency and search from there

And if you change frequency by using radio.change_freqency(), the search direction will be set to the same direction of frequency change.

Turn the search mode off is simply

```python
radio.search(False)
```

## Mute/standby

```python
radio.mute(True)
radio.standby(True)
```

Mute is simply turning off the sound output. If you want to save more power, use radio.standby().

The TEA5767 also allows you to turn off right or left speaker, however I did not implement these functions.

## Read data

You can retrieve some info from the TEA5767:

```python
radio.read()
```

If the debug option in initialization is set to True, you'll see some output text in REPL/serial port window:

```
FM frequency: 99.7 MHz
In search mode: False
Station ready: True
Station has stereo: True
Signal ADC level: 10
```

You can also read these info via

```python
my_variable = radio.frequency
my_variable = radio.search_mode
my_variable = radio.is_ready
my_variable = radio.is_stereo
my_variable = radio.signal_adc_level
```

## A simplified version

If you just want to tune the frequency of TEA5767, you can use code as short as below (simply paste it into your script):

```python
from machine import Pin, I2C

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

def radio_frequency(freq):
    freqB = 4 * (freq * 1000000 + 225000) / 32768
    data = bytearray(5)
    data[0] = int(freqB) >> 8
    data[1] = int(freqB) & 0XFF
    data[2] = 0X90
    data[3] = 0X1E
    data[4] = 0X00
    i2c.writeto(0x60, data)
    
radio_frequency(99.7)
```

Call radio_frequency() to change the radio frequency.

This code does not enable search mode but also turns on stereo mode, soft mute, stereo noise cancelling and high cut.

For ESP32 boards SCL pin=22 and SDA pin=21.
