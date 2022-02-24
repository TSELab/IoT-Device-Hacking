# Dump image from a uboot instance.
# Adapted from SecurityJon/reliableubootdumper
import serial, time, os, sys

serialDev = "/dev/ttyUSB0"
baudRate = 115200
flashAddr = 0x2c000000
flashSz = 128 * 1024 * 1024 # 128MiB

dumpCmd = "md"
ttyPrompt = b"ath> "
perDumpLn = 16
perDumpLnSz = 16

tempFile = "temp.bin"
targetFile = "flash.bin"
targetTxt = "flash.txt"

ttyWidth = 80

def calcSleepTime():
	return perDumpLn * (11 + perDumpLnSz * 3) * 8 * 1.2 / baudRate

def dispProgress(currAddr):
	barLen = int(((currAddr - flashAddr) / flashSz) * (ttyWidth - 26))
	#                   [] 0x******** / 0x********, width = 23 + 3
	sys.stdout.write("\r[" + barLen * "-" +  (ttyWidth - 26 - barLen) * "." + "] " + \
	 f"{hex(currAddr)} / {hex(flashAddr + flashSz)}")
	sys.stdout.flush()

def mainReader():
	print("Stop the device at uboot terminal, then press any key to continue: ")
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

		for block in range(int(flashSz / perDumpLn / perDumpLnSz)):
			currAddr = flashAddr + block * perDumpLn * perDumpLnSz
			serialPort.write((dumpCmd + " " + hex(currAddr) + "\n").encode('utf-8'))
			time.sleep(sleepTime)
			responseStr = serialPort.readline() #first line is gonna be the command sent
			responseStr = serialPort.readline()
			numLine = 0
			while responseStr != ttyPrompt:
				filetxt.write(responseStr.decode('utf-8'))
				responseStr = serialPort.readline()
				numLine += 1
			if numLine != 16:
				raise ValueError(f"Got less than 16 ({numLine}) lines at {hex(currAddr)}")
			serialPort.reset_input_buffer()
			serialPort.reset_output_buffer()
			dispProgress(currAddr)
	except KeyboardInterrupt:
		serialPort.close()
		sys.exit()
	finally:
		serialPort.close()

with open(targetTxt, "w") as filetxt:
	mainReader()
os.system("./dump2Bin.sh")
