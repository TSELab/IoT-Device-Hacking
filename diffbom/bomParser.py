import os
#from spdx.parsers.parse_anything import parse_file 
# Returns None on failure, otherwise a dict
# {pkg1: [
#		{name: file1Name, sha1Sum: file1Sum}, 
#		{name: file2name, sha1Sum: file2Sum}...],
# pkg2:...}

def stripExt(fname):
	i = len(fname) - 1
	while i >= 0:
		if fname[i] == ".":
			break
		i -= 1
	return fname[:i]

def opkg(pkgPath):
	pkgDict = {}
	pkgList = []
	for files in os.listdir(pkgPath):
		if ".list" in files:
			pkgList.append(stripExt(files))
	for files in pkgList:
		with open(f"{pkgPath}/{files}.list", "r") as listFile:
			pkgDict[files] = listFile.readlines()
		pkgDict[files] = [{"name": fname.strip("\n"), "sha1Sum": None} for fname in pkgDict[files]]
	if not pkgDict:
		return None
	return pkgDict

def ipkg(pkgPath):
	pkgDict = dict()
	for files in os.listdir(pkgPath):
		with open(f"{pkgPath}/{files}") as f:
			flist = f.readlines()
		pkgDict[stripExt(files)] = [{"name": fname.strip("\n"), "sha1Sum": None} for fname in flist]
	if not pkgDict:
		return None
	return pkgDict


def spdx(bomFile):
	bomDoc, isfail = parse_file(bomFile)
	if isfail:
		return None
	bomDict = {}
	for package in bomDoc.packages:
		bomDict[package.name] = []
		for file in package.files:
			bomDict[package.name].append({"name": file.name, "sha1Sum": file.chk_sum.value})
	if not pkgDict:
		return None
	return pkgDict

def autoDetect():
	opkg_path = "./usr/lib/opkg/info"
	ipkg_path = "./usr/lib/ipkg/info"
	if os.path.exists(opkg_path):
		bomDict = opkg(opkg_path)
		if bomDict is not None:
			return bomDict
	if os.path.exists(ipkg_path):
		bomDict = ipkg(ipkg_path)
		if bomDict is not None:
			return bomDict
	return None

if __name__ == "__main__":
	print(autoDetect())
