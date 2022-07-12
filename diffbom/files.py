import os, re, hashlib
from enum import Enum

excludeList = ["./usr/lib/opkg", "./dev", "./proc", "./sys", "./tmp"]
silent = False

class FileTypes(Enum):
	UNKNOWN = -1
	FILE = 0
	DIR = 1
	LINK = 2

class DirFile:
	def __getHash(self):
		if self.fileType == FileTypes.FILE:
			# cr: Randall Hunt @ stackoverflow
			BUFSIZE = 65536
			self.sha1 = hashlib.sha1()
			with open(self.name, "rb") as f:
				data = f.read(BUFSIZE)
				while data:
					self.sha1.update(data)
					data = f.read(BUFSIZE)
	def __getType(self):
		if self.fileType == FileTypes.FILE:
			with open(self.name, "rb") as f:
				magic = f.read(4)
				if magic == bytearray([0x7f, ord('E'), ord('L'), ord('F')]):
					self.fSubType = "ELF"
				else:
					self.fSubType = "Regular"

	def __init__(self, fname, ftype):
		self.packageName = ""
		self.name = fname
		self.fileType = ftype
		self.__getHash()
		self.__getType()
	def __str__(self):
		return f"{self.name}: {self.fileType}, Package {self.packageName};"
	def __repr__(self):
		return self.__str__()
	def searchPath(self, path):
		if path == self.name:
			return self
		return None
	def setPkg(self, pkgName):
		self.packageName = pkgName
	def Name(self):
		return self.name
	def PackageName(self):
		return self.packageName
	def FileType(self):
		return self.fileType
	def SubType(self):
		return self.fSubType

def findSlash(loc, direction):
	if direction == 0:
		i = 0
		while i < len(loc) and loc[i] != "/":
			i += 1
		return i
	else:
		i = len(loc) - 1
		while i >= 0 and loc[i] != "/":
			i -= 1
		return i

def getAbsPath(linkLoc, linkPath):
	if linkPath[0] == "/":
		return "." + linkPath
	currPath = linkLoc[0 : findSlash(linkLoc, 1) + 1]
	while linkPath != "":
		if linkPath[0] == ".":
			if linkPath[1] == ".":
				if linkPath[2] != "/":
					return None
				# ../
				currPath = currPath[0 : findSlash(currPath[0 : -1], 1) + 1]
				linkPath = linkPath[3:]
			# ./
			elif linkPath[1] == "/":
				linkPath = linkPath[2:]
		else:
			currPath += linkPath
			return currPath
	return None

class DirLinks(DirFile):
	def __init__(self, fname, ftype):
		super().__init__(fname, ftype)
		self.linkPath = getAbsPath(self.Name(), os.readlink(self.Name()))
		self.linkDest = None
	def findLink(self, root):
		self.linkDest = root.searchPath(self.linkPath)
	def searchPath(self, path):
		if super().searchPath(path):
			return self
		if self.linkDest == None:
			return None
		return self.linkDest.searchPath(path.replace(self.name, self.linkPath))

class DirTree(DirFile):
	def __init__(self, fname, ftype):
		self.subDirs = []
		self.subfiles = []
		self.sublinks = []
		super().__init__(fname, ftype)
		for files in os.listdir(fname):
			if os.path.islink(f"{fname}/{files}"):
				self.sublinks.append(DirLinks(f"{fname}/{files}", FileTypes.LINK))
			elif os.path.isdir(f"{fname}/{files}"):
				self.subDirs.append(DirTree(f"{fname}/{files}", FileTypes.DIR))
			elif os.path.isfile(f"{fname}/{files}"):
				self.subfiles.append(DirFile(f"{fname}/{files}", FileTypes.FILE))
			else:
				self.subfiles.append(DirFile(f"{fname}/{files}", FileTypes.UNKNOWN))
	def searchPath(self, path):
		if path == self.Name():
			return self
		for childFile in self.subDirs + self.subfiles + self.sublinks:
			if childFile.Name() in path:
				result = childFile.searchPath(path)
				if result:
					return result
		return None
	def findLink(self, root):
		for links in self.sublinks + self.subDirs:
			links.findLink(root)
	def subFiles(self):
		return self.subDirs + self.subfiles + self.sublinks
	def findMissing(self):
		if self.name not in excludeList:
			untrackedNum = 0
			for files in self.subfiles + self.sublinks:
				if files.PackageName() == "":
					untrackedNum += 1
			# All files untracked
			if untrackedNum == len(self.subfiles + self.sublinks) and len(self.subfiles + self.sublinks) != 0:
				if not silent:
					print(f"{untrackedNum} files and links in {self.Name()} untracked")
			# Some files untracked
			elif untrackedNum > 0:
				for files in self.subfiles + self.sublinks:
					if files.PackageName() == "":
						if not silent:
							print(f"File {files.Name()} untracked")
			for childDirs in self.subDirs:
				childDirs.findMissing()
	def checkCoverage(self):
		if self.name in excludeList:
			return 0, 0, 0, 0, 0
		totUntracked = 0
		totULinks = 0
		totUELFs = 0
		totUFiles = 0
		totalFiles = len(self.subfiles + self.sublinks)
		for childFiles in self.subfiles + self.sublinks:
			if childFiles.PackageName() == "":
				totUntracked += 1
				if childFiles.FileType() == FileTypes.LINK:
					totULinks += 1
				elif childFiles.SubType() == "ELF":
					totUELFs += 1
				else:
					totUFiles += 1
		for childDirs in self.subDirs:
			ulinks, uelfs, ufiles, untracked, tot = childDirs.checkCoverage()
			totULinks += ulinks
			totUELFs += uelfs
			totUFiles += ufiles
			totUntracked += untracked
			totalFiles += tot
		return totULinks, totUELFs, totUFiles, totUntracked, totalFiles

def tagPackage(logDict, rootdir):
	num404 = 0
	numDual = 0
	for pkgName in logDict.keys():
		for lines in logDict[pkgName]:
			lines = lines.strip("\n")
			if lines[-1] == "/":
				lines = lines[:-1]
			targetFile = rootdir.searchPath("." + lines)
			if targetFile == None:
				num404 += 1
				if not silent:
					print(f"File .{lines} for package {pkgName} not found")
				continue
			if targetFile.PackageName() != "":
				numDual += 1
				if not silent:
					print(f"{targetFile.Name()} already claimed by package {targetFile.PackageName()}, overriding to {pkgName}")
			targetFile.setPkg(pkgName)
	return num404, numDual

# pkgFileDict["pkgName"] = ["list", "of", "files"]
def initDir(dirPath, pkgFileDict):
	root = DirTree(dirPath, FileTypes.DIR)
	root.findLink(root)
	print(tagPackage(pkgFileDict, root))
	return root
