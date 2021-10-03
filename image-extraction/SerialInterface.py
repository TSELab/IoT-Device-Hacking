from typing import List, Optional
import serial


class SerialInterface:
    def __init__(self, port_name: str, prompt_text: str, baud_rate: int = 115200):
        self.ser = serial.Serial(port=port_name, baudrate=baud_rate)
        self.prompt_text = prompt_text

    def flush(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def write(self, string: str, encode: bool = True):
        if encode:
            string = string.encode('utf-8')
        self.ser.write(string)
        self.ser.write(b'\n')

    def read_line(self, decode: bool = True) -> str or bytes:
        done = False
        line = ''
        while not done:
            char = self.ser.read()
            if char == b'\n':
                return line
            else:
                if decode:
                    char = char.decode('utf-8')
                line += char
                if line == self.prompt_text:
                    return line

    def read_lines(self, count: int) -> List[str]:
        lines = []
        for i in range(count):
            lines.append(self.read_line())
        return lines
