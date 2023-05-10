from maix import camera, image, display

import serial,struct

ser = serial.Serial("/dev/ttyS1",115200)


while True:
    img = camera.capture()
    ma = img.find_line()
    if ma:
        img.draw_line(ma['rect'][0], ma['rect'][1], ma['rect'][2], ma['rect'][3], (255,255,225), 1)
        img.draw_line(ma["rect"][2], ma["rect"][3], ma["rect"][4], ma["rect"][5], (255,255,225), 1)
        img.draw_line(ma["rect"][4], ma["rect"][5], ma["rect"][6], ma["rect"][7], (255,255,225), 1)
        img.draw_line(ma["rect"][6], ma["rect"][7], ma["rect"][0], ma["rect"][1], (255,255,225), 1)
        img.draw_circle(ma["cx"], ma["cy"], 2, (255,255,225), 1)
        data = int(float(ma["rotation"]*10))
        send_data = struct.pack("<BBhhh", 0x1c, 0x2c, ma["cx"], ma["cy"], data)
    ser.write(send_data)
    display.show(img)