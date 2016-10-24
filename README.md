ESP8266 Micropython driver for SSD1306 OLED 128x64 display. 

**font5x7.fnt** is a 5 x 7 font file. It holds the font in pure binary and so uses only 480 bytes
When the display needs a character it reads the five bytes it needs from the file rather than loading the whole font into memory

**bmp.py** converts a 24-bit BITMAP file to a displayed image. Although this is a colour format, the image must be black and white.

**lcd_gfx.py** is not my work. It came from here https://forum.micropython.org/viewtopic.php?t=195

**icon.bmp** is the bitmap that is displayed in main.py. Be aware there is cuerrently no positioning, size check or resizing.

invoke the display with:

from SSD1306 import SSD1306

if you use different pins then you will need to specify these in the inital call

d = PCD8544()

d.poweron()

d.init_display() # displays the Project Pages logo 

d.clear() # clears the display buffer

d.display() # writes the buffer to the actual display

d._row is the character row

d._col is the character column

d.p_char('x') 
* puts the character into the display buffer
* advances _row and _col accordingly. They will wrap back to the top of the screen
* requires d.display() to show it

d.p_string('hello world') 
* prints the string to the display buffer
* advances _row and _col accoridngly. They will wrap back to the top of the screen
* requires d.display() to show it

d.pixel(x,y,fill)
* sets a pixel in the display buffer 
* this is for use by the lcd_gfx.py
* this allows you to draw lines, rectangles, triangles and circles. Filled or not

I have added a **main.py** that demonstrates the string printing and drawing capabilities


