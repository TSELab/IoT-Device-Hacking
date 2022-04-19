import os, re
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

class FileTypes(Enum):
	UNKNOWN = -1
	FILE = 0
	DIR = 1
	LINK = 2

class NodeColors(Enum):
	UNTRACKED = "#ff834d"
	DIR = "#ffe859"
	LINK = "#ff40d6"
	CHANGED = "#26ffe5"
	TRACKED = "#8876ff"

class DirFile:
	def __init__(self, fname, ftype):
		self.packageName = ""
		self.name = fname
		self.fileType = ftype
		self.changed = False
		i = len(self.name) - 1
		while self.name[i] != "/" and i >= 0:
			i -= 1
		self.baseName = self.name[i + 1:]
	def __str__(self):
		return f"{self.name}: {self.fileType}, Package {self.packageName}"
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
	def BaseName(self):
		i = 8
		retStr = self.baseName
		while i < len(self.name):
			retStr = retStr[0 : i] + "\n" + retStr[i : ]
			i += 9
		return retStr
	def isChanged(self):
		return self.changed
	def setChanged(self):
		self.changed = True

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
				if linkPath[2] != "/" or linkPath == "./":
					return None
				# ../
				currPath = currPath[0 : findSlash(currPath[0 : -1], 1) + 1]
				linkPath = linkPath[3:]
			# ./
			elif linkPath[1] == "/":
				linkPath = linkPath[2 : 0]
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
		if self.linkDest == None:
			print(f"No link for {self.Name()}")
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
		if super().searchPath(path):
			return self
		for childFile in self.subDirs + self.subfiles + self.sublinks:
			result = None
			if childFile.Name() in path:
				result = childFile.searchPath(path)
				if not result:
					continue
				else:
					return result
		return None
	def findLink(self, root):
		for links in self.sublinks + self.subDirs:
			links.findLink(root)
	def subFiles(self):
		return self.subDirs + self.subfiles + self.sublinks
	def findMissing(self):
		untrackedNum = 0
		for files in self.subfiles + self.sublinks:
			if files.PackageName() == "":
				untrackedNum += 1
		if untrackedNum == len(self.subfiles + self.sublinks) and len(self.subfiles + self.sublinks) != 0:
			print(f"{untrackedNum} files and links in {self.Name()} untracked")
		elif untrackedNum > 0:
			for files in self.subfiles + self.sublinks:
				if files.PackageName() == "":
					print(f"File {files.Name()} untracked")
		for childDirs in self.subDirs:
			childDirs.findMissing()
	def fillGraph(self, G, baseNameDict, nodeColors):
		# Process links
		ulinkNum = 0
		for childLinks in self.sublinks:
			ulinkNum += 1
		if ulinkNum:
			G.add_node(f"ulink-{self.Name()}")
			G.add_edge(self.Name(), f"ulink-{self.Name()}")
			baseNameDict[f"ulink-{self.Name()}"] = f"{ulinkNum} links"
			nodeColors.append(NodeColors.LINK.value)

		#Process files
		trackedNum = 0
		untrackedNum = 0
		for childFiles in self.subfiles:
			if childFiles.PackageName() != "":
				trackedNum += 1
			else:
				untrackedNum += 1
		if trackedNum:
			G.add_node(f"tracked-{self.Name()}")
			G.add_edge(self.Name(), f"tracked-{self.Name()}")
			baseNameDict[f"tracked-{self.Name()}"] = f"{trackedNum} files\ntracked"
			nodeColors.append(NodeColors.TRACKED.value)
		if untrackedNum:
			G.add_node(f"untracked-{self.Name()}")
			G.add_edge(self.Name(), f"untracked-{self.Name()}")
			baseNameDict[f"untracked-{self.Name()}"] = f"{untrackedNum} files\nuntracked"
			nodeColors.append(NodeColors.UNTRACKED.value)

		#Process dir
		for childDirs in self.subDirs:
			G.add_node(childDirs.Name())
			G.add_edge(self.Name(), childDirs.Name())
			baseNameDict[childDirs.Name()] = childDirs.BaseName()
			nodeColors.append(NodeColors.DIR.value)
			childDirs.fillGraph(G, baseNameDict, nodeColors)

# log file format (generated by pbom.sh):
# @Package name
# file path
# file path...
def tagPackage(logFile, rootdir):
	pkgName = ""
	with open(logFile, "r") as logStream:
		for lines in logStream.readlines():
			lines = lines.strip("\n")
			if lines[0] == "@":
				pkgName = lines[1:]
			else:
				targetFile = rootdir.searchPath("." + lines)
				if targetFile == None:
					print(f"File .{lines} for package {pkgName} not found")
					continue
				if targetFile.PackageName() != "":
					print(f"{targetFile.Name()} already claimed by package {targetFile.PackageName()}, overriding to {pkgName}")
				targetFile.setPkg(pkgName)

root = DirTree(".", FileTypes.DIR)
root.findLink(root)
tagPackage("../test.txt", root)
root.findMissing()

plt.rcParams["figure.figsize"] = (150, 20)
G = nx.Graph()
G.add_node(root.Name())
baseNameDict = {root.Name() : root.BaseName()}
nodeColors = [NodeColors.DIR.value]
root.fillGraph(G, baseNameDict, nodeColors)
graphLayout = nx.nx_pydot.graphviz_layout(G, prog = "dot")
nx.draw_networkx(G, graphLayout, with_labels = False, node_color = nodeColors, node_size = 1000, node_shape = "o")
nx.draw_networkx_labels(G, graphLayout, labels = baseNameDict, verticalalignment = "top")

legend_elems = [Line2D([0], [0], color = "w", markerfacecolor = NodeColors.DIR.value, marker = "o", label = "Directories", markersize = 12),
		Line2D([0], [0], color = "w", markerfacecolor = NodeColors.UNTRACKED.value, marker = "o", label = "Untracked File", markersize = 12),
		Line2D([0], [0], color = "w", markerfacecolor = NodeColors.TRACKED.value, marker = "o", label = "Tracked File", markersize = 12),
		Line2D([0], [0], color = "w", markerfacecolor = NodeColors.LINK.value, marker = "o", label = "Links", markersize = 12),
		Line2D([0], [0], color = "w", markerfacecolor = NodeColors.CHANGED.value, marker = "o", label = "Changed Since Last Version", markersize = 12)]
plt.legend(handles = legend_elems)
plt.savefig("image.png", dpi = 220)
