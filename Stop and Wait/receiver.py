import socket
import time
import sys

if len(sys.argv) < 2:
	print "[Port Number] [Directory Path]"
	sys.exit()

udpIP = ""
udpPORT = int(sys.argv[1])
directoryPath = sys.argv[2]
bufferSize = 1024
sequence = 0
count = 0
sequenceData = None
writeData = None

def printTransferRate(size, fileSize):
	print "%d / %d (current/total size), %.2f%%" \
		% (size, fileSize, (float(size) / float(fileSize)) * 100)

def printFileInfo(addr, fileName, fileSize):
	print "Client Address:", addr
	print "FileName:", fileName
	print "fileSize:", fileSize

def sequenceNumber():
	return str(sequence % 2)

def nextSequenceNumber():
	global sequence
	sequence += 1

def checkPreviousSequenceNumber():
	return (sequence - 1) % 2

def farEndReceiveFailure():
	print "Not Connected..."
	sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udpIP, udpPORT))
sock.settimeout(3)

try:
	print "Ready For Client..."

	receiveStartTime = time.time()

	fileName, addr = sock.recvfrom(bufferSize)
	sock.sendto("ACK", addr)
	fileSize, addr = sock.recvfrom(bufferSize)
	sock.sendto("ACK", addr)

	fileSize = int(fileSize)
	printFileInfo(addr, fileName, fileSize)
	receiveFile = open(directoryPath + fileName, "wb")

	size = bufferSize
	while (size != fileSize + bufferSize):
		try:
			sequenceData, addr = sock.recvfrom(bufferSize)
			writeData, addr = sock.recvfrom(bufferSize)

			if (sequenceData == sequenceNumber()):
				sock.sendto("ACK", addr)
			elif (sequenceData == checkPreviousSequenceNumber()):
				print "... Already received data"
				sock.sendto("ACK", addr)
				continue
			else:
				raise socket.timeout

		except socket.timeout:
			while (True):
				try:
					print "... Request the retransmission of missing data"
					sock.sendto(sequenceNumber(), addr)
					sequenceData, addr = sock.recvfrom(bufferSize)
					writeData, addr = sock.recvfrom(bufferSize)
					if (sequenceData == sequenceNumber()):
						sock.sendto("ACK", addr)
						count = 0
						break
					else:
						raise socket.timeout
				except socket.timeout:
					if (count == 5):
						farEndReceiveFailure()
					else:
						print "... timeout"
						count += 1

		finally:
			if (size > fileSize):
				size = fileSize
			printTransferRate(size, fileSize)
			receiveFile.write(writeData)
			size = size + bufferSize
			nextSequenceNumber()
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
