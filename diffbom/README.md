DiffBOM 
====

A tool for determining SBOM coverage of IoT file systems and docker images. WIP paper describing this tool is available at zhiruih/diffbom-paper.

# How to use

dockerConn pulls docker images from Docker Hub and extract into a file system. First initialize with dockerConn.initDocker(), then extract with dockerConn.pullXtractImage(imgName, saveDirName).

bomParser parses SBOMs. Currently supports SPDX and opkg/dpkg metadata.
- To parse SPDX, use bomParser.spdx.parseSpdx(spdxFileLoc_str) 
- To parse opkg metadata, use bomParser.opkg.readInfoDir(metadataDir_str)

fileTree constructs DirTree object representing file system hierarchy and compare it to SBOM information. initDir(sbomDict) takes parsed SBOM info generated by bomParser, generates DirTree **with / assumed at shell's current directory** and do comparison. It returns the object and a tuple of 8 integers, each are the number of:
- multi-claimed file
- changed ELF
- missing file
- unclaimed link
- unclaimed ELF
- unclaimed regular
- total unclaimed
- total file
DirTree.printUnclaimed() prints path to all unclaimed file to stderr. silent must be False to take effect.

Configurations are stored in config.py, available configurations are
- excludeList: a list containing directories to be ignored in comparison. These typically contains tmpfs directories such as /dev/ or /proc/. No trailing / should be included due to limitation of tool. 
- silent: a boolean dictating if missing files should be outputted to terminal.
- roots: a list of root directory names to go through

diffbom is a sample implementation of all functions. It takes all configurations in config.py and outputs in csv format. Use by doing `python3 diffbom.py [Output File Name]`.

visualizer plots data in two formats: line plot and stacked plot. The line plot draws unclaimed & missing rate, while the stacked plot shows how many of each type of file exists. Use by doing `visualizer.py [Input csv] [Output figure 1] [Output figure 2]`.
