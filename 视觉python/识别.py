# generated by maixhub, tested on maixpy3 v0.4.8
from maix import nn, camera, display, image

import serial,struct

global send_data


input_size = (224, 224)
model = "model-5984.awnn.mud"
labels = ['2', '3', '4', '5', '6', '1']
anchors = [4.34, 5.47, 4.56, 5.69, 4.91, 6.06, 4.75, 5.88, 4.62, 6.0]

ser = serial.Serial("/dev/ttyS1",115200)

class YOLOv2:
    def __init__(self, model_path, labels, anchors, net_in_size, net_out_size):
        self.labels = labels
        self.anchors = anchors
        self.net_in_size = net_in_size
        self.net_out_size = net_out_size
        print("-- load model:", model)
        self.model = nn.load(model_path)
        print("-- load ok")
        print("-- init yolo2 decoder")
        self._decoder = nn.decoder.Yolo2(len(labels), anchors, net_in_size=net_in_size, net_out_size=net_out_size)
        print("-- init complete")

    def run(self, img, nms=0.3, threshold=0.5):
        out = self.model.forward(img, layout="hwc")
        boxes, probs = self._decoder.run(out, nms=nms, threshold=threshold, img_size=input_size)
        return boxes, probs

    def draw(self, img, boxes, probs):
        global send_data
        for i, box in enumerate(boxes):
            class_id = probs[i][0]
            prob = probs[i][1][class_id]
            msg = "{}:{:.2f}%".format(self.labels[class_id], prob*100)
            if   self.labels[class_id] == '1':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x01)
                 ser.write(send_data)
            if   self.labels[class_id] == '2':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x02)
                 ser.write(send_data)
            if   self.labels[class_id] == '3':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x03)
                 ser.write(send_data)
            if   self.labels[class_id] == '4':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x04)
                 ser.write(send_data)
            if   self.labels[class_id] == '5':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x05)
                 ser.write(send_data)
            if   self.labels[class_id] == '6':
                 send_data = struct.pack("<BBB", 0x1c, 0x2c,0x06)
                 ser.write(send_data)
            img.draw_rectangle(box[0], box[1], box[0] + box[2], box[1] + box[3], color=(255, 255, 255), thickness=2)
            img.draw_string(box[0] + 2, box[1] + 2, msg, scale = 1.2, color = (255, 255, 255), thickness = 2)

def main():
    camera.config(size=input_size)
    yolov2 = YOLOv2(model, labels, anchors, input_size, (input_size[0] // 32, input_size[1] // 32))
    while True:
        img = camera.capture()
        boxes, probs = yolov2.run(img, nms=0.3, threshold=0.5)
        yolov2.draw(img, boxes, probs)
        display.show(img)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback, time
        msg = traceback.format_exc()
        print(msg)
        img = image.new(size = (240, 240), color = (255, 0, 0), mode = "RGB")
        img.draw_string(0, 0, msg, scale = 0.8, color = (255, 255, 255), thickness = 1)
        display.show(img)
        time.sleep(20)
