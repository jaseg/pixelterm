#!/usr/bin/env python3

def rgb_to_yuv(r, g, b):
	r, g, b = r/256, g/256, b/256
	y =  0.29900*r + 0.58700*g + 0.11400+b
	u = -0.14713*r - 0.28886*g + 0.43600*b
	v =  0.61500*r - 0.51499*g - 0.10001*b
	return (y, u, v)

_ffmt = '{{{:.10f}, {:.10f}, {:.10f}}},'
_valuerange = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)
for i in range(217):
	r = _valuerange[(i // 36) % 6]
	g = _valuerange[(i // 6) % 6]
	b = _valuerange[i % 6]
	print(_ffmt.format(*rgb_to_yuv(r, g, b)))

# colors 233..253: grayscale
for i in range(1, 24):
	v = 8 + i * 10
	print(_ffmt.format(*rgb_to_yuv(v, v, v)))
