import os, sys, fileTree, bomParser
from config import silent, roots

if len(sys.argv) < 2:
	sys.stderr.write("Usage: python3 diffbom.py [Output File Name]\n")
	sys.exit(1)
csvName = sys.argv[1]

with open(csvName, "w") as csvFile:
	csvFile.write("version,multi-claimed,changed ELF,missing,unclaimed link,\
unclaimed ELF,unclaimed regular,total unclaimed,total files\n")
	for root in roots:
		if not silent:
			sys.stderr.write(f"Version {root}:\n")
		os.chdir(root)
		bomDict = bomParser.autoDetect()
		if bomDict is None:
			sys.stderr.write(f"No SBOM detected for {root}\n")
			os.chdir("../")
			continue
		rootTree, metrics = fileTree.initDir(bomDict)
		if not silent:
			rootTree.printUnclaimed()
		csvFile.write(f"{root},{str(metrics)[1:-1]}\n")
		os.chdir("../")
