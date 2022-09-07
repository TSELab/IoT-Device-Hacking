import os, fileTree, bomParser

print("multi-claimed, changed ELF, missing, unclaimed link, \
 unclaimed ELF, unclaimed regular, total unclaimed, total files")

os.chdir("root20190925")
root, metrics = fileTree.initDir(bomParser.opkg.readInfoDir("./usr/lib/opkg/info"))
print(metrics)