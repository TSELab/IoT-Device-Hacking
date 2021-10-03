from SerialInterface import SerialInterface
import re


def _is_image_line(line: str) -> bool:
    r = re.match(r"[0-9a-f]{8}(: )([0-9a-f]{2} ){1,16}   .{1,16}", line)
    return bool(r)


def _format_line(line: str) -> str:
    line = line[10:-20]
    line = line.replace(" ", "")
    line = line.replace('\n', '')
    line = line.replace('\r', '')
    return line


class ImageDump:
    def __init__(self, filename: str, dump_cmd: str, ser: SerialInterface):
        self.ser = ser
        self.filename = filename
        self.dump_cmd = dump_cmd
        self.stop_string = ser.prompt_text

    def set_filename(self, filename: str):
        self.filename = filename

    def run(self):
        file = open(self.filename, 'wb')
        self.ser.flush()
        self.ser.write(self.dump_cmd)
        while True:
            line = self.ser.read_line()
            if line == self.stop_string:
                break
            else:
                if _is_image_line(line):
                    temp = line[0:10]
                    line = _format_line(line)
                    print(temp + line)
                    file.write(line.encode('utf-8'))
        file.close()

