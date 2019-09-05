# MicroPython ESP8266/ESP32 driver for TEA5767 FM radio module by Alan Wang
# Datasheet: https://www.sparkfun.com/datasheets/Wireless/General/TEA5767.pdf

from machine import Pin, I2C

class Radio:
    
    def __init__(self, freq=0.0, scl=5, sda=4, addr=0x60, debug=False, band="US", 
                 stereo=True, soft_mute=True, noise_cancel=True, high_cut=True):
        self._i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=400000)
        self._address = addr
        self.frequency = freq
        self.band_limits = band
        self.standby_mode = False
        self.mute_mode = False
        self.soft_mute_mode = soft_mute
        self.search_mode = False
        self.search_direction = 1
        self.search_adc_level = 5
        self.stereo_mode = stereo
        self.stereo_noise_cancelling_mode = noise_cancel
        self.high_cut_mode = high_cut
        self.is_ready = False
        self.is_stereo = False
        self.signal_adc_level = 0
        self.debug = debug
        if self.frequency > 0.0:
            self.update()

    def set_frequency(self, freq=0.0):
        if self.frequency > 0.0:
            self.frequency = freq
            self.update()

    def change_freqency(self, change=0.1):
        if self.frequency + change > 0.0:
            self.frequency += change
            self.search_direction = 1 if change >= 0 else 0
            self.update()

    def search(self, mode=True, dir=1, adc=5, freq=0.0):
        if freq > 0.0:
            self.frequency = freq
        self.search_mode = mode
        self.search_direction = dir
        self.search_adc_level = adc if adc in [10, 7, 5, 0] else 5
        self.update()

    def mute(self, mode=True):
        self.mute_mode = mode
        self.update()
        
    def standby(self, mode=True):
        self.standby_mode = mode
        self.update()

    def update(self):
        freqB = 4 * (self.frequency * 1000000 + 225000) / 32768
        freqH = int(freqB) >> 8
        freqL = int(freqB) & 0Xff
        data = bytearray(5)
        str1 = ""
        str2 = ""
        str1 = "1" if self.mute_mode else "0"
        str1 += "1" if self.search_mode else "0"
        data[0] = int(str1 + "{0:b}".format(freqH), 2)
        data[1] = freqL
        str1 = ""
        str1 = str(self.search_direction) if self.search_direction in [0, 1] else "0"
        if self.search_adc_level == 10:
            str1 += "11"
        elif self.search_adc_level == 7:
            str1 += "10"
        elif self.search_adc_level == 5:
            str1 += "01"
        else:
            str1 += "00"
        str2 = "0" if self.stereo_mode else "1"
        data[2] = int(str1 + "1" + str2 + "000", 2)
        str1 = ""
        str2 = ""
        str1 = "1" if self.standby_mode else "0"   
        str1 += "1" if self.band_limits == "JP" else "0"
        str2 = "1" if self.soft_mute_mode else "0"
        str2 += "1" if self.high_cut_mode else "0"  
        str2 += "1" if self.stereo_noise_cancelling_mode else "0"
        data[3] = int("0" + str1 + "1" + str2 + "0", 2)
        data[4] = int('00000000', 2)
        self._i2c.writeto(self._address, data)
        self.read()
        
    def read(self):
        buf = self._i2c.readfrom(self._address, 5)
        self.frequency = round(((int((("{:08b}".format(int(buf[0])))[2:8] + "{:08b}".format(int(buf[1]))), 2) * 32768 / 4) - 225000) / 1000000, 1)
        self.is_ready = int(buf[0]) >> 7 == 1
        self.is_stereo = int(buf[2]) >> 7 == 1
        self.signal_adc_level = int(buf[3]) >> 4
        if self.debug:
            print("FM frequency: " + str(self.frequency) + " MHz")
            print("Search mode: " + str(self.search_mode))
            print("Station ready: " + str(self.is_ready))
            print("Signal is stereo: " + str(self.is_stereo))
            print("Signal ADC resolution: " + str(self.signal_adc_level))
            print("")
