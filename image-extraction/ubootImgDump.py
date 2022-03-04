# Dump image from a uboot instance.
# Adapted from SecurityJon/reliableubootdumper
import serial, time, os, sys, re

# Serial device and flash configuration
serialDev = "/dev/ttyUSB0"
baudRate = 115200
flashAddr = 0x0
flashSz = 128 * 1024 * 1024 # 128MiB
perDumpLn = 128
perDumpLnSz = 16

# Dump command and return format
dumpCmd = "nand dump"
ttyPrompt = b'OOB:\r\n'
dataPattern = re.compile(r"[a-f0-9]{2}")
skipPattern = re.compile(r"")

# Output files
targetFile = "flash.bin"
targetTxt = "flash.txt"

# Debug options
outputToTTY = False
performLineNumCheck = True

# For progress bar
ttyWidth = 80
progUpdateInterval = 25000

def txt2bin():
	progSym = ["/", "|", "\\", "-", "|"]
	with open(inputFile, "r") as inputStream:
		with open(outputFile, "wb") as outputStream:
			line = inputStream.readline()
			byteArr = bytearray([])
			linNum = 0;
			while line != "":
				startIdx = skipPattern.search(line).span()[1]
				line = line[startIdx:]
				for match in re.finditer(dataPattern, line):
					byteArr.append(int(match.group(), 16))
				outputStream.write(byteArr)
				line = inputStream.readline()
				byteArr = bytearray([])

				sys.stdout.write("\rConverting txt to bin... " + progSym[int(linNum / progUpdateInterval) % len(progSym)])
				sys.stdout.flush()
				linNum += 1;

def calcSleepTime():
	return perDumpLn * (11 + perDumpLnSz * 3) * 8 * 1.2 / baudRate

def dispProgress(currAddr):
	barLen = int(((currAddr - flashAddr) / flashSz) * (ttyWidth - 26))
	#                   [] 0x******** / 0x********, width = 23 + 3
	sys.stdout.write("\r[" + barLen * "-" +  (ttyWidth - 26 - barLen) * "." + "] " + \
	 f"{currAddr:#0{10}x} / {(flashAddr + flashSz):#0{10}x}")
	sys.stdout.flush()

def mainReader():
	print("Stop the device at uboot terminal, then press any key to continue: ", end="")
	input()
	serialPort = serial.Serial(port = serialDev, baudrate = baudRate, timeout = 0.2)
	if not serialPort.isOpen():
		print("Cannot open serial connection. Exiting.")
		return;
	try:
		serialPort.reset_input_buffer()
		serialPort.reset_output_buffer()
		time.sleep(0.5)
		sleepTime = calcSleepTime()

		if not outputToTTY:
			dispProgress(flashAddr)
		for block in range(int(flashSz / perDumpLn / perDumpLnSz)):
			currAddr = flashAddr + block * perDumpLn * perDumpLnSz
			serialPort.write((dumpCmd + " " + hex(currAddr) + "\n").encode('utf-8'))
			time.sleep(sleepTime)
			responseStr = serialPort.readline() #first line is gonna be the command sent
			responseStr = serialPort.readline() #second line the prompt message
			responseStr = serialPort.readline() # this is what we want
			numLine = 0
			while responseStr != ttyPrompt:
				filetxt.write(responseStr.decode('utf-8'))
				if outputToTTY:
					print(responseStr)
				responseStr = serialPort.readline()
				numLine += 1
			if numLine != perDumpLn and performLineNumCheck:
				raise ValueError(f"Got less than {perDumpLn} ({numLine}) lines at {hex(currAddr)}")
			serialPort.reset_input_buffer()
			serialPort.reset_output_buffer()
			if not outputToTTY:
				dispProgress(currAddr)
	except KeyboardInterrupt:
		serialPort.close()
		filetxt.close()
		sys.exit()
	finally:
		dispProgress(flashAddr + flashSz)
		serialPort.close()

with open(targetTxt, "w") as filetxt:
	mainReader()
txt2bin()
