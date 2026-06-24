from loguru import logger
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256, md5, sha1
import requests
import random
import binascii
import json
import time
import re
from captcha_recognizer.slider import Slider

class Spider(object):
    def __init__(self):
        self.href = "https://static.geetest.com/"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://www.geetest.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.count = 0
        self.count2 = 0

    # 随机16位字符串
    def get_random_str(self):
        def e():
            return hex(int(65536 * (1 + random.random())) | 0)[2:][1:]

        return e() + e() + e() + e()

    # 第一次请求获取信息
    def init_req(self):
        cookies = {
            "Hm_lvt_25b04a5e7a64668b9b88e2711fb5f0c4": "1782116502",
            "HMACCOUNT": "898C7941C8D2F0E5",
            "sajssdk_2015_cross_new_user": "1",
            "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%2219eee6bca0a2214-08c937d5dc2e5a8-26061151-1338645-19eee6bca0b1c23%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Fbaidu.php%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.geetest.com%2F%3Futm_campaign%3D%E7%99%BE%E5%BA%A6SEM%26utm_source%3Dbaidu%26utm_medium%3Dcpc%26utm_term%3D%E6%9E%81%E9%AA%8C%26utm_content%3D%E5%93%81%E7%89%8C%E8%AF%8D%E7%B3%BB%E5%88%97%26_channel_track_key%3DqXBWd7ZK%26bd_vid%3D9256518005686371993%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22cpc%22%2C%22%24latest_utm_campaign%22%3A%22%E7%99%BE%E5%BA%A6SEM%22%2C%22%24latest_utm_content%22%3A%22%E5%93%81%E7%89%8C%E8%AF%8D%E7%B3%BB%E5%88%97%22%2C%22%24latest_utm_term%22%3A%22%E6%9E%81%E9%AA%8C%22%7D%2C%22%24device_id%22%3A%2219eee6bca0a2214-08c937d5dc2e5a8-26061151-1338645-19eee6bca0b1c23%22%7D",
            "language": "zh",
            "Hm_lpvt_25b04a5e7a64668b9b88e2711fb5f0c4": "1782116550"
        }
        url = "https://gt4.geetest.com/"
        response = requests.get(url, headers=self.headers, cookies=cookies)
        id_ = re.compile('index\.(.*?)\.js', re.S).findall(response.text)[0]

        url = f"https://gt4.geetest.com/assets/index.{id_}.js"
        response = requests.get(url, headers=self.headers)
        self.captchaId = re.compile('captchaId:"(.*?)"', re.S).findall(response.text)[0]

        url = "https://gcaptcha4.geetest.com/load"
        params = {
            "callback": f"geetest_{str(int(time.time() * 1000))}",
            "captcha_id": self.captchaId,
            "challenge": "172dd5aa-1d1d-4f1c-9c43-29ac88b663b5",
            "client_type": "web",
            "risk_type": "slide",
            "lang": "zh"
        }
        response = requests.get(url, headers=self.headers, params=params)
        data = json.loads(response.text[22:-1])['data']
        # self.static_path = "https://static.geetest.com" + data["static_path"] + data['js']
        self.lot_number = data["lot_number"]
        self.payload = data["payload"]
        self.process_token = data["process_token"]
        self.payload_protocol = data["payload_protocol"]
        self.pt = data["pt"]
        bg = self.href + data["bg"]
        self.version = data["pow_detail"]["version"]
        self.bits = str(data["pow_detail"]["bits"])
        self.datetime = data["pow_detail"]["datetime"]
        self.hashfunc = data["pow_detail"]["hashfunc"]

        img_res = requests.get(bg)
        box = Slider().identify(source=img_res.content, show=False)
        self.distance = int(box[0][0]) - 15

        self.RSA()

    # rsa加密
    def RSA(self):
        # 公钥参数
        n_hex = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
        e_hex = "10001"

        n = int(n_hex, 16)
        e = int(e_hex, 16)

        # 生成 RSA 公钥对象
        pub_key = RSA.construct((n, e))

        # 明文
        random_str = self.get_random_str()
        # random_str = "dd2671f233352236"
        plaintext = random_str.encode("utf-8")

        # PKCS#1 v1.5 加密
        cipher = PKCS1_v1_5.new(pub_key)
        encrypted = cipher.encrypt(plaintext)

        # 输出和 JS 类似的小写十六进制
        self.rsa_result = binascii.hexlify(encrypted).decode("utf-8")
        self.AES(random_str)

    # 获取 pow_sign
    def get_pow_sign(self, pow_msg_left):
        bits = int(self.bits)
        a = bits % 4
        zero_len = bits // 4
        u = "0" * zero_len

        while True:
            h = self.get_random_str()
            pow_msg = pow_msg_left + h

            if self.hashfunc == "md5":
                pow_sign = md5(pow_msg.encode("utf-8")).hexdigest()
            elif self.hashfunc == "sha1":
                pow_sign = sha1(pow_msg.encode("utf-8")).hexdigest()
            elif self.hashfunc == "sha256":
                pow_sign = sha256(pow_msg.encode("utf-8")).hexdigest()
            else:
                logger.warning(f"pow_sign加密方法: {self.hashfunc}")
                continue

            if a == 0:
                if pow_sign.startswith(u):
                    return pow_msg, pow_sign
            else:
                if pow_sign.startswith(u):
                    d = pow_sign[zero_len]

                    if a == 1:
                        f = 7
                    elif a == 2:
                        f = 3
                    elif a == 3:
                        f = 1
                    else:
                        continue

                    if int(d, 16) <= f:
                        return pow_msg, pow_sign

    # aes加密
    def AES(self, random_str):
        pow_msg_left = self.version + "|" + self.bits + "|" + self.hashfunc + "|" + self.datetime + "|" + self.captchaId + "|" + self.lot_number + "||"
        pow_msg, pow_sign = self.get_pow_sign(pow_msg_left)

        arg = {
            "setLeft": self.distance,
            "passtime": random.randint(500, 1000),
            "userresponse": self.distance / 1.0059466666666665 + 2,
            "device_id": "",
            "lot_number": self.lot_number,
            "pow_msg": pow_msg,
            "pow_sign": pow_sign,
            "geetest": "captcha",
            "lang": "zh",
            "ep": "123",
            "biht": "1426265548",
            "gee_guard": {
                "roe": {
                    "aup": "3",
                    "sep": "3",
                    "egp": "3",
                    "auh": "3",
                    "rew": "3",
                    "snh": "3",
                    "res": "3",
                    "cdc": "3"
                }
            },
            "ZAhG": "MwHu",
            self.lot_number[17:19] + self.lot_number[9:11]: {
                self.lot_number[16:20]: {
                    self.lot_number[23:31]: self.lot_number[10:16]
                }
            },
            "em": {
                "ph": 0,
                "cp": 0,
                "ek": "11",
                "wd": 1,
                "nt": 0,
                "si": 0,
                "sc": 0
            }
        }
        plaintext = json.dumps(arg, ensure_ascii=False, separators=(',', ':'))

        key = f"{random_str}".encode()
        iv = b"0000000000000000"

        cipher = AES.new(key, AES.MODE_CBC, iv)
        cipher_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        cipher_array = list(cipher_bytes)

        self.aes_result = ''.join(f'{b:02x}' for b in cipher_array)

        # time.sleep(2)
        self.send()

    # 验证请求
    def send(self):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://gt4.geetest.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        cookies = {
            "captcha_v4_user": "2697368040f549b3966fe39cb8c6b763",
            "Hm_lvt_25b04a5e7a64668b9b88e2711fb5f0c4": "1782116502",
            "HMACCOUNT": "898C7941C8D2F0E5",
            "sajssdk_2015_cross_new_user": "1",
            "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%2219eee6bca0a2214-08c937d5dc2e5a8-26061151-1338645-19eee6bca0b1c23%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Fbaidu.php%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.geetest.com%2F%3Futm_campaign%3D%E7%99%BE%E5%BA%A6SEM%26utm_source%3Dbaidu%26utm_medium%3Dcpc%26utm_term%3D%E6%9E%81%E9%AA%8C%26utm_content%3D%E5%93%81%E7%89%8C%E8%AF%8D%E7%B3%BB%E5%88%97%26_channel_track_key%3DqXBWd7ZK%26bd_vid%3D9256518005686371993%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22cpc%22%2C%22%24latest_utm_campaign%22%3A%22%E7%99%BE%E5%BA%A6SEM%22%2C%22%24latest_utm_content%22%3A%22%E5%93%81%E7%89%8C%E8%AF%8D%E7%B3%BB%E5%88%97%22%2C%22%24latest_utm_term%22%3A%22%E6%9E%81%E9%AA%8C%22%7D%2C%22%24device_id%22%3A%2219eee6bca0a2214-08c937d5dc2e5a8-26061151-1338645-19eee6bca0b1c23%22%7D",
            "language": "zh",
            "Hm_lpvt_25b04a5e7a64668b9b88e2711fb5f0c4": "1782116550"
        }
        url = "https://gcaptcha4.geetest.com/verify"
        params = {
            "callback": f"geetest_{str(int(time.time() * 1000))}",
            "captcha_id": self.captchaId,
            "client_type": "web",
            "lot_number": self.lot_number,
            "risk_type": "slide",
            "payload": self.payload,
            "process_token": self.process_token,
            "payload_protocol": self.payload_protocol,
            "pt": self.pt,
            "w": self.aes_result + self.rsa_result
        }
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        json_data = json.loads(response.text[22:-1])
        self.count2 += 1
        if json_data['data']['result'] == 'success':
            self.count += 1
            logger.success(str(self.count) + '/' + str(self.count2))
            logger.success(response.text)
        else:
            logger.error(str(self.count) + '/' + str(self.count2))
            logger.error(response.text)



if __name__ == '__main__':
    m = Spider()
    num = 100
    for i in range(num):
        m.init_req()
    logger.success(f'{num}次成功率为: {m.count / num * 100}%')
