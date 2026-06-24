import io
import os
from PIL import Image
from .predict import Predict

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

word_path = os.path.join(CURRENT_PATH, "models", "geetest4_word_det_v1.onnx")
siamese_path = os.path.join(CURRENT_PATH, "models", "geetest4_word_siamese_v3.onnx")
for path in [siamese_path, word_path]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Error! 模型路径无效: '{path}'")
pre_word = Predict(per_path=siamese_path, yolo_path=word_path)

def transparence2white(img):
    img=Image.open(io.BytesIO(img))
    sp = img.size
    width = sp[0]
    height = sp[1]
    for yh in range(height):
        for xw in range(width):
            dot = (xw, yh)
            color_d = img.getpixel(dot)
            if color_d[3] == 0:
                color_d = (255, 255, 255, 255)
                img.putpixel(dot, color_d)
    return img

def get_word_position(captcha_img_data, icon_img_list):
    que_img_list = [transparence2white(icon) for icon in icon_img_list]
    captcha_img_data=Image.open(io.BytesIO(captcha_img_data))
    result = pre_word.run2(captcha_img_data, que_img_list)
    positions = []
    for point in result:
        center_x = (point[0] + point[2]) / 2
        center_y = (point[1] + point[3]) / 2
        positions.append([int(center_x), int(center_y)])
    return positions
