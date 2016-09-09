import socket
import os
import sys
import time
import threading
import struct

if len(sys.argv) < 3:
	print "[Dst IP Addr] [Dst Port] [File Path]"
	sys.exit()

serverIP = sys.argv[1]
serverPORT = int(sys.argv[2])
filePath = sys.argv[3]
fileSize = os.path.getsize(filePath)
fileName = os.path.split(filePath)[1]

bufferSize = 1024
sequenceSize = 3
windowSize = (pow(2, sequenceSize) - 1)

sequence = 0
count = 0
readData = None
ack = None

dataTable = {}

def printTransferRate(size, fileSize):
	print "%d / %d (current/total size), %.2f%% " \
		% (size, fileSize, (float(size) / float(fileSize)) * 100)
	
def sequenceNumber():
	return str(sequence % pow(2, sequenceSize))

def nextSequenceNumber():
	global sequence
	sequence += 1

def calculateChecksum(data):
	sum = 0
	for iterator in data:
		sum += int(iterator, 16)
	checksum = 0xff - (sum & 0xff) + 1
	if (checksum < 10):
		checksum = "00" + str(checksum)
		#print checksum
		return checksum
	elif (checksum < 100):
		checksum = "0" + str(checksum)
		#print checksum
		return checksum
	else:
		#print checksum
		return str(checksum)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)	

try:
	print "Server Connected..."
	print "Server Address:", serverIP

	transmitStartTime = time.time()

	transmitFile = open(filePath, "rb")
	
	sock.sendto(str(fileName), (serverIP, serverPORT))
	sock.sendto(str(fileSize), (serverIP, serverPORT))
	ack, addr = sock.recvfrom(bufferSize)

	size = bufferSize
	for i in range(1, windowSize):
		readData = transmitFile.read(bufferSize)
		packet = sequenceNumber() \
			+ calculateChecksum(readData.encode("hex")) \
			+ readData
		sock.sendto(packet, (serverIP, serverPORT))
		dataTable[str(sequenceNumber())] = packet
		nextSequenceNumber()
		printTransferRate(size, fileSize)
		size = size + bufferSize

	while (size != fileSize + bufferSize):
		try:
			ack, addr = sock.recvfrom(bufferSize)
			if (ack == "ACK"):
				for i in range(1, windowSize):
					readData = transmitFile.read(bufferSize)
					packet = sequenceNumber() \
						+ calculateChecksum(readData.encode("hex")) \
						+ readData
					sock.sendto(packet, (serverIP, serverPORT))
					dataTable[str(sequenceNumber())] = packet
					if (size > fileSize):
						size = fileSize
						printTransferRate(size, fileSize)
						size = size + bufferSize
						break
					nextSequenceNumber()
					printTransferRate(size, fileSize)
					size = size + bufferSize
			else:
				sock.sendto(dataTable.get(ack), (serverIP, serverPORT))
		except socket.timeout:
			print "timeout"
			tempTable = dataTable.keys()
			for i in range(0, windowSize - 1):
				sock.sendto(dataTable[tempTable[i]], (serverIP, serverPORT))

	transmitEndTime = time.time() - transmitStartTime
	
	transmitFile.close()
	sock.close()
	print "Completed..."
	print "Time elapsed:", transmitEndTime

except socket.timeout:
	print "Not Connected..."
	sys.exit()
except socket.error as error:
	print error
	sys.exit()
