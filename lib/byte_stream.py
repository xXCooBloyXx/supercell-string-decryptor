import struct

class ByteStream:
	def __init__(self, buffer=b"", endian="little"):
		self.buffer = buffer
		self.endian = endian
		
		self.offset = 0

	def seek(self, value):
		self.offset = value
	
	def skip(self, value):
		self.seek(self.tell() + value)
	
	def tell(self):
		return self.offset
	
	def isAtEnd(self):
		return self.tell() == len(self.buffer)
	
	def align(self, value):
		self.skip((value - (self.tell() % value)) % value)
	
	# Read
	def readBytes(self, size):
		offset = self.tell()
		result = self.buffer[offset:offset + size]
		self.skip(size)
		return result
	
	def readIntOfSize(self, size):
		return int.from_bytes(self.readBytes(size), self.endian, signed=True)
	
	def readUIntOfSize(self, size):
		return int.from_bytes(self.readBytes(size), self.endian, signed=False)
	
	def readInt8(self):
		return self.readIntOfSize(1)
	
	def readUInt8(self):
		return self.readUIntOfSize(1)
	
	def readInt16(self):
		return self.readIntOfSize(2)
	
	def readUInt16(self):
		return self.readUIntOfSize(2)
	
	def readInt24(self):
		return self.readIntOfSize(3)
	
	def readUInt24(self):
		return self.readUIntOfSize(3)
	
	def readInt32(self):
		return self.readIntOfSize(4)
	
	def readUInt32(self):
		return self.readUIntOfSize(4)
	
	def readInt64(self):
		return self.readIntOfSize(8)
	
	def readUInt64(self):
		return self.readUIntOfSize(8)
	
	def readFloat32(self):
		return struct.unpack((">" if self.endian == "big" else "<") + "f", self.readBytes(4))[0]
	
	def readFloat64(self):
		return struct.unpack((">" if self.endian == "big" else "<") + "d", self.readBytes(8))[0]
	
	def readBoolean(self):
		return self.readUInt8() != 0
	
	def readChars(self, length):
		return self.readBytes(length).decode("UTF-8")
	
	def readString(self, lengthSize=2):
		return self.readChars(self.readUIntOfSize(lengthSize))
	
	def readCString(self):
		result = []
		while (byte := self.readUInt8()) != 0:
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
				if byte & 0x40:
					result |= -(1 << shift)
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
		return [[self.readFloat32() for _ in range(4)] for _ in range(4)]
	
	# Write
	def writeBytes(self, value):
		self.buffer += value
		self.skip(len(value))
	
	def writeIntOfSize(self, value, size):
		self.writeBytes(int.to_bytes(value, size, self.endian, signed=True))
	
	def writeUIntOfSize(self, value, size):
		self.writeBytes(int.to_bytes(value, size, self.endian, signed=False))
	
	def writeInt8(self, value):
		self.writeIntOfSize(value, 1)
	
	def writeUInt8(self, value):
		self.writeUIntOfSize(value, 1)
	
	def writeInt16(self, value):
		self.writeIntOfSize(value, 2)
	
	def writeUInt16(self, value):
		self.writeUIntOfSize(value, 2)
	
	def writeInt24(self, value):
		self.writeIntOfSize(value, 3)
	
	def writeUInt24(self, value):
		self.writeUIntOfSize(value, 3)
	
	def writeInt32(self, value):
		self.writeIntOfSize(value, 4)
	
	def writeUInt32(self, value):
		self.writeUIntOfSize(value, 4)
	
	def writeInt64(self, value):
		self.writeIntOfSize(value, 8)
	
	def writeUInt64(self, value):
		self.writeUIntOfSize(value, 8)
	
	def writeFloat32(self, value):
		self.writeBytes(struct.pack((">" if self.endian == "big" else "<") + "f", value))
	
	def writeFloat64(self, value):
		self.writeBytes(struct.pack((">" if self.endian == "big" else "<") + "d", value))
	
	def writeBoolean(self, value):
		self.writeUInt8(1 if value else 0)
	
	def writeChars(self, value):
		self.writeBytes(value.encode("UTF-8"))
	
	def writeString(self, value, lengthSize=2):
		self.writeUIntOfSize(len(value.encode("UTF-8")), lengthSize)
		self.writeChars(value)
	
	def writeCString(self, value):
		self.writeChars(value)
		self.writeUInt8(0)
	
	def writeLEB128(self, value):
		while True:
			byte = value & 0x7F
			value >>= 7
			if (value == 0 and byte & 0x40 == 0) or (value == -1 and byte & 0x40 != 0):
				self.writeUInt8(byte)
				break
			else:
				self.writeUInt8(byte | 0x80)
	
	def writeULEB128(self, value):
		while True:
			byte = value & 0x7F
			value >>= 7
			if value == 0:
				self.writeUInt8(byte)
				break
			else:
				self.writeUInt8(byte | 0x80)
	
	def writeMatrix4x4(self, value):
		for row in value:
			for cell in row:
				self.writeFloat32(cell)