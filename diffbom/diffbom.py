import os, fileTree, bomParser

os.chdir("root20190925")
root, metrics = fileTree.initDir(bomParser.opkg.readInfoDir("./usr/lib/opkg/info"))
print(metrics)