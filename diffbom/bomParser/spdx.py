import sys
from spdx.parsers.parse_anything import parse_file 

# Returns None on failure, otherwise a dict
# {pkg1: [
#		{name: file1Name, sha1Sum: file1Sum}, 
#		{name: file2name, sha1Sum: file2Sum}...],
# pkg2:...}
def parseSpdx(bomFile):
	bomDoc, isfail = parse_file(bomFile)
	if isfail:
		return None
	bomDict = {}
	for package in bomDoc.packages:
		bomDict[package.name] = []
		for file in package.files:
			bomDict[package.name].append({"name": file.name, "sha1Sum": file.chk_sum.value})
	return bomDict
