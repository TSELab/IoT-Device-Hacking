import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 4:
	sys.stderr.write("Usage: visualizer.py [Input csv] [Output figure 1] [Output figure 2]\n")
csvFile = sys.argv[1]
rawData = pd.read_csv(csvFile)
missing = rawData[["missing"]].to_numpy().T[0]

unclaimed_link = rawData[["unclaimed link"]].to_numpy().T[0]
unclaimed_elf = rawData[["unclaimed ELF"]].to_numpy().T[0]
unclaimed_reg = rawData[["unclaimed regular"]].to_numpy().T[0]
unclaimed = rawData[["total unclaimed"]].to_numpy().T[0]

totFiles = rawData[["total files"]].to_numpy().T[0]

unclaimed_rate = unclaimed / totFiles
missing_rate = missing / (totFiles - unclaimed + missing)

fig, ax = plt.subplots()
x = [i for i in range(len(totFiles))]
ax.set_xlabel("Version")
ax.plot(x, unclaimed_rate, color="blue", label="Unclaimed Rate")
ax.plot(x, missing_rate, color="red", label = "Missing Rate")
plt.legend()
plt.savefig(sys.argv[2])

fig, ax = plt.subplots()
ax.set_xlabel("Version")
ax.set_ylabel("Number of Files")
ax.stackplot(x, unclaimed_link, unclaimed_elf, unclaimed_reg, totFiles - unclaimed, missing, 
	labels=["Unclaimed Link", "Unclaimed ELF", "Unclaimed Regular", "Total Present", "Missing"])
plt.legend()
plt.savefig(sys.argv[3])
