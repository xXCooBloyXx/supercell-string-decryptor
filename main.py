import os

from lib.byte_stream import ByteStream

""" Examples:
fileName = "bs_v29.258_x32_libg.so"
lv1_string_encryption_decryption_keyOffset = 0xA64106
lv1_string_encryption_read_ranges_range_tableOffset = 0x908584

fileName = "bs_v29.270_x64_libg.so"
lv1_string_encryption_decryption_keyOffset = 0xD97FEF
lv1_string_encryption_read_ranges_range_tableOffset = 0xA67F10

fileName = "bs_v29.274_ios"
lv1_string_encryption_decryption_keyOffset = 0x275C0F3
lv1_string_encryption_read_ranges_range_tableOffset = 0x2846610

fileName = "bs_v36.218_x64_libg.so"
lv1_string_encryption_decryption_keyOffset = 0x1057EAC
lv1_string_encryption_read_ranges_range_tableOffset = 0x101A7E4
"""

fileName = "bs_v29.270_x64_libg.so"
lv1_string_encryption_decryption_keyOffset = 0xD97FEF
lv1_string_encryption_read_ranges_range_tableOffset = 0xA67F10

def xor(key, data):
	result = []
	for i, byte in enumerate(data):
		result.append(byte ^ key[i % len(key)])
	return bytes(result)

fileBaseName, fileExtension = os.path.splitext(fileName)
fileData = bytearray(open(fileName, "rb").read())
stream = ByteStream(fileData)

stream.seek(lv1_string_encryption_decryption_keyOffset)
lv1_string_encryption_decryption_key = stream.readBytes(128)

stream.seek(lv1_string_encryption_read_ranges_range_tableOffset)
count = 0
with open(f"{fileBaseName}_dump.txt", "w") as dumpFile:
	v1 = stream.readInt32()
	v2 = stream.readInt32()
	v3 = stream.readInt32()
	while True:
		v4 = stream.readInt32()
		v5 = stream.readInt32()
		v6 = stream.readInt32()
		endOffset = stream.tell()
		
		offset = (v4 - v1 - v2 - v3 + lv1_string_encryption_read_ranges_range_tableOffset) & 0xFFFFFFFF
		length = (v2 + v4 - v5) & 0xFFFFFFFF
		
		if length == 0:
			break
		
		stream.seek(offset)
		
		value = xor(lv1_string_encryption_decryption_key, stream.readBytes(length))
		stream.buffer[offset:offset + length] = value
		dumpFile.write(f"{hex(offset)} {value}\n")
		
		count += 1
		
		stream.seek(endOffset)
		v1, v2, v3 = v4, v5, v6

outputFileData = stream.buffer
with open(f"{fileBaseName}_decrypted{fileExtension}", "wb") as outputFile:
	outputFile.write(outputFileData)

print(f"Decrypted {count} strings")