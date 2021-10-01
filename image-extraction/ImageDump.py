from SerialInterface import SerialInterface
import re


def _is_image_line(line) -> bool:
    r = re.match(r"[0-9a-f]{8}(: )([0-9a-f]{2} ){1,16}   .{1,16}", line)
    return bool(r)


class ImageDump:
    def __init__(self, filename: str, dump_cmd: str, ser: SerialInterface):
        self.ser = ser
        self.filename = filename
        self.dump_cmd = dump_cmd
        self.stop_string = ser.prompt_text

    def set_filename(self, filename: str):
        self.filename = filename

    def run(self):
        file = open(self.filename, 'w')
        self.ser.flush()
        self.ser.write(self.dump_cmd)
        while True:
            line = self.ser.read_line()
            if line == self.stop_string:
                break
            else:
                if _is_image_line(line):
                    print(line)
                    file.write(line)
        file.close()

