#!/usr/bin/env python

# Display an xterm-256color color palette on the terminal, including color ids

reset_sequence = '\033[39;49m'

def esc(i):
	return '\033[48;5;'+str(i)+'m'

print(''.join([str(i).ljust(4) for i in range(16)]))
print('    '.join([esc(i) for i in range(16)])+'    ' + reset_sequence)

for j in range(6):
	for k in range(6):
		c = 16+j*6+k*6*6
		print(''.join([str(c+i).ljust(4) for i in range(6)]))
		print('    '.join([esc(c+i) for i in range(6)])+'    ' + reset_sequence)

print(''.join([str(i).ljust(4) for i in range(16+6*6*6, 16+6*6*6+24)]))
print('    '.join([esc(i) for i in range(16+6*6*6, 16+6*6*6+24)])+'    ' + reset_sequence)

