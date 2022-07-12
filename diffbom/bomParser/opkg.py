import os

def readInfoDir(pkgPath):
	pkgDict = {}
	pkgList = []
	for files in os.listdir(pkgPath):
		if ".control" in files:
			i = len(files) - 1
			while i >= 0:
				if files[i] == ".":
					break
				i -= 1
			pkgList.append(files[:i])
	for files in pkgList:
		with open(f"{pkgPath}/{files}.list", "r") as listFile:
			pkgDict[files] = listFile.readlines()
		pkgDict[files] = [{"name": fname.strip("\n"), "sha1Sum": None} for fname in pkgDict[files]]
	return pkgDict
