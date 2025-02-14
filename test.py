
parityLUT = [
	0x80,0x01,0x02,0x83,0x04,0x85,0x86,0x07,
	0x08,0x89,0x8A,0x0B,0x8C,0x0D,0x0E,0x8F,
	0x10,0x91,0x92,0x13,0x94,0x15,0x16,0x97,
	0x98,0x19,0x1A,0x9B,0x1C,0x9D,0x9E,0x1F,
	0x20,0xA1,0xA2,0x23,0xA4,0x25,0x26,0xA7,
	0xA8,0x29,0x2A,0xAB,0x2C,0xAD,0xAE,0x2F,
	0xB0,0x31,0x32,0xB3,0x34,0xB5,0xB6,0x37,
	0x38,0xB9,0xBA,0x3B,0xBC,0x3D,0x3E,0xBF,
	0x40,0xC1,0xC2,0x43,0xC4,0x45,0x46,0xC7,
	0xC8,0x49,0x4A,0xCB,0x4C,0xCD,0xCE,0x4F,
	0xD0,0x51,0x52,0xD3,0x54,0xD5,0xD6,0x57,
	0x58,0xD9,0xDA,0x5B,0xDC,0x5D,0x5E,0xDF,
	0xE0,0x61,0x62,0xE3,0x64,0xE5,0xE6,0x67,
	0x68,0xE9,0xEA,0x6B,0xEC,0x6D,0x6E,0xEF,
	0x70,0xF1,0xF2,0x73,0xF4,0x75,0x76,0xF7,
	0xF8,0x79,0x7A,0xFB,0x7C,0xFD,0xFE,0x7F
];

def paritySet(string):
	string = bytes(string,'ascii')
	outputString = ''
	
	for char in string:
		outputString += chr(parityLUT[char])
	
	return outputString

print(paritySet("1234567890"))