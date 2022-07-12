import os, files, bomParser

os.chdir("RAX120/RAX120-root")
root = files.initDir(".", bomParser.opkg.readInfoDir())
root.findMissing()
print(root.checkCoverage())