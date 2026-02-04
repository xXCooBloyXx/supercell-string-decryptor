import struct

class ByteStream:
	def __init__(self, buffer=None, endian="<"):
		self.buffer = buffer or b""
		self.endian = endian
		self.offset = 0

	def align(self, value):
		self.skip((value - (self.tell() % value)) % value)

	def eof(self):
		return self.offset == len(self.buffer)

	def rewind(self):
		self.offset = 0

	def seek(self, value):
		self.offset = value

	def skip(self, value):
		self.offset += value

	def tell(self):
		return self.offset

	def readBytes(self, length):
		result = self.buffer[self.offset:self.offset+length]
		self.offset += length
		return result

	def readInt8(self):
		return struct.unpack(self.endian + "b", self.readBytes(1))[0]

	def readUInt8(self):
		return struct.unpack(self.endian + "B", self.readBytes(1))[0]

	def readInt16(self):
		return struct.unpack(self.endian + "h", self.readBytes(2))[0]

	def readUInt16(self):
		return struct.unpack(self.endian + "H", self.readBytes(2))[0]

	def readInt24(self):
		return int.from_bytes(self.readBytes(3), "little" if self.endian == "<" else "big", signed=True)

	def readUInt24(self):
		return int.from_bytes(self.readBytes(3), "little" if self.endian == "<" else "big", signed=False)

	def readInt32(self):
		return struct.unpack(self.endian + "i", self.readBytes(4))[0]

	def readUInt32(self):
		return struct.unpack(self.endian + "I", self.readBytes(4))[0]

	def readInt64(self):
		return struct.unpack(self.endian + "q", self.readBytes(8))[0]

	def readUInt64(self):
		return struct.unpack(self.endian + "Q", self.readBytes(8))[0]

	def readFloat16(self):
		return struct.unpack(self.endian + "e", self.readBytes(2))[0]

	def readFloat32(self):
		return struct.unpack(self.endian + "f", self.readBytes(4))[0]

	def readFloat64(self):
		return struct.unpack(self.endian + "d", self.readBytes(8))[0]

	def readBoolean(self):
		return self.readUInt8() == 1

	def readCharacters(self, length):
		return self.readBytes(length).decode("UTF-8")

	def readString(self, lengthType=2):
		if lengthType == 1:
			length = self.readUInt8()
		elif lengthType == 2:
			length = self.readUInt16()
		elif lengthType == 3:
			length = self.readUInt24()
		elif lengthType == 4:
			length = self.readUInt32()
		return self.readCharacters(length)

	def readCString(self):
		result = []
		while True:
			byte = self.readUInt8()
			if byte == 0:
				break
			result.append(byte)
		return bytes(result).decode("UTF-8")

	def readLEB128(self):
		result = 0
		shift = 0
		while True:
			byte = self.readUInt8()
			result |= (byte & 0x7F) << shift
			shift += 7
			if (byte & 0x80) == 0:
				if (shift < 64) and (byte & 0x40):
					result |= - (1 << shift)
				break
		return result

	def readULEB128(self):
		result = 0
		shift = 0
		while True:
			byte = self.readUInt8()
			result |= (byte & 0x7F) << shift
			if (byte & 0x80) == 0:
				break
			shift += 7
		return result

	def readMatrix4x4(self):
		return [[self.readFloat32() for j in range(4)] for i in range(4)]

	readByte = readInt8
	readUByte = readUInt8
	readShort = readInt16
	readUShort = readUInt16
	readInt = readInt32
	readUInt = readUInt32
	readLong = readInt64
	readULong = readUInt64
	readHalf = readFloat16
	readFloat = readFloat32
	readDouble = readFloat64
	readBool = readBoolean

	def writeBytes(self, data):
		self.buffer += data
		self.offset += len(data)

	def writeInt8(self, value):
		self.writeBytes(struct.pack(self.endian + "b", value))

	def writeUInt8(self, value):
		self.writeBytes(struct.pack(self.endian + "B", value))

	def writeInt16(self, value):
		self.writeBytes(struct.pack(self.endian + "h", value))

	def writeUInt16(self, value):
		self.writeBytes(struct.pack(self.endian + "H", value))

	def writeInt24(self, value):
		self.writeBytes(value.to_bytes(3, "little" if self.endian == "<" else "big", signed=True))

	def writeUInt24(self, value):
		self.writeBytes(value.to_bytes(3, "little" if self.endian == "<" else "big", signed=False))

	def writeInt32(self, value):
		self.writeBytes(struct.pack(self.endian + "i", value))

	def writeUInt32(self, value):
		self.writeBytes(struct.pack(self.endian + "I", value))

	def writeInt64(self, value):
		self.writeBytes(struct.pack(self.endian + "q", value))

	def writeUInt64(self, value):
		self.writeBytes(struct.pack(self.endian + "Q", value))

	def writeFloat16(self, value):
		self.writeBytes(struct.pack(self.endian + "e", value))

	def writeFloat32(self, value):
		self.writeBytes(struct.pack(self.endian + "f", value))

	def writeFloat64(self, value):
		self.writeBytes(struct.pack(self.endian + "d", value))

	def writeBoolean(self, value):
		self.writeUInt8(int(value is True))

	def writeCharacters(self, value):
		return self.writeBytes(value.encode("UTF-8"))

	def writeString(self, value, lengthType=2):
		data = value.encode("UTF-8")
		if lengthType == 1:
			self.writeUInt8(len(data))
		elif lengthType == 2:
			self.writeUInt16(len(data))
		elif lengthType == 3:
			self.writeUInt24(len(data))
		elif lengthType == 4:
			self.writeUInt32(len(data))
		self.writeBytes(data)

	def writeCString(self, value):
		self.writeBytes(value.encode("UTF-8") + b"\x00")

	def writeULEB128(self, value):
		while True:
			byte = value & 0x7F
			value >>= 7
			if value == 0:
				self.writeUInt8(byte)
				break
			else:
				self.writeUInt8(byte | 0x80)

	def writeLEB128(self, value):
		while True:
			byte = value & 0x7F
			value >>= 7
			if (value == 0 or value == -1) and byte & 0x40 != 0:
				self.writeUInt8(byte)
				break
			else:
				self.writeUInt8(byte | 0x80)

	def writeMatrix4x4(self, value):
		[[self.writeFloat32(j) for j in i] for i in value]

	writeByte = writeInt8
	writeUByte = writeUInt8
	writeShort = writeInt16
	writeUShort = writeUInt16
	writeInt = writeInt32
	writeUInt = writeUInt32
	writeLong = writeInt64
	writeULong = writeUInt64
	writeHalf = writeFloat16
	writeFloat = writeFloat32
	writeDouble = writeFloat64
	writeBool = writeBoolean