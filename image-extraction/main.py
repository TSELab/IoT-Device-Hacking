# script to dump the software image of the philips hue multiple times to multiple files


from SerialInterface import SerialInterface
from ImageDump import ImageDump


def dump_image():
    run_count = 3

    port = "COM5"
    filename = "img"
    prompt_text = "ath> "
    cmd = "md.b 0x0 0x0000ffff"
    ser = SerialInterface(port, prompt_text)
    imgDmp = ImageDump(filename, cmd, ser)
    for i in range(run_count):
        imgDmp.set_filename(filename + "_" + str(i + 1) + ".txt")
        imgDmp.run()


if __name__ == '__main__':
    dump_image()
