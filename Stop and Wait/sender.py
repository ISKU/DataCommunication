import socket
import os
import sys
import time

if len(sys.argv) < 3:
	print "[Dst IP Addr] [Dst Port] [File Path]"
	sys.exit()

serverIP = sys.argv[1]
serverPORT = int(sys.argv[2])
filePath = sys.argv[3]
fileSize = os.path.getsize(filePath)
fileName = os.path.split(filePath)[1]
bufferSize = 1024
sequence = 0
count = 0
readData = None
ack = None


def printTransferRate(size, fileSize):
	print "%d / %d (current/total size), %.2f%% " \
		% (size, fileSize, (float(size) / float(fileSize)) * 100)
	
def sequenceNumber(): 
	return str(sequence % 2)

def nextSequenceNumber():
	global sequence
	sequence += 1

def transmissionFailure():
	print "Not Connected..."
	sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)	

try:
	print "Server Connected..."
	print "Server Address:", serverIP

	transmitStartTime = time.time()

	transmitFile = open(filePath, "rb")
	sock.sendto(str(fileName), (serverIP, serverPORT))
	ack, addr = sock.recvfrom(bufferSize)
	sock.sendto(str(fileSize), (serverIP, serverPORT))
	ack, addr = sock.recvfrom(bufferSize)

	size = bufferSize
	while (size != fileSize + bufferSize):
		readData = transmitFile.read(bufferSize)

		sock.sendto(sequenceNumber(), (serverIP, serverPORT))
		sock.sendto(readData, (serverIP, serverPORT))
		while (True):
			try:
				ack, addr = sock.recvfrom(bufferSize)
				if (ack == sequenceNumber()):
					raise socket.timeout
				else:
					count = 0
					break
			except socket.timeout:
				print "... Negative Acknowledge, Retransmits missing data"
				sock.sendto(sequenceNumber(), (serverIP, serverPORT))
				sock.sendto(readData, (serverIP, serverPORT))
				if (count == 5):
					transmissionFailure()
				else:
					count += 1

		if (size > fileSize):
			size = fileSize
		printTransferRate(size, fileSize)
		size = size + bufferSize
		nextSequenceNumber()
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
