import os, files

os.chdir("./root-20190925")
print("Version 20190925:")
root09 = files.initDir(".", "../ctrl-20190925.txt")
root09.findMissing()
#files.graphDir(root09, saveLoc = "../20190925.png")
print("\n")

os.chdir("../root-20191023")
print("Version 20191023:")
root10 = files.initDir(".", "../ctrl-20191023.txt")
root10.findMissing()
#files.graphDir(root10, saveLoc = "../20191023.png")
root10.tagChanged(root09)

trackedStat = root10.checkCoverage()
print(f"Overall {trackedStat}")
trackedStat = root10.searchPath("./bin").checkCoverage()
print(f"\t/bin {trackedStat}")
trackedStat = root10.searchPath("./etc").checkCoverage()
print(f"\t/etc {trackedStat}")
trackedStat = root10.searchPath("./home").checkCoverage()
print(f"\t/home {trackedStat}")
trackedStat = root10.searchPath("./lib").checkCoverage()
print(f"\t/lib {trackedStat}")
trackedStat = root10.searchPath("./root").checkCoverage()
print(f"\t/root {trackedStat}")
trackedStat = root10.searchPath("./sbin").checkCoverage()
print(f"\t/sbin {trackedStat}")
trackedStat = root10.searchPath("./usr").checkCoverage()
print(f"\t/usr {trackedStat}")
trackedStat = root10.searchPath("./www").checkCoverage()
print(f"\t/www {trackedStat}")