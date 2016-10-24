import time
from SSD1306 import SSD1306
import lcd_gfx
import network
import bmp
d = SSD1306()
d.poweron()
d.init_display()

d.clear()
d.p_string('The quick brown fox jumped over the lazy dog')
d.display()
time.sleep(5)

d.clear()
lcd_gfx.drawTrie(42,2,21,23,63,23,d,1)
d.display()
time.sleep(1)

lcd_gfx.drawFillRect(10,12,20,20,d,1)
d.display()
time.sleep(1)

lcd_gfx.drawCircle(70,24,10,d,1)
d.display()
time.sleep(1)

d.clear()
bmp.bmp('icon.bmp',d)
d.display()
time.sleep(5)

nic = network.WLAN(network.STA_IF)
ip, subnet, gateway, dns = nic.ifconfig()
d.clear()
d._row = 0
d._col = 2
d.p_string('IP Address')
d._row = 1
d._col = 0
d.p_string(ip)
d._row = 3
d._col = 3
d.p_string('Gateway')
d._row = 4
d._col = 0
d.p_string(gateway)
d.display()
time.sleep(5)
d.clear()

