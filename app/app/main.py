"""
实验名称：32串口通信
"""
import serial
import struct

ser = serial.Serial("/dev/ttyS0",115200)    # 连接串口

while True:
    send_data = struct.pack("<BhhbBB", 0x7B, 1001, -1111, -36, 120, 0x7D)
    ser.write(send_data)
    print("ok")
