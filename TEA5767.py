"""
MicroPython ESP8266/ESP32 driver for TEA5767 FM radio module:
https://github.com/alankrantas/micropython-TEA5767

TEA5767 Datasheet:
https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf

MIT License

Copyright (c) 2020 Alan Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class Radio:
    
    FREQ_RANGE_US = (87.5, 108.0)
    FREQ_RANGE_JP = (76.0, 91.0)
    
    def __init__(self, i2c, addr=0x60, freq=0.0, band='US', stereo=True,
                 soft_mute=True, noise_cancel=True, high_cut=True):
        self._i2c = i2c
        self._address = addr
        self.frequency = freq
        self.band_limits = band
        self.standby_mode = False
        self.mute_mode = False
        self.soft_mute_mode = soft_mute
        self.search_mode = False
        self.search_direction = 1
        self.search_adc_level = 7
        self.stereo_mode = stereo
        self.stereo_noise_cancelling_mode = noise_cancel
        self.high_cut_mode = high_cut
        self.is_ready = False
        self.is_stereo = False
        self.signal_adc_level = 0
        self.update()

    def set_frequency(self, freq):
        self.frequency = freq
        self.update()

    def change_freqency(self, change):
        self.frequency += change
        self.search_direction = 1 if change >= 0 else 0
        self.update()

    def search(self, mode, dir=1, adc=7):
        self.search_mode = mode
        self.search_direction = dir
        self.search_adc_level = adc if adc in (10, 7, 5, 0) else 7
        self.update()

    def mute(self, mode):
        self.mute_mode = mode
        self.update()
        
    def standby(self, mode):
        self.standby_mode = mode
        self.update()

    def read(self):
        buf = self._i2c.readfrom(self._address, 5)
        freqB = ('{:08b}'.format(int(buf[0])))[2:8] + '{:08b}'.format(int(buf[1]))
        self.frequency = round(((int(freqB, 2) * 32768 / 4) - 225000) / 1000000, 1)
        self.is_ready = int(buf[0]) >> 7 == 1
        self.is_stereo = int(buf[2]) >> 7 == 1
        self.signal_adc_level = int(buf[3]) >> 4

    def update(self):
        buf = bytearray(5)
        cmd = ''
        if self.band_limits == 'US':
            if self.frequency < self.FREQ_RANGE_US[0]:
                self.frequency = self.FREQ_RANGE_US[0]
            elif self.frequency > self.FREQ_RANGE_US[1]:
                self.frequency = self.FREQ_RANGE_US[1]
        else:
            if self.frequency < self.FREQ_RANGE_JP[0]:
                self.frequency = self.FREQ_RANGE_JP[0]
            elif self.frequency > self.FREQ_RANGE_JP[1]:
                self.frequency = self.FREQ_RANGE_JP[1]
        freqB = 4 * (self.frequency * 1000000 + 225000) / 32768
        freqH = int(freqB) >> 8
        freqL = int(freqB) & 0Xff
        cmd = '1' if self.mute_mode else '0'
        cmd += '1' if self.search_mode else '0'
        buf[0] = int(cmd + '{:06b}'.format(freqH), 2)
        buf[1] = freqL
        cmd = '1' if self.search_direction == '1' else '0'
        if self.search_adc_level == 10:
            cmd += '11'
        elif self.search_adc_level == 7:
            cmd += '10'
        elif self.search_adc_level == 5:
            cmd += '01'
        else:
            cmd += '00'
        cmd += '1'
        cmd += '0' if self.stereo_mode else '1'
        cmd += '000'
        buf[2] = int(cmd, 2)
        cmd = '0'
        cmd += '1' if self.standby_mode else '0'   
        cmd += '1' if self.band_limits == 'JP' else '0'
        cmd += '1'
        cmd += '1' if self.soft_mute_mode else '0'
        cmd += '1' if self.high_cut_mode else '0'  
        cmd += '1' if self.stereo_noise_cancelling_mode else '0'
        cmd += '0'
        buf[3] = int(cmd, 2)
        buf[4] = 0
        self._i2c.writeto(self._address, buf)
        self.read()
