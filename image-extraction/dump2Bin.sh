!#/bin/bash

tempFile="temp.bin"
targetFile="flash.bin"
targetTxt="flash.txt"
flashAddr="0x2c000000"

xxd -r ${targetTxt} ${tempFile}
dd if=${tempFile} of=${targetFile} bs=1 skip=${flashAddr}
rm -f ${tempFile}
