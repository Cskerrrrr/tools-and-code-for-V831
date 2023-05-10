import serial
import struct

ser = serial.Serial("/dev/ttyS0",115200)    # 连接串口

while True:
    send_data = struct.pack("<BhhbBB", 0x7B, 10, -10, -36, 120, 0x7D)
    ser.write(send_data)
    #B 0xFF----FF
    #h 100-----64 00 2位16进制
    #b -36-----DC    最低位16进制