# MicroPython Driver for TEA5767 FM Radio Module

![41015747](https://user-images.githubusercontent.com/44191076/64875299-62e6e300-d67f-11e9-92d2-b0bdd43494aa.jpg)

[TEA5767](https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf) is a cheap but functional FM radio module, which allow you to build DIY FM radios. It comes with an antenna via a 3.5mm jack but have no internal volume control. 

This driver has been tested on ESP8266, ESP32 and RPi Pico running MicroPython v1.16.

The CircuitPython version can be found [here](https://github.com/alankrantas/circuitpython-TEA5767).

## Wiring

| Pin | Connect to |
| --- | --- |
| +5V | 3.3V or 5V |
| SDA | SDA |
| SLC | SCL |
| GND | GND |

Both 3.3V and 5V power works; 5V may results better sound quality.

## Import and Initialize

To import and initialize the module:

```python
from machine import Pin, SoftI2C
from TEA5767 import Radio

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)
radio = Radio(i2c)  # initialize and set to the lowest frequency
radio = Radio(i2c, freq=99.7)  # initialize and set to a specific frequency

print('Frequency: FM {}\nReady: {}\nStereo: {}\nADC level: {}'.format(
        radio.frequency, radio.is_ready,  radio.is_stereo, radio.signal_adc_level
        ))
```

You can use ```I2C``` module on pins that supported hardware I2C bus.

## Parameters

There are a list of parameters that you can set for the radio:

```python
radio = Radio(i2c, addr=0x60, freq=99.7, band="US", stereo=True,
                      soft_mute=True, noise_cancel=True, high_cut=True)
```

| Parameter | description |
| --- | --- |
| i2c | machine.I2C or machine.SoftI2C object |
| addr | I2C address (default 0x60) |
| freq | FM frequency (default = lowest freq by the band setting) |
| band | band limits; "US" (default) = US/Europe band (87.5-108 MHz); "JP" = Japan band (76-91 MHz) |
| stereo | stereo mode (default True = use stereo sound if possible; False = forced mono) |
| soft_mute | soft mute mode (noise control, default True) |
| noise_cancel | stereo noise cancelling (default True) |
| high_cut | high cut control (noise control, default True) |

## Set Frequency

Set the radio to a specific frequency:

```python
radio.set_frequency(99.7)  # set to FM 99.7
```

## Change Frequency

```python
radio.change_freqency(0.1)  # increase 0.1 MHz
radio.change_freqency(-0.1)  # decrease 0.1 MHz
```

These methods also will change the direction of search mode (see below).

## Search Mode

```python
radio.search(True)  # turn on search mode
radio.search(False)  # turn off search mode
radio.search(not radio.search_mode)  # toogle search mode
radio.search(True, dir=1, adc=7)  # turn on search mode and set search parameters
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

```radio.mute()``` is simply turning off the sound output. If you want to save power, use ```radio.standby()``` instead.

The TEA5767 also allows you to turn off right and/or left speaker, but I decided not to implement these functions.

## Read Status From the Radio

Some variables will be updated after calling ```radio.read()```:

```python
radio.read()
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

You may need to call it a few times with some time delay when the search mode is enabled (the radio frequency would jump around a bit).

## Manually Update the Radio

```python
radio.update()
```

This method will be automatically called by many other methods of the radio. If you wish to change some parameters, you can manually call ```radio.update()``` to update radio.

```python
radio.stereo_mode = True
radio.stereo_noise_cancelling_mode = True
radio.high_cut_mode = True
radio.update()
```

By default ```radio.update()``` will wait 50 ms at the end and then call ```radio.read()```.

## A Simplified MicroPython Version Without Using This Driver

If you just want to tune the frequency of TEA5767, you can use code as short as below (simply paste it into your script):

```python
from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)

def radio_frequency(freq):
    freqB = 4 * (freq * 1000000 + 225000) / 32768
    i2c.writeto(0x60, bytearray([int(freqB) >> 8, int(freqB) & 0XFF, 0X90, 0X1E, 0X00]))
    
radio_frequency(99.7)
```

This code does not read anything back and don't use enable search mode, but turn on stereo mode, soft mute, stereo noise cancelling and high cut.
