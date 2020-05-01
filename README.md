# MicroPython ESP8266/ESP32 Driver for TEA5767 FM Radio Module

![41015747](https://user-images.githubusercontent.com/44191076/64875299-62e6e300-d67f-11e9-92d2-b0bdd43494aa.jpg)

[TEA5767](https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf) is a cheap FM radio module, which allow you to build DIY FM radios. It comes with an antenna via a 3.5mm audio jack but have no internal volume control. 

This driver has been tested on ESP8266 and ESP32 boards running MicroPython v1.12.

## Wiring

* +5V -> power (both 3.3V and 5V works; 5V may results better sound quality)
* SDA -> SDA pin
* SLC -> SCL pin
* GND -> GND

## Import and Initialize

To import and initialize the module:

```python
from machine import Pin, I2C
from TEA5767 import Radio

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000) # change the pins if you are using ESP32
radio = Radio(i2c) # initialize and set to the lowest frequency
radio = Radio(i2c, freq=99.7)  # initialize and set to a specific frequency
```

There are a series of parameters you can set as well:

```python
radio = Radio(i2c, addr=0x60, freq=99.7, band="US", stereo=True,
                      soft_mute=True, noise_cancel=True, high_cut=True)
```

* i2c: MicroPython I2C object
* addr: I2C address (default 0x60)
* freq: FM frequency
* band: band limits; "US" (default) = US/Europe band (87.5-108 MHz); "JP" = Japan band (76-91 MHz)
* stereo: stereo mode (default True; set as False = forced mono)
* soft_mute: soft mute (noise control, default True)
* noise_cancel: stereo noise cancelling (default True)
* high_cut: high cut control (noise control, default True)

## Set Frequency

Set the radio to a specific frequency:

```python
radio.set_frequency(99.7)
```

## Change Frequency

```python
radio.change_freqency(0.1) # increase 0.1 MHz
radio.change_freqency(-0.1) # decrease 0.1 MHz
```

These methods also will change the direction of search mode (see below).

## Search Mode

```python
radio.search(True) # turn on search mode
radio.search(False) # turn off search mode
radio.search(not radio.search_mode) # toogle search mode
radio.search(True, dir=1, adc=7) # turn on search mode and set search parameters
```

If the search mode is enabled, the radio would attempt to find a station with strong signal whenever you set a new frequency.

* dir = search direction; 1 = search upward along frequency (default), 0 = downward.
* adc = desired signal ADC resolution (sound quality), default 7. Can be set as 0, 5, 7 or 10. The radio would try to find a station which ADC level satisfied this setting.

The radio might need some time to find a new station.

## Mute/standby Mode

```python
radio.mute(True)
radio.standby(True)
```

<b>radio.mute()</b> is simply turning off the sound output. If you want to save power, use <b>radio.standby() instead</b>.

The TEA5767 also allows you to turn off right and/or left speaker, but I decided not to implement these functions.

## Read Status From the Radio

```python
my_variable = radio.frequency
my_variable = radio.search_mode
my_variable = radio.is_ready
my_variable = radio.is_stereo
my_variable = radio.signal_adc_level
```

* radio.frequency: current frequency, float number (may be changed in search mode)
* radio.search_mode: search mode status (True/False)
* radio.is_ready: station is ready (signal is strong enough)? (True/False)
* radio.is_stereo: stereo mode status? (True/False)
* radio.signal_adc_level: station ADC resolution? (0, 5, 7 or 10)

To update these data:

```python
radio.read() # update radio status
```

You may need to call it multiple times when the search mode is enabled (because radio.frequency would be changed).

## Manually Update the Radio

```python
radio.update()
radio.update(read=False) # update but do not call radio.read()
```

This method will be automatically called by many other methods of the radio. If you wish to change some parameters, you can manually call <b>radio.update()</b> to update radio.

```python
radio.stereo_mode = True
radio.stereo_noise_cancelling_mode = True
radio.high_cut_mode = True
```

By default <b>radio.update()</b> will call <b>radio.read()</b> at the end. However, You can set the <b>read</b> parameter to False if you want to speed thing up a little bit.

## A Simplified MicroPython Version Without Using This Driver

If you just want to tune the frequency of TEA5767, you can use code as short as below (simply paste it into your script):

```python
from machine import Pin, I2C

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

def radio_frequency(freq):
    freqB = 4 * (freq * 1000000 + 225000) / 32768
    buf = bytearray(5)
    buf[0] = int(freqB) >> 8
    buf[1] = int(freqB) & 0XFF
    buf[2] = 0X90
    buf[3] = 0X1E
    buf[4] = 0X00
    i2c.writeto(0x60, buf)
    
radio_frequency(99.7)
```

Then simply call <b>radio_frequency()</b> to change the radio frequency.

This code does not enable search mode but turns on stereo mode, soft mute, stereo noise cancelling and high cut.
