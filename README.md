# MicroPython ESP8266/ESP32 Driver for TEA5767 FM Radio Module

![41015747](https://user-images.githubusercontent.com/44191076/64875299-62e6e300-d67f-11e9-92d2-b0bdd43494aa.jpg)

[TEA5767](https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf) is one of the cheaper FM radio receiver modules, which allow you to build DIY FM radios real quick. It comes with an antenna with a 3.5mm audio jack but with does not have volume control.

This is the driver for MicroPython on ESP8266/ESP32 boards. I've tested it on NodeMCU V2 and WeMos D1 mini (ESP8266s running firmware v1.11-8) as well as BPI:bit and DOIT ESP32 DevKit V1 (ESP32 running v1.11-37).

## Wiring

* +5V -> power (both 3.3V and 5V works)
* SDA -> SDA
* SLC -> SCL
* GND -> GND

From personal experiments the TEA5767 works better (have better reception/sound quality) in 5V with sufficent power supply. The power from most MCU boards alone might give you a lot of noise.

## Import and Initialization on ESP8266

To import and initialize the module:

```python
from machine import Pin, I2C
from TEA5767 import Radio

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
radio = Radio(i2c, freq=99.7)
```

The module would immediately tune to the frequency. If you did not specify a frequency here, the TEA5767 would set to lowest freqency of current band limit (see below).

There are also a series of parameters you can set:

```python
radio = Radio(i2c, addr=0x60, freq=99.7, band="US", stereo=True,
                      soft_mute=True, noise_cancel=True, high_cut=True)
```

* i2c: MicroPython I2C object
* addr: I2C address (default 0x60)
* freq: FM frequency
* band: band limits; "US" (default) = US/Europe band (87.5-108 MHz), "JP" = Japan band (76-91 MHz)
* stereo: stereo mode (default True; set as False = forced mono)
* soft_mute: soft mute (noise control, default True)
* noise_cancel: stereo noise cancelling (default True)
* high_cut: high cut control (noise control, default True)

## Import and Initialization on ESP32

It's basic the same as ESP8266, however the SCL and SDA pins are 22 and 21 respectively:

```python
from machine import Pin, I2C
from TEA5767 import Radio

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
radio = Radio(i2c, freq=99.7)
```

Other parameters are as same as above.

## Set/Change Frequency

Tuning to a specific frequency:

```python
radio.set_frequency(freq=99.7)
```

The frequency would not go beyond current band limit.

Or you can change the currently frequency by some degree (takes effect immediately), like turning a knob on radios:

```python
radio.change_freqency(change=0.1)
radio.change_freqency(change=-0.1)
```

## Search Mode

You can set the TEA5756 to half-auto select a possible working station near a frequency:

```python
radio.search(True)
radio.search(False)
radio.search(mode=True)
radio.search(mode=True, dir=1, adc=7)
```

When the search mode is turned on (True), the actual frequency may change after you selected the frequency. It may take a little while - you'll have to keep calling <b>radio.read()</b> and read the value <b>radio.frequency</b> (see below).

* dir = search direction; 1 means go up on the frequency (default), 0 means go down.
* adc = signal ADC resolution (sound quality), default 7. The adc level can be set as 0 (no search), 5, 7 or 10. In search mode the TEA5767 would search stations with ADC resolution higher than the level you select.

And if you call <b>radio.change_freqency()</b>, the search mode direction will be set to the same direction of frequency change.

To toogle search mode:

```python
radio.search(not radio.search_mode)
```

## Mute/Standby Mode

```python
radio.mute(True)
radio.standby(True)
```

Mute is simply turning off the sound output. If you want to save power, use <b>radio.standby()</b>.

The TEA5767 also allows you to turn off right and/or left speaker, but I did not implement these functions.

## Read Data

You can retrieve some info from the TEA5767:

```python
radio.read()
```

Then you can also get the following values:

```python
my_variable = radio.frequency
my_variable = radio.search_mode
my_variable = radio.is_ready
my_variable = radio.is_stereo
my_variable = radio.signal_adc_level
```

* radio.frequency: current frequency, float number (may change due to enabling search mode)
* radio.search_mode: search mode status (True/False)
* radio.is_ready: station is ready, probably meaning the signal is strong enough? (True/False)
* radio.is_stereo: stereo mode status (True/False)
* radio.signal_adc_level: station ADC resolution (0, 5, 7 or 10)

## A Simplified Version Without Using Module

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

Call <b>radio_frequency()</b> to change the radio frequency.

This code does not enable search mode but turns on stereo mode, soft mute, stereo noise cancelling and high cut.

For ESP32 boards set SCL pin=22 and SDA pin=21.
