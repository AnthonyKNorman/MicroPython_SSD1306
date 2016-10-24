from time import sleep_ms
from machine import Pin, I2C

# Constants
DISPLAYOFF          = 0xAE
SETCONTRAST         = 0x81
DISPLAYALLON_RESUME = 0xA4
DISPLAYALLON        = 0xA5
NORMALDISPLAY       = 0xA6
INVERTDISPLAY       = 0xA7
DISPLAYON           = 0xAF
SETDISPLAYOFFSET    = 0xD3
SETCOMPINS          = 0xDA
SETVCOMDETECT       = 0xDB
SETDISPLAYCLOCKDIV  = 0xD5
SETPRECHARGE        = 0xD9
SETMULTIPLEX        = 0xA8
SETLOWCOLUMN        = 0x00
SETHIGHCOLUMN       = 0x10
SETSTARTLINE        = 0x40
MEMORYMODE          = 0x20
COLUMNADDR          = 0x21
PAGEADDR            = 0x22
COMSCANINC          = 0xC0
COMSCANDEC          = 0xC8
SEGREMAP            = 0xA0
CHARGEPUMP          = 0x8D
EXTERNALVCC         = 0x10	#0x1
SWITCHCAPVCC        = 0x20	#0x2
SETPAGEADDR         = 0xB0
SETCOLADDR_LOW      = 0x00
SETCOLADDR_HIGH     = 0x10
ACTIVATE_SCROLL                      = 0x2F
DEACTIVATE_SCROLL                    = 0x2E
SET_VERTICAL_SCROLL_AREA             = 0xA3
RIGHT_HORIZONTAL_SCROLL              = 0x26
LEFT_HORIZONTAL_SCROLL               = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL  = 0x2A

# I2C devices are accessed through a Device ID. This is a 7-bit
# value but is sometimes expressed left-shifted by 1 as an 8-bit value.
# A pin on SSD1306 allows it to respond to ID 0x3C or 0x3D. The board
# I bought from ebay used a 0-ohm resistor to select between "0x78"
# (0x3c << 1) or "0x7a" (0x3d << 1). The default was set to "0x78"
DEVID = 0x3c

# I2C communication here is either <DEVID> <CTL_CMD> <command byte>
# or <DEVID> <CTL_DAT> <display buffer bytes> <> <> <> <>...
# These two values encode the Co (Continuation) bit as b7 and the
# D/C# (Data/Command Selection) bit as b6.
CTL_CMD = 0x80
CTL_DAT = 0x40

class SSD1306(object):

	def __init__(self, height=64, external_vcc=True, i2c_devid=DEVID):
		self.external_vcc = external_vcc
		self.height       = 32 if height == 32 else 64
		self.pages        = int(self.height / 8)
		self.columns      = 128
		self._row = 0
		self._col = 0
		self._x = 0
		self._y = 0

		self.devid = i2c_devid
		self.offset = 1
		self.cbuffer = bytearray(2)
		self.cbuffer[0] = CTL_CMD

		self.i2c = I2C(scl=Pin(2), sda=Pin(16), freq=400000) 
		self.buffer = bytearray(self.offset + self.pages * self.columns)
		
	def clear(self):
		self.buffer = bytearray(self.offset + self.pages * self.columns)
		if self.offset == 1:
			self.buffer[0] = CTL_DAT

	def write_command(self, command_byte):
		self.cbuffer[1] = command_byte
		self.i2c.writeto(self.devid, self.cbuffer)

	def invert_display(self, invert):
		self.write_command(INVERTDISPLAY if invert else NORMALDISPLAY)

	def display(self):
		self.write_command(COLUMNADDR)
		self.write_command(0)
		self.write_command(self.columns - 1)
		self.write_command(PAGEADDR)
		self.write_command(0)
		self.write_command(self.pages - 1)
		self.i2c.writeto(self.devid, self.buffer)

	def set_pixel(self, x, y, state):
		index = x + (int(y / 8) * self.columns)
		if state:
			self.buffer[self.offset + index] |= (1 << (y & 7))
		else:
			self.buffer[self.offset + index] &= ~(1 << (y & 7))

	def init_display(self):
		chargepump = 0x10 if self.external_vcc else 0x14
		precharge  = 0x22 if self.external_vcc else 0xf1
		multiplex  = 0x1f if self.height == 32 else 0x3f
		compins    = 0x02 if self.height == 32 else 0x12
		contrast   = 0x9f # 0x8f if self.height == 32 else (0x9f if self.external_vcc else 0x9f)
		data = [DISPLAYOFF,
				SETDISPLAYCLOCKDIV, 0xF0,
				SETMULTIPLEX, 0x3f,
				SETDISPLAYOFFSET, 0x00,
				SETSTARTLINE | 0x00,
				CHARGEPUMP, 0x14,
				MEMORYMODE, 0x00,
				SEGREMAP | 0x00,
				COMSCANINC,
				SETCOMPINS, 0x12,
				SETCONTRAST, 0xCF,
				SETPRECHARGE, 0xF1,
				DISPLAYALLON_RESUME,
				NORMALDISPLAY,
				0x2e,		# stop scroll
				DISPLAYON]
		for item in data:
			self.write_command(item)
		# self.clear()
		self.display()

	def poweron(self):
		if self.offset == 1:
			sleep_ms(10)
		else:
			self.res.high()
			sleep_ms(1)
			self.res.low()
			sleep_ms(10)
			self.res.high()
			sleep_ms(10)

	def poweroff(self):
		self.write_command(DISPLAYOFF)

	def contrast(self, contrast):
		self.write_command(SETCONTRAST)
		self.write_command(contrast)
		
	def set_start_end_cols(self, start_col=0, end_col=None):
		if end_col is None:
			end_col = self.columns - 1
		if start_col < 0 or start_col > self.columns - 1:
			raise ValueError('Start column must be between 0 and %d.' % (self.columns - 1,))
		if end_col < start_col or end_col > self.columns -1:
			raise ValueError('End column must be between the start column (%d) and %d.' % (start_col, self.columns - 1))
		self.write_command(COLUMNADDR)
		self.write_command(start_col)  # Start column
		self.write_command(end_col)  # End column

	def set_start_end_pages(self, start_page=0, end_page=None):
		if end_page is None:
			end_page = self.pages - 1
		if start_page < 0 or start_page > self.pages - 1:
			raise ValueError('Start page must be between 0 and %d.' % (self.pages - 1,))
		if end_page < start_page or end_page > self.pages - 1:
			raise ValueError('End page must be between the start page (%d) and %d.' % (start_page, self.pages - 1))
		self.write_command(PAGEADDR)
		self.write_command(start_page)  # Page start address. (0 = reset)
		self.write_command(end_page) # Page end address.
			
	def p_char(self, ch):
		fp = (ord(ch)-0x20) * 5
		char_buf = bytearray([0,0,0,0,0])
		f = open('font5x7.fnt','rb')
		f.seek(fp)
		char_buf = f.read(5)
		bp = self.columns*self._row + 6*self._col + 1
		for x in range (0,5):
			self.buffer[bp+x] = char_buf[x]
			self.buffer[bp+5] = 0 # put in inter char space
		self._col += 1
		if (self._col>int(self.columns/6 - 1)):
			self._col = 0
			self._row += 1
			if (self._row>int(self.height/8 - 1)):
				self._row = 0	

	def p_string(self, str):
		for ch in (str):
			self.p_char(ch)

	def pixel(self,x,y,fill):
		r = int(y/8)
		i = r * self.columns + x + self.offset
		b = y % 8
		self.buffer[i] = self.buffer[i] | ( 1 << b )
		



