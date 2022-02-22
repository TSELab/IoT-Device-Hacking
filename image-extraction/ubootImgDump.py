# Dump image from a uboot instance.
# Adapted from SecurityJon/reliableubootdumper
import serial, time, os, sys

serialDev = "/dev/ttyUSB0"
baudRate = 115200
flashAddr = 0x2c000000
flashSz = 128 * 1024 * 1024 # 128MiB

dumpCmd = "md"
perDumpSz = 16 * 16

# Use xxd and dd to create. Check with binwalk.
tempFile = "temp.bin"
targetFile = "flash.bin"
targetTxt = "flash.txt"

def writeToFile(string):
	filetxt.write(string.decode('utf-8'))

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

		for block in range(int(flashSz / perDumpSz)):
			serialPort.write((dumpCmd + " " + hex(flashAddr + block * perDumpSz) + "\n").encode('utf-8'))
			time.sleep(0.5)
			responseStr = serialPort.readline() #first line is gonna be the command sent
			responseStr = serialPort.readline()
			numLine = 0
			while responseStr != b'ath> ':
				writeToFile(responseStr)
				responseStr = serialPort.readline()
				numLine += 1
			if numLine != 16:
				raise ValueError(f"Got less than 16 ({numLine}) lines at {hex(flashAddr + perDumpSz * block)}")
			serialPort.reset_input_buffer()
			serialPort.reset_output_buffer()
			print(f"Read flash image at address {hex(flashAddr + perDumpSz * block)}")
	except KeyboardInterrupt:
		serialPort.close()
		sys.exit()
	finally:
		serialPort.close()

filetxt = open(targetTxt, "w")
mainReader()
os.system("./dump2Bin.sh")
