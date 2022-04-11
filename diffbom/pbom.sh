#!/bin/bash

if [ $# != 2 ]
then
	printf "Usage: pbom.sh <scanPath> <outputFile>\n"
	exit 1
fi

fpath=$1
outputFile=$2
printf "" > ${outputFile}

for ctrlFile in ${fpath}/*.control
do
	pkgPath=${ctrlFile%.*}
	pkgName=$(basename "${pkgPath}")
	printf "@"${pkgName}"\n" >> ${outputFile}
	cat ${pkgPath}.list >> ${outputFile}
done
