import sys
import os

from utils.bytestream import ByteStream

"""
You need to specify key decryption and range table addresses, for example:

fileName = "bs_v29.258_x32_libg.so"
lv1_string_encryption_decryption_keyAddress = 0xA64106
lv1_string_encryption_read_ranges_range_tableAddress = 0x908584

fileName = "bs_v29.270_x64_libg.so"
lv1_string_encryption_decryption_keyAddress = 0xD97FEF
lv1_string_encryption_read_ranges_range_tableAddress = 0xA67F10

fileName = "bs_v29.274_ios"
lv1_string_encryption_decryption_keyAddress = 0x275C0F3
lv1_string_encryption_read_ranges_range_tableAddress = 0x2846610

fileName = "bs_v36.218_x64_libg.so"
lv1_string_encryption_decryption_keyAddress = 0x1057EAC
lv1_string_encryption_read_ranges_range_tableAddress = 0x101A7E4
"""

fileName = None
lv1_string_encryption_decryption_keyAddress = None
lv1_string_encryption_read_ranges_range_tableAddress = None

if None in [fileName, lv1_string_encryption_decryption_keyAddress, lv1_string_encryption_read_ranges_range_tableAddress]:
	raise Exception("Make sure that all required fields are specified")

def xor(key, data1):
	data2 = bytearray(len(data1))

	for i in range(len(data1)):
		data2[i] = data1[i] ^ key[i % len(key)]

	return bytes(data2)

fileData = bytearray(open(fileName, "rb").read())
stream = ByteStream(fileData)

stream.seek(lv1_string_encryption_decryption_keyAddress)
lv1_string_encryption_decryption_key = stream.readBytes(128)

strings = []

stream.seek(lv1_string_encryption_read_ranges_range_tableAddress)
while True:
	v1 = stream.readInt()
	v2 = stream.readInt()
	v3 = stream.readInt()
	
	# These 2 shouldnt change offset but im too lazy to read manually
	v4 = stream.readInt()
	v5 = stream.readInt()
	stream.skip(-8)
	
	address = (v4 - v3 - v2 - v1 + lv1_string_encryption_read_ranges_range_tableAddress) & 0xFFFFFFFF
	length = (v2 + v4 - v5) & 0xFFFFFFFF
	
	if length == 0:
		break
	
	oldAddress = stream.tell()
	
	stream.seek(address)
	strings.append([address, xor(lv1_string_encryption_decryption_key, stream.readBytes(length))])
	
	stream.seek(oldAddress)

for string in strings:
	fileData[string[0]:string[0]+len(string[1])] = string[1]

if fileName.lower().endswith(".so"):
	fileBaseName, fileExtension = os.path.splitext(fileName)
else:
	fileBaseName = fileName
	fileExtension = ""

#with open(f"{fileBaseName}_dump.txt", "w") as dumpFile:
#	for string in strings:
#		dumpFile.write(f"{hex(string[0])} {string[1]}\n")

with open(f"{fileBaseName}_decrypted{fileExtension}", "wb") as outFile:
	outFile.write(fileData)

print(f"Decrypted {len(strings)} strings")
