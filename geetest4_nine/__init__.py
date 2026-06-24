
from io import BytesIO
import os
from PIL import Image
from .predict import NineClassify

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PLUGIN_NAME = "极验4九宫格识别"
PLUGIN_VERSION = "v2_fp16"
PLUGIN_LABEL = "geetest4_nine"


nine_model_path = os.path.join(CURRENT_PATH, "model", "geetest4_nine_v2_fp16.onnx")
ncls = NineClassify(nine_model_path)


def get_nine_position(que_data, imgs, nine_nums):
    positions = []
    p = {
        0: [1, 1],
        1: [1, 2],
        2: [1, 3],
        3: [2, 1],
        4: [2, 2],
        5: [2, 3],
        6: [3, 1],
        7: [3, 2],
        8: [3, 3],
    }
    que_data=Image.open(BytesIO(que_data))
    que_class = ncls.predict(que_data)["class"]
    result = ncls.predict_list(imgs)
    for item in result:
        if item.get("class") == que_class:
            index = item.get("index")
            positions.append(p[index])
    c = nine_nums - len(positions)
    if c > 0:
        result.sort(key=lambda x: x.get("confidence"))
        for item in result:
            if item.get("class") == que_class:
                continue
            positions.append(p[item.get("index")])
            if len(positions) >= nine_nums:
                break
    elif c < 0:
        positions = positions[:c]
    return positions, que_class


def get_images(positions, imgs):
    result = []
    for pos in positions:
        index = (pos[0] - 1) * 3 + (pos[1] - 1)
        result.append(Image.open(BytesIO(imgs[index])))
    return result


def update_matrix(matrix, index):
    """将最大值所在的行和列置为零"""
    matrix[index[0], :] = 0  # 将行置为零
    matrix[:, index[1]] = 0  # 将列置为零
    return matrix


def split_image(image_data):
    # 打开图像
    img = Image.open(BytesIO(image_data))
    # 获取图像的宽度和高度
    width, height = img.size
    # 计算每个小块的宽度和高度
    block_width = width // 3
    block_height = height // 3
    # 由于保存切割后的图片
    split_image_list = []

    # 切割图像为9份
    for i in range(3):
        for j in range(3):
            # 计算切割区域的坐标
            left = j * block_width
            top = i * block_height
            right = (j + 1) * block_width
            bottom = (i + 1) * block_height

            # 切割图像
            block = img.crop((left, top, right, bottom))
            # 调整图片大小
            block = block.resize((128, 128))
            data = BytesIO()
            block.save(data, format='PNG')
            split_image_list.append(data.getvalue())

    return split_image_list



# with open(r"C:\Users\Administrator\Desktop\1.jpg","rb") as f:
#     img_input=Image.open(BytesIO(f.read()))
# with open(r"C:\Users\Administrator\Desktop\2.png","rb") as f:
#     icon_input=f.read()
#
# # img_input=Image.open(r"C:\Users\Administrator\Desktop\1.jpg")
# # icon_input=Image.open(r"C:\Users\Administrator\Desktop\2.png")
#
#
# img_input = img_input.convert('RGBA')
#
# buf = BytesIO()
# img_input.save(buf, format="PNG")
#
# imgs = split_image(buf.getvalue())
#
# positions, que_class = get_nine_position(icon_input, imgs, 3)
