def bmp(fname, display):
	f=open(fname,'rb')
	b=bytearray(54)
	b=f.read(54)
	# header check
	if b[0]==0x42 and b[1]==0x4D:
		# is bitmap
		size = b[2] + (b[3]<<8) + (b[4]<<16) +(b[5]<<24)
		offset = b[10] + (b[11]<<8) + (b[12]<<16) +(b[13]<<24)
		width = b[18] + (b[19]<<8) + (b[20]<<16) +(b[21]<<24)
		height = b[22] + (b[23]<<8) + (b[24]<<16) +(b[25]<<24)
		color_planes = b[26] + (b[27]<<8)
		bits_per_pixel = b[28] + (b[29]<<8)
		compression = b[30] + (b[31]<<8) + (b[32]<<16) +(b[33]<<24)
		image_size = b[34] + (b[35]<<8) + (b[36]<<16) +(b[37]<<24)
		
		f.seek(offset)
		
		row_bytes = int(bits_per_pixel/8) * width
		# Add up to multiple of 4
		if row_bytes % 4 > 0:
			row_bytes += 4 - row_bytes % 4
		
		buffer = bytearray(row_bytes)
		for row in range(height):
			# print(row)
			# read in a whole row
			buffer=f.read(row_bytes)
			index = 0
			for index in range(width):
				y = (height-1) - row
				x = index
				if buffer[index*3]!=0xff:
					display.pixel(x,y,1)
	f.close()

