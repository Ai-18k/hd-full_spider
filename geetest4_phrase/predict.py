import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='jieba')
import os
import cv2
import math
import itertools
from concurrent.futures import ThreadPoolExecutor
os.environ["YOLO_VERBOSE"] = "False"
from ultralytics import YOLO


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
classify_path = os.path.join(CURRENT_PATH, "models", "classify.onnx")
detect_path = os.path.join(CURRENT_PATH, "models", "detect.onnx")
dict_mini_path = os.path.join(CURRENT_PATH, "models", "dict_mini.txt")


class ImprovedLMSolver:
    def __init__(self, dict_path='dict_mini.txt'):
        self.word_dict = {}

        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.split()
                    if not parts:
                        continue
                    word = parts[0]

                    try:
                        freq = int(parts[2])
                    except:
                        freq = 1

                    if freq <= 0:
                        freq = 1

                    self.word_dict[word] = freq

        except Exception as e:
            print(f"词库加载失败: {e}")

        # =====================================================
        # strong_phrases（不变）
        # =====================================================
        self.strong_phrases = {
            "具备下列条件",
            "丰富的维生素",
            "社会经济发展",
            "主要营养成分",
            "自主研发的",
            "学术带头人",
            "象征着",
            "几千年",
            "电影上映时间",
            "教育示范学校",
            "全球范围内",
            "主要表现在",
            "发表论文",
            "辽宁省沈阳",
            "优秀作品奖",
            "发明了",
            "成千上万的",
            "多数情况下",
            "优质的服务",
            "中国戏",
            "作品名",
            "中国现代文学",
            "在古代",
            "影响深远的",
            "急数措施",
            "绝大多数",
            "质量认证体系",
        }

        # =====================================================
        # 只用前三个字做触发
        # =====================================================
        self.trigger_prefix = set()
        for item in self.strong_phrases:
            self.trigger_prefix.add(item[0:2])

    def score(self, text):

        total_score = 0
        n = len(text)

        # =====================================================
        # 原始子串评分（不动）
        # =====================================================
        for i in range(n):
            for j in range(i + 1, n + 1):
                sub_word = text[i:j]
                if sub_word in self.word_dict:
                    freq = self.word_dict[sub_word]
                    length = len(sub_word)
                    total_score += (length ** 2) * math.log(freq + 1)


        # =====================================================
        # 只用前三个字判断是否使用 jieba
        # =====================================================
        need_jieba = False

        if len(text) >= 2:
            prefix = text[:2]
            if prefix in self.trigger_prefix:
                need_jieba = True

        # =====================================================
        # 只有触发才使用 jieba
        # =====================================================
        if need_jieba:
            import jieba
            # 关闭 jieba 日志
            jieba.setLogLevel(20)
            words = jieba.lcut(text)
            joined = ''.join(words)

            for phrase in self.strong_phrases:
                if phrase == joined:
                    total_score += 1000000
                elif phrase in joined:
                    total_score += 500000

        return total_score

    def solve(self, chars):

        best_text = None
        best_score = -1e9
        best_perm = None

        for perm in itertools.permutations(range(len(chars))):

            text = ''.join(chars[i] for i in perm)
            s = self.score(text)

            if s > best_score:
                best_score = s
                best_text = text
                best_perm = list(perm)

        return best_text, best_perm


# =========================================================
# 加载模型
# =========================================================
detect_model = YOLO(
    detect_path,
    task="detect",
)

classify_model = YOLO(
    classify_path,
    task="classify"
)

solver = ImprovedLMSolver(dict_mini_path)


# =========================================================
# 单字符分类
# =========================================================
def classify_single(args):
    crop, box, device = args

    cls_results = classify_model(
        crop,
        device=device,
        verbose=False
    )

    probs = cls_results[0].probs

    cls_id = probs.top1
    word = cls_results[0].names[cls_id]
    conf = probs.top1conf.item()

    x1, y1, x2, y2 = box

    return {
        "word": word,
        "conf": conf,
        "box": [x1, y1, x2, y2],
        "x": x1
    }


# =========================================================
# 主识别函数
# =========================================================
def recognize_text(
        img_input,
        detect_conf=0.25,
        classify_size=64,
        device="cpu",
        max_workers=4,
        use_lm_sort=True
):
    """识别图片中的文字（语序点选）
    
    Args:
        img_input: 图片路径(str) 或 bytes 或 numpy ndarray (BGR)
    """
    if isinstance(img_input, str):
        img = cv2.imread(img_input)
    elif isinstance(img_input, bytes):
        import numpy as np
        nparr = np.frombuffer(img_input, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        # 假设已经是 numpy ndarray
        img = img_input

    if img is None:
        raise ValueError(f"图片读取失败: {str(img_input)[:100]}")

    detect_results = detect_model(
        img,
        device=device,
        verbose=False,
        conf=detect_conf,
        imgsz=640
    )

    boxes = detect_results[0].boxes
    tasks = []

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(img.shape[1], x2)
        y2 = min(img.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            continue
        crop = img[y1:y2, x1:x2]
        crop = cv2.resize(
            crop,
            (classify_size, classify_size),
            interpolation=cv2.INTER_NEAREST
        )
        tasks.append((crop, (x1, y1, x2, y2), device))

    if not tasks:
        return {
            "raw_text": "",
            "final_text": "",
            "details": [],
            "perm": []
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(classify_single, tasks))

    results.sort(key=lambda x: x["x"])

    raw_chars = [item["word"] for item in results]
    raw_text = ''.join(raw_chars)

    final_text = raw_text
    best_perm = list(range(len(results)))

    if use_lm_sort and len(raw_chars) > 1:
        try:
            final_text, best_perm = solver.solve(raw_chars)
        except Exception as e:
            print("LM排序失败:", e)

    sorted_results = [results[i] for i in best_perm]

    for item in sorted_results:
        del item["x"]

    return {
        "raw_text": raw_text,
        "final_text": final_text,
        "details": sorted_results,
        "perm": best_perm
    }


# =========================================================
# 获取信息
# =========================================================
def get_info(img_input):
    """获取语序点选识别结果
    
    Args:
        img_input: 图片路径(str) 或 图片bytes数据 或 numpy ndarray
        
    Returns:
        list: 排序后的文字框坐标列表 [[x1,y1,x2,y2], ...]
    """
    result = recognize_text(
        img_input,
        device="cpu",
        max_workers=5,
        use_lm_sort=True
    )
    info = []
    for item in result["details"]:
        info.append(item['box'])
    return info



# if __name__ == "__main__":
#     img_path = r"imgs\2.jpg"
#
#     res = get_info(img_path)
#     logger.info(res)

