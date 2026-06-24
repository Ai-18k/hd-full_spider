import io
import os

from PIL import Image

from .predict import Predict

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PLUGIN_NAME = "极验4图标点选识别"
PLUGIN_VERSION = "v1-3_fp16/s1_v2_fp16"
PLUGIN_LABEL = "geetest4_icon"

icon_path = os.path.join(CURRENT_PATH, "models", "geetest4_icon_det_v1.onnx")
siamese_path = os.path.join(CURRENT_PATH, "models", "geetest4_icon_siamese_v3_fp16.onnx")
siamese_pro_path = os.path.join(CURRENT_PATH, "models", "geetest4_icon_siamese_s1_v2_fp16.onnx")
for path in [siamese_path, icon_path]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Error! 模型路径无效: '{path}'")
pre_icon = Predict(per_path=siamese_path, yolo_path=icon_path)
pre_icon_pro = Predict(per_path=siamese_pro_path, yolo_path=icon_path)


def get_icon_position(captcha_img_data, icon_img_list, pro=True):
    captcha_img_data=Image.open(io.BytesIO(captcha_img_data))
    que_img_list = [transparence2white(icon) for icon in icon_img_list]
    if pro:
        result = pre_icon_pro.run2(captcha_img_data, que_img_list)
    else:
        result = pre_icon.run2(captcha_img_data, que_img_list)
    positions = []
    for point in result:
        center_x = (point[0] + point[2]) / 2
        center_y = (point[1] + point[3]) / 2
        positions.append([int(center_x), int(center_y)])
    return positions


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

