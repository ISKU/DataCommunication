import socket
import time
import sys
import struct

if len(sys.argv) < 2:
	print "[Port Number] [Directory Path]"
	sys.exit()

udpIP = ""
udpPORT = int(sys.argv[1])
directoryPath = sys.argv[2]

bufferSize = 1024
sequenceSize = 3
windowSize = (pow(2, sequenceSize) - 1)
headerSize = 4

sequence = 0
count = 0
sequenceData = None
writeData = None

dataTable = {}

def printTransferRate(size, fileSize):
	print "%d / %d (current/total size), %.2f%%" \
		% (size, fileSize, (float(size) / float(fileSize)) * 100)

def printFileInfo(addr, fileName, fileSize):
	print "Client Address:", addr
	print "FileName:", fileName
	print "fileSize:", fileSize

def sequenceNumber():
	return str(sequence % pow(2, sequenceSize))

def nextSequenceNumber():
	global sequence
	sequence += 1

def checksum(checksum, data):
	sum = 0
	for iterator in data:
		sum += int(iterator, 16)
	if ((checksum + sum) & 0xff == 0):
		return True
	return False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udpIP, udpPORT))
sock.settimeout(3)

try:
	print "Ready For Client..."

	receiveStartTime = time.time()

	fileName, addr = sock.recvfrom(bufferSize)
	fileSize, addr = sock.recvfrom(bufferSize)
	sock.sendto("ACK", addr)

	fileSize = int(fileSize)
	printFileInfo(addr, fileName, fileSize)
	receiveFile = open(directoryPath + fileName, "wb")

	count = 1
	size = bufferSize
	while (size != fileSize + bufferSize):
		try:
			for i in range(count, windowSize):
				packet, addr = sock.recvfrom(bufferSize + headerSize)
				if (len(packet) < 1028):
					if (checksum(int(packet[1:4]), packet[4:len(packet)].encode("hex"))):
						dataTable[packet[0]] = packet[4:len(packet)]
                                                #print int(packet[1:4])
						break
					else:
						sock.sendto(packet[0], addr)
				else:
					packet = struct.unpack("1s3s1024s", packet[0:len(packet)])
					if (checksum(int(packet[1]), packet[2].encode("hex"))):
						dataTable[packet[0]] = packet[2]
						#print packet[1]
					else:
						sock.sendto(packet[0], addr)
		except socket.timeout:
			print "timeout"
			for i in range(0, windowSize - 1):
				if dataTable.get(str(i)) is None:
					sock.sendto(str(i), addr)
					packet, addr = sock.recvfrom(bufferSize + headerSize)
					packet = struct.unpack("1s3s1024s", packet[0:len(packet)])
					if (checksum(int(packet[1]), packet[2].encode("hex"))):
						dataTable[packet[0]] = packet[2]
					else:
						sock.sendto(packet[0], addr)

		for i in range(0, windowSize - 1):
			if (size > fileSize):
				receiveFile.write(dataTable.get(sequenceNumber()))
				size = fileSize
				printTransferRate(size, fileSize)
				size = size + bufferSize
				break
			receiveFile.write(dataTable.get(sequenceNumber()))
			dataTable[sequenceNumber()] = None
			nextSequenceNumber()
			printTransferRate(size,fileSize)
			size = size + bufferSize
		sock.sendto("ACK", addr)
		count = 1

	receiveEndTime = time.time() - receiveStartTime

	receiveFile.close()
	sock.close()
	print "Completed..."
	print "Time elapsed:", receiveEndTime

except socket.timeout:
	print "Not Connected..."
	sys.exit()
except socket.error as error:
	print error
	sys.exit()
