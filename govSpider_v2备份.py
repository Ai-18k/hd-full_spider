import random
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from loguru import logger
from lxml import etree
from curl_cffi import requests
import requests as req
import execjs
import json
import time
from retrying import retry
from datetime import datetime
from geetest4_icon import get_icon_position
from geetest4_nine import split_image, get_nine_position
from geetest4_word import get_word_position
from geetest4_phrase.predict import get_info
from feapder.network.user_agent import get
from pymongo import MongoClient
import re
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import iv8
import urllib.parse
import threading


def proxy_list():
    # return {
    # "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user":"17773711437", "pwd":"Qa9Uu2kf", "proxy": "t152.juliangip.cc:15041"},
    # "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user":"17773711437", "pwd":"Qa9Uu2kf", "proxy": "t152.juliangip.cc:15041"},
    # }
    return None

def safe_update(dst: dict, src: dict):
    """只更新合法 cookie（value 必须是 str/bytes）"""
    for k, v in src.items():
        if isinstance(v, (str, bytes)):
            dst[k] = v

def clean_cookie_dict(cookies: dict):
    """原地清洗非法 cookie"""
    bad_keys = [k for k, v in cookies.items() if not isinstance(v, (str, bytes))]
    for k in bad_keys:
        del cookies[k]

# 全局 requests session（WAF穿透用）
requests = requests.Session(impersonate=random.choice(["edge99",
    "edge101",
    # Chrome
    "chrome99",
    "chrome100",
    "chrome101",
    "chrome104",
    "chrome107",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "chrome133a",
    "chrome136",
    "chrome142",
    "chrome145",
    "chrome146",
    "safari153",
    "safari155",
    "safari170",
    "safari180",
    "safari184",
    "safari260",
    "safari2601",
    "firefox133",
    "firefox135",
    "firefox144",
    "firefox147",
    "tor145",
    "chrome",
    "edge",
    "safari",
    "safari_beta",
    "safari_ios_beta",
    "firefox",
    "safari15_3",
    "safari15_5",
    "safari17_0",
    "safari18_0",
    "safari18_4"
]))
functo_code = None

class CT:
    """瑞数CT WAF 穿透层 — 处理 521→521→412 以及CT cookie生成"""

    def __init__(self):
        self.cookies = {}
        self._cookies_lock = threading.Lock()
        self._last_rs_content = None
        self.url = "https://shiming.gsxt.gov.cn/socialuser-use-rllogin.html"
        self.waf_url = "https://shiming.gsxt.gov.cn/ctct/nwaf/waf.log"
        self.proxies = proxy_list()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://shiming.gsxt.gov.cn/socialuser-use-rllogin.html",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

    # ========== 加密工具方法 ==========

    def AES_encrypt(self, data, key, iv):
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypt_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypt_data).decode('utf-8')

    def AES_decrypt(self, data, key, iv):
        encrypted_data = base64.b64decode(data)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        decrypt_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return decrypt_data.decode('utf-8')

    def md5_encrypt(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # ========== CT Cookie 生成方法 ==========

    def get_CT_1rqu7ab01(self, xyjgnaksfLocal, js_code):
        _0x580299 = xyjgnaksfLocal['a6607e9a31_5d01d7']
        _0x1643ac = xyjgnaksfLocal['af8_dc12a_a162678']
        md5_js_code = self.md5_encrypt(js_code)
        _0x53a09c = "queryCTCT&&777&&" + md5_js_code
        text = "002&&" + _0x1643ac + "&&" + _0x53a09c + "&&" + xyjgnaksfLocal['af8_dc12a_a162678'][-2:]
        key = iv = _0x580299[3:19]
        CT_1rqu7ab01 = self.AES_encrypt(text, key, iv)
        return CT_1rqu7ab01

    def get_CT_16eadf26c(self, xyjgnaksfLocal):
        _0x580299 = xyjgnaksfLocal['a6607e9a31_5d01d7']
        _0x1643ac = xyjgnaksfLocal['af8_dc12a_a162678']
        text = _0x1643ac + '{"md":0,"mv":0,"mp":0,"kc":0}' + _0x1643ac[-2:]
        key = iv = _0x580299[3:19]
        CT_16eadf26c = self.AES_encrypt(text, key, iv)
        return CT_16eadf26c

    def get_CT_1f7ba0eb8(self):
        env = '[{"key":"user_agent","value":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"},{"key":"language","value":"zh-CN"},{"key":"pixel_ratio","value":1.75},{"key":"device_memory","value":0},{"key":"color_depth","value":32},{"key":"hardware_concurrency","value":16},{"key":"resolution","value":[1463,915]},{"key":"available_resolution","value":[867,1463]},{"key":"session_storage","value":true},{"key":"local_storage","value":true},{"key":"indexed_db","value":true},{"key":"open_database","value":false},{"key":"navigator_platform","value":"Win32"},{"key":"navigator_oscpu"},{"key":"do_not_track","value":null},{"key":"touch_support","value":10},{"key":"navigator_plugin_0","value":"PDF Viewer"},{"key":"navigator_plugin_1","value":"Chrome PDF Viewer"},{"key":"navigator_plugin_2","value":"Chromium PDF Viewer"},{"key":"navigator_plugin_3","value":"Microsoft Edge PDF Viewer"},{"key":"navigator_plugin_4","value":"WebKit built-in PDF"},{"key":"cookie_enabled","value":true},{"key":"canvas","value":"42bc35a6e9bd8118b80e48e1630186c8"},{"key":"svg","value":{"vendor":"Google Inc. (NVIDIA)","renderer":"ANGLE (NVIDIA, NVIDIA GeForce RTX 5060 Laptop GPU (0x00002D19) Direct3D11 vs_5_0 ps_5_0, D3D11)"}},{"key":"font","value":["Arial","Times New Roman","Helvetica","Courier New"]},{"key":"audio","value":48000}]'
        CT_1f7ba0eb8 = self.md5_encrypt(env) + self.md5_encrypt("ct2_fp" + self.md5_encrypt(env))[:4]
        return CT_1f7ba0eb8

    def get_CT_1e6tzab00(self, xyjgnaksfLocal, CT_1g9aa1ec2):
        _0x580299 = xyjgnaksfLocal['e09b_cc0baf4c431']
        key = iv = _0x580299[3:19]
        _0x53a09c = f"envCTCT&&{CT_1g9aa1ec2}&&0&&allRight"
        text = f"002&&{xyjgnaksfLocal['af8_dc12a_a162678']}&&{_0x53a09c}&&{xyjgnaksfLocal['af8_dc12a_a162678'][-2:]}"
        CT_1e6tzab00 = self.AES_encrypt(text, key, iv)
        return CT_1e6tzab00

    @staticmethod
    def genum_random(num):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        random_char = ''
        for i in range(num):
            random_char += chars[random.randint(0, 61)]
        return random_char

    def _0x58caff(self, length, mode=0):
        """随机字符串生成器
        :param length: 生成长度
        :param mode: 0=大小写字母+数字, 1=大小写字母, 2=数字
        """
        chars_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        chars_numbers = "0123456789"
        if mode == 0:
            charset = chars_letters + chars_numbers
        elif mode == 1:
            charset = chars_letters
        else:
            charset = chars_numbers
        return ''.join(random.choice(charset) for _ in range(length))

    def get_uuid(self):
        """生成魔改版的 UUID"""
        buffer = bytearray(16)
        timestamp = int(time.time() * 1000)
        for i in range(5, -1, -1):
            buffer[i] = timestamp & 255
            timestamp >>= 8
        for i in range(6, 16):
            buffer[i] = random.randint(0, 255)
        buffer[6] = buffer[6] & 15 | 64
        buffer[8] = buffer[8] & 63 | 128
        parts = []
        for i, byte in enumerate(buffer):
            hex_str = format(byte, '02x')
            if i in (4, 6, 8, 10):
                parts.append("-" + hex_str)
            else:
                parts.append(hex_str)
        base_uuid = "".join(parts)
        if base_uuid.startswith("-"):
            base_uuid = base_uuid[1:]
        hex_chars = base_uuid.replace("-", "")
        base_uuid_str = f"{hex_chars[0:8]}-{hex_chars[8:12]}-{hex_chars[12:16]}-{hex_chars[16:20]}-{hex_chars[20:]}"
        sum_val = 0
        for char in base_uuid_str:
            if char == '-':
                continue
            char_code = ord(char)
            if 48 <= char_code <= 57:
                sum_val += char_code - 48
            elif 97 <= char_code <= 102:
                sum_val += char_code - 97
            else:
                raise ValueError("UUID 只能包含 0-9 和 a-f 的字符")
        sum_str = str(sum_val)
        if len(sum_str) > 3:
            sum_str = sum_str[:3]
        else:
            sum_str = sum_str.zfill(3)
        random_part = self._0x58caff(8 - len(sum_str))
        magic_segment = sum_str + random_part
        uuid_parts = base_uuid_str.split("-")
        uuid_parts.insert(1, magic_segment)
        return "-".join(uuid_parts)

    def fetch(self, url):
        for _ in range(5):
            try:
                response = req.get(url, headers=self.headers, cookies=self.cookies, verify=False, proxies=self.proxies)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 412:
                    logger.success("Env Check PASS!!!")
                    self.cookies.update(response.cookies.get_dict())
                    return response.text
                time.sleep(2)
            except Exception as e:
                print(f"request_ct请求异常:{e},重试{_}/5 次")
                time.sleep(2**_)
        raise ConnectionError("网络链接异常")

    def fetch_waf(self, data):
        for _ in range(5):
            try:
                response = requests.post(self.waf_url, headers=self.headers, cookies=self.cookies, data=data, proxies=self.proxies)
                if response.status_code == 405:
                    return response.cookies['CT_1w0g8z10g']
                time.sleep(2)
            except Exception as e:
                print(f"request_ct请求异常:{e},重试{_}/5 次")
                time.sleep(2**_)
        raise ConnectionError("网络链接异常")


    def first_req(self, content):
        """处理412页面：提取JS、解密xyjgnaksf、生成CT cookies、获取RS6页面"""
        url_list = re.compile('src="(.*?)"', re.S).findall(content)
        js_url1 = "https://shiming.gsxt.gov.cn" + url_list[0]
        js_url2 = "https://shiming.gsxt.gov.cn" + url_list[1]
        cthtml = self.fetch(js_url2)
        eehtml = self.fetch(js_url1)
        xyjgnaksf = re.findall('= "(.*?)";', eehtml)[0]
        key = iv = xyjgnaksf[:4] + "1iuxaYxp0i#q"
        xyjgnaksfLocal = json.loads(self.AES_decrypt(xyjgnaksf[4:], key, iv))
        CT_1rqu7ab01 = self.get_CT_1rqu7ab01(xyjgnaksfLocal, cthtml)
        CT_16eadf26c = self.get_CT_16eadf26c(xyjgnaksfLocal)
        CT_1f7ba0eb8 = self.get_CT_1f7ba0eb8()
        CT_1g9aa1ec2 = self.get_uuid()
        CT_1e6tzab00 = self.get_CT_1e6tzab00(xyjgnaksfLocal, CT_1g9aa1ec2)
        self.cookies['CT_1rqu7ab01'] = CT_1rqu7ab01
        self.cookies['CT_16eadf26c'] = CT_16eadf26c
        self.cookies['CT_1f7ba0eb8'] = CT_1f7ba0eb8
        self.cookies['CT_1g9aa1ec2'] = CT_1g9aa1ec2
        self.cookies['CT_1e6tzab00'] = CT_1e6tzab00
        _0x5bbe33 = self.genum_random(4)
        text = '{"ips":["121.204.120.13"],"context":{"ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36","uach":{"brands":[{"brand":"Chromium","version":"148"},{"brand":"Google Chrome","version":"148"},{"brand":"Not/A)Brand","version":"99"}],"mobile":false,"platform":"Windows","hasOverride":false,"architecture":"x86","bitness":"64","formFactors":["Desktop"],"fullVersionList":[{"brand":"Chromium","version":"148.0.7778.217"},{"brand":"Google Chrome","version":"148.0.7778.217"},{"brand":"Not/A)Brand","version":"99.0.0.0"}],"model":"","platformVersion":"19.0.0","wow64":false},"browser":{"name":"Chrome","version":"148.0.7778.217","source":"uach","uach":{"name":"Chrome","version":"148.0.7778.217"},"ua":{"name":"Chrome","version":"148.0.0.0"},"shell":null},"os":{"name":"Windows","version":"19.0.0","uach":{"name":"Windows","version":"19.0.0"},"ua":{"name":"Windows","version":"10.0"},"source":"uach"},"engine":{"type":"Blink","source":"uach"},"screen":{"dpr":1.75,"cssWidth":836,"cssHeight":522.8571428571429,"cssMin":522.8571428571429,"hasTouch":false,"maxTouchPoints":10,"colorDepth":32,"pixelDepth":32},"mobile":{"isMobile":false,"source":"uach.mobile","confidence":"high","allDimensions":{"uachDisabled":false,"uachMobile":false,"platformMobile":false,"uaMobile":false,"touch":false,"smallScreen":true,"coarsePointer":false,"noHover":false}}},"checkRes":{"score":15,"tags":["mobile"],"reasons":["\\u79fb\\u52a8\\u7aef\\u68c0\\u6d4b\\u77db\\u76fe\\uff1anoHover=false \\u4e0e smallScreen=true \\u4e0d\\u4e00\\u81f4"]}}'
        key = iv = _0x5bbe33 + xyjgnaksfLocal['d92130a3ea_557685'][4:-4]
        data = _0x5bbe33 + self.AES_encrypt(text, key, iv)
        CT_1w0g8z10g = self.fetch_waf(data)
        self.cookies['CT_1w0g8z10g'] = CT_1w0g8z10g
        rs_html = self.fetch(self.url)
        return rs_html


class Hg(CT):
    """继承CT的WAF穿透能力，添加加速乐(521)处理和iv8 RS6环境执行"""

    def __init__(self):
        super(Hg, self).__init__()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":get("chrome"),
            "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }


    def jsl(self, content):
        """处理加速乐第一层 521 (JSFuck)"""
        resp = execjs.eval(re.findall(r"cookie=(.*?);location", content)[0])
        cookie = {
            "__jsl_clearance_s": re.findall(r"nce_s=(.*?); Max", resp)[0]
        }
        self.cookies.update(cookie)
        response = requests.get(url=self.url, headers=self.headers, cookies=self.cookies, proxies=self.proxies)
        logger.info(f"加速乐第二次请求的状态码:{response}")
        return response.text


    def _encrypt(self, str, new_bts):
        if str == "sha256":
            return hashlib.sha256(new_bts.encode('utf-8')).hexdigest()
        elif str == "md5":
            return hashlib.md5(new_bts.encode('utf-8')).hexdigest()
        elif str == "sha1":
            return hashlib.sha1(new_bts.encode('utf-8')).hexdigest()
        else:
            input(f"加密方式错误！{str}")


    def get_new_bts(self, godata):
        """破解加速乐第二层 521 (go())"""
        new_bts = ''
        for i in godata['chars']:
            for j in godata['chars']:
                new_bts = godata['bts'][0] + i + j + godata['bts'][1]
                encry_bts = self._encrypt(godata['ha'], new_bts)
                if encry_bts == godata['ct']:
                    return new_bts


    def resp_jsl(self, data):
        """处理加速乐第二层 521"""
        max_retries = 10
        for attempt in range(max_retries):
            try:
                godata = re.findall(r';go\((.*?)\)', data)[0]
                godata = json.loads(godata)
                __jsl_clearance_s = self.get_new_bts(godata)
                self.cookies.update({'__jsl_clearance_s': __jsl_clearance_s})
                respones = requests.get(url=self.url, headers=self.headers, cookies=self.cookies, proxies=self.proxies, timeout=(5, 15))
                if respones.status_code == 412 or respones.status_code == 200:
                    logger.info(f"加速乐第三次请求得到瑞数返回的状态码:{respones}")
                    return respones.text
            except Exception as e:
                logger.warning(f"请求失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
                if attempt == max_retries - 1:
                    raise

    def merge_cookie_header(self, cookie_header):
        """把 iv8 里拿到的 Cookie 请求头合并回 cookies 字典"""
        merged = dict(self.cookies or {})
        if cookie_header:
            for item in cookie_header.split(';'):
                item = item.strip()
                if not item or '=' not in item:
                    continue
                k, v = item.split('=', 1)
                merged[k] = v
        return merged


    def iv8_env(self, rs_response):
        """用 iv8 执行RS6页面中的 m.js，获取 RS6 会话 cookie

        Returns:
            tuple: (_publicKey, fiKxeghI)
              - _publicKey: RSA 公钥（用于加密登录凭据）
              - fiKxeghI: RS6 会话token（= dUs8TeLcaHgjP cookie值，登录POST必需参数）
        """
        environment = {
            "location": {
                "ancestorOrigins": {},
                "href": "https://shiming.gsxt.gov.cn/socialuser-use-rllogin.html",
                "origin": "https://shiming.gsxt.gov.cn",
                "protocol": "https:",
                "host": "shiming.gsxt.gov.cn",
                "hostname": "shiming.gsxt.gov.cn",
                "port": "",
                "pathname": "/socialuser-use-rllogin.html",
                "search": "",
                "hash": ""
            },
            "navigator": {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
            }
        }
        page_url = environment['location']['href']
        with iv8.JSContext(environment=environment, config={"timezone": "Asia/Shanghai"}) as ctx:
            # 1. 加载 second_req 返回的瑞数页面，执行页面里的 m.js。
            js_match = re.search(r'src=["\']([^"\']+\.js)["\'][^>]*r=[\'"]m[\'"]', rs_response)
            # html_data= etree.HTML(rs_response)
            # jsurl = html_data.xpath('//script[4]/@src')[0]
            # js_url = urllib.parse.urljoin(page_url, jsurl)
            if not js_match:
                raise RuntimeError("rs_response 里没有匹配到 r='m' 的 js")

            js_url = urllib.parse.urljoin(page_url, js_match.group(1))

            js_code = requests.get(js_url, headers=self.headers, cookies=self.cookies, proxies=self.proxies).text

            ctx.expose({
                "baseURL": page_url,
                "html": rs_response,
                "headers": [[k, v] for k, v in self.headers.items()],
                "resources": {js_url: js_code},
            }, "s1")

            ctx.eval("window.__iv8__.page.load(window.__iv8__.data.s1)")
            ctx.eval("window.__iv8__.eventLoop.sleep(100)")

            cookies_str = ctx.eval("""
                    (function () {
                        var entries = window.__iv8__.netLog.entries || [];
                        if (!entries.length) return '';
                        return entries[entries.length - 1].cookieHeader || '';
                    })()
                """)
            # 重点：iv8 生成的新 cookie 不要单独用，要合并到前两步 cookies 里面。
            cookies = self.merge_cookie_header(cookies_str)
            self.cookies.update(cookies)

    def get_publicKey(self):
        for _ in range(5):
            try:
                response = requests.get(self.url, headers=self.headers, cookies=self.cookies, proxies=self.proxies,
                                        verify=False, timeout=(10, 20))
            except Exception as e:
                logger.error(f"get_publicKey响应状态码 {response}:报错{e}")
                continue
            if response.status_code == 200:
                self.cookies.update(response.cookies.get_dict())
                pk_match = re.search(r'var\s+_publicKey\s*=\s*"(.*?)"', response.text)
                _publicKey = pk_match.group(1).strip('"') if pk_match else None
                logger.info(f"获取密钥 publicKey 成功!!")
                fiKxeghI = self.cookies.get("dUs8TeLcaHgjP", "")
                return _publicKey, fiKxeghI
        raise ConnectionError("获取publicKey失败！")

    def main_qe(self):
        """主WAF穿透流程: 521(JSFuck) → 521(go) → 412(CT cookies) → RS6(iv8) → 200(登录页)
        Returns:
            tuple: (_publicKey, fiKxeghI)
        """
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.get(self.url, headers=self.headers, proxies=self.proxies, timeout=(10, 20))
                if response.status_code == 521:
                    safe_update(self.cookies, response.cookies.get_dict())
                    logger.info(f"加速乐第一次请求的状态码:{response}")
                    data = self.jsl(response.text)
                else:
                    data = None
                ct_content = self.resp_jsl(data)
                rs_content = self.first_req(ct_content)
                self.iv8_env(rs_content)
                # 2. 携带完整 cookie 重新请求页面，拿到带 XHR hook 的真实页面 JS。
                _publicKey, fiKxeghI=self.get_publicKey()
                return _publicKey, fiKxeghI
            except Exception as e:
                logger.warning(f"请求失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
                if attempt == max_retries - 1:
                    raise


class JY(Hg):
    """极验4验证码处理层 — 识别+验证"""

    def __init__(self):
        super(JY, self).__init__()
        self.url_wou = "http://gcaptcha4.geetest.com/load"
        self.execjs_js = execjs.compile(open("jydemo.js", mode="r", encoding="utf-8").read())
        self.uuid_challenge = self.execjs_js.call("uuid")
        self.ts = str(int(time.time() * 1000))
        self.user = "xiaoajian"
        self.api_key = "bb743a2a395eec730fe480323e7bfdcf"
        self.captcha_id = "b608ae7850d2e730b89b02a384d6b9cc"
        self._publicKey = None
        self.fiKxeghI = ""
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://shiming.gsxt.gov.cn/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec-ch-ua": "Google",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows"
        }
        self.enc = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256}

    @staticmethod
    def base64_api_s(img):
        b64 = base64.b64encode(img).decode()
        data = {"token": "6EubemuI0kmsMzHS6BjgVTBwMEu4uADPuXnJ30SwDr4", "type": "30114", "extra": "je4_phrase", "image": b64}
        resp = requests.post("http://api.jfbym.com/api/YmServer/customApi", headers={"Content-Type": "application/json"}, json=data).json()
        return resp["data"]["data"] if resp.get("code") == 10000 else "232,145|159,107|61,34"

    def load_jy(self):
        params = {"captcha_id": self.captcha_id, "client_type": "web", "lang": "zh-cn"}
        resp = json.loads(requests.get(url=self.url_wou, params=params, headers=self.headers).text.replace("(", "").replace(")", ""))
        data = resp["data"]
        info = {"type_name": data["captcha_type"], "process_token": data["process_token"], "payload": data["payload"],
                "datetime": data["pow_detail"]["datetime"], "lot_number": data["lot_number"],
                "hashfunc": data["pow_detail"]["hashfunc"], "bits": data["pow_detail"]["bits"],
                "pt": data["pt"], "payload_protocol": data["payload_protocol"]}
        ct = info["type_name"]
        if ct == "word": info.update({"imgs_url": "http://static.geetest.com/" + data["imgs"], "ques_list": data["ques"]})
        elif ct == "icon": info.update({"imgs_url": "https://static.geetest.com/" + data["imgs"], "ques_list": data["ques"]})
        elif ct == "phrase": info.update({"slice_xiao": "https://static.geetest.com/" + data["imgs"]})
        elif ct == "nine": info.update({"slice_xiao": "https://static.geetest.com/" + data["imgs"], "bg_da": "https://static.geetest.com/" + data["ques"][0], "nine_nums": data["nine_nums"]})
        return info

    def get_random_str(self):
        return "".join(hex(int(65536 * (1 + random.random())))[3:] for _ in range(4))


    def get_sign(self, data):
        lot = data["lot_number"]; hf = data["hashfunc"]; bits = data["bits"]; dt = data["datetime"]
        arg = {"passtime": random.randint(1700, 3500), "userresponse": data["click_smark"], "device_id": "",
               "lot_number": lot, "pow_msg": "", "geetest": "captcha", "lang": "zh", "ep": "123",
               "biht": "1426265548", "LldF": "7rCZ",
               lot[7:13]: {lot[1:5] + lot[24:28]: {lot[3:5] + lot[16:18]: lot[16:20]}},
               "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0}}
        while True:
            rs = self.get_random_str()
            pm = f"1|{bits}|{hf}|{dt}|{self.captcha_id}|{lot}||{rs}"
            ps = self.enc[hf](pm.encode()).hexdigest()
            if ps.startswith("000"): arg["pow_msg"] = pm; arg["pow_sign"] = ps; break
        return arg

    def jy_shibie(self):
        data = self.load_jy()
        if data.get("type_name") == "word":
            bl = [requests.get("https://static.geetest.com/" + u).content for u in data["ques_list"]]
            click_list = get_word_position(requests.get(data["imgs_url"]).content, bl)
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
        elif data.get("type_name") == "phrase":
            resp_bytes = requests.get(url=data["slice_xiao"]).content
            # coord_str = self.base64_api_s(resp_bytes)
            coord_str = get_info(resp_bytes)
            print("语序识别:",coord_str)
            click_list = [[int(x), int(y)] for p in coord_str.split("|") if len(parts := p.split(",")) == 2 for x, y in [parts]]
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
            logger.info(f"语序点选坐标:{click_smark}")
        elif data.get("type_name") == "icon":
            bl = [requests.get("https://static.geetest.com/" + u).content for u in data["ques_list"]]
            click_list = get_icon_position(requests.get(data["imgs_url"]).content, bl)
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
        elif data.get("type_name") == "nine":
            tg = requests.get(data["bg_da"]).content; bg = requests.get(data["slice_xiao"]).content
            im = Image.open(BytesIO(bg)).convert("RGBA"); buf = BytesIO(); im.save(buf, format="PNG")
            click_smark, qc = get_nine_position(tg, split_image(buf.getvalue()), data["nine_nums"])
        else:
            logger.warning(f"未知验证码类型: {data.get('type_name')}"); click_smark = None
        data["click_smark"] = click_smark
        return self.get_sign(data), data

    def get_w(self):
        arg, data = self.jy_shibie()
        with open("w.js", mode="r", encoding="utf8") as f:
            jsObj = execjs.compile(f.read())
        return jsObj.call("get_w", arg, self.get_random_str()), data

    def send(self):
        for attempt in range(10):
            try:
                h = {"Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://shiming.gsxt.gov.cn/",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"}
                w, data = self.get_w()
                params = {"captcha_id": self.captcha_id, "client_type": "web", "lot_number": data["lot_number"],
                          "payload": data["payload"], "process_token": data["process_token"],
                          "payload_protocol": data["payload_protocol"], "pt": data["pt"], "w": w}
                resp = json.loads(requests.get("https://gcaptcha4.geetest.com/verify", headers=h, params=params).text.replace("(", "").replace(")", ""))
                if resp["data"]["result"] == "success":
                    logger.success("验证码识别成功！！")
                    return {"captcha_output": resp["data"]["seccode"]["captcha_output"], "gen_time": resp["data"]["seccode"]["gen_time"],
                            "lot_number": resp["data"]["seccode"]["lot_number"], "pass_token": resp["data"]["seccode"]["pass_token"]}
            except Exception as e:
                logger.warning(f"验证码识别失败 ({attempt+1}/10): {e}")
                if attempt == 9: raise


class Govspider(JY):

    def __init__(self):
        super().__init__()
        self.headers = {"Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9", "Cache-Control": "no-cache",
                        "Connection": "keep-alive", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://shiming.gsxt.gov.cn", "Pragma": "no-cache",
                        "Referer": "https://shiming.gsxt.gov.cn/socialuser-use-rllogin.html",
                        "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest",
                        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                        "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\""}
        self.CURRENT_ACCOUNT_KEY = "gov:01"; self.backcomp = []
        self.processed_codes = set(); self.PROCESSED_CODES_KEY = "gov:processed_codes"
        self.mongo_client = MongoClient(host="192.168.6.167", port=27017)
        self.mongo_db = self.mongo_client["gov_spider"]
        self.shareholder_collection = self.mongo_db["shareholder_data"]
        self.shareholder_coll2 = self.mongo_db["shareholder_type"]
        self.equity_collection = self.mongo_db["equity_data"]
        self.Intellectual_property = self.mongo_db["intell_property"]
        self.trademark_info = self.mongo_db["trademark_info"]
        self.login_url="https://shiming.gsxt.gov.cn/socialuser-use-login-request.html"

    def unified_request(self, url, method, params=None, data=None, json_data=None,
                        timeout=(10, 20), custom_headers=None, custom_cookie=None, retry_func=None, **kwargs):
        """
        统一的HTTP请求方法，封装所有请求的通用逻辑

        Args:
            url: 请求URL
            method: 请求方法 ('GET' 或 'POST')
            params: URL参数 (GET请求)
            data: 表单数据 (POST请求)
            json_data: JSON数据 (POST请求)
            timeout: 超时时间
            custom_headers: 自定义请求头
            custom_cookie: 自定义cookies字典
            retry_func: 重试时调用的函数
            **kwargs: 其他参数

        Returns:
            response: requests.Response对象
        """
        # 合并自定义请求头
        # headers = self.headers.copy()
        # if custom_headers:
        #     headers.update(custom_headers)
        if custom_cookie:
            self.cookies.update(custom_cookie)
        try:
            if method.upper() == 'GET':
                response = requests.get(
                    url=url,
                    headers=custom_headers if custom_headers else self.headers,
                    cookies=self.cookies,
                    params=params,
                    proxies=self.proxies,
                    timeout=timeout,
                    **kwargs
                )
            elif method.upper() == 'POST':
                response = requests.post(
                    url=url,
                    headers=custom_headers if custom_headers else self.headers,
                    cookies=self.cookies,
                    params=params,
                    data=data,
                    json=json_data,
                    proxies=self.proxies,
                    timeout=timeout,
                    **kwargs
                )
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            # 处理响应状态码
            if response.status_code == 200:
                with open("Node_control/unified_request_200.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                if "NGIDERRORCODE" in response.text:
                    logger.error("账号异常！！切换账号。。。。")
                    # user = self.ltouser()
                    # self.next_login(user)
                    raise "重试！！"
                else:
                    return response
            elif response.status_code == 412:
                with open("Node_control/unified_request_412.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                try:
                    logger.info(
                        f"代理412信息：{requests.get('https://myip.ipip.net', proxies=self.proxies, timeout=(5, 10)).text}")
                except:
                    pass
                try:
                    # rs_content = response.text
                    # content, ts_js, jsurl = self.main_rs_info(response.text)
                    # self.execjs_data(content,ts_js,jsurl)
                    self.iv8_env(response.text)
                except Exception as e:
                    logger.info(f"处理412状态码时出错: {e}")
                if retry_func:
                    return retry_func()
                else:
                    raise ConnectionError("412状态码，需要重试")
            elif response.status_code == 521:
                with open("Node_control/unified_request_521.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                try:
                    logger.info(
                        f"代理521信息：{requests.get('https://myip.ipip.net', proxies=self.proxies, timeout=(5, 10)).text}")
                except:
                    pass
                try:
                    logger.info(f"加速乐第一次请求的状态码:{response}")
                    self.url = url
                    data = self.jsl(response.text)
                    ct_content = self.resp_jsl(data)
                    self._last_rs_content = self.first_req(ct_content)
                    self.iv8_env(self._last_rs_content)
                except Exception as e:
                    logger.info(f"处理521状态码时出错: {e}")
                if retry_func:
                    return retry_func()
                else:
                    raise ConnectionError("521状态码，需要重试")
            elif response.status_code == 403:
                with open("Node_control/unified_request_403.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                try:
                    logger.info(
                        f"代理403信息：{requests.get('https://myip.ipip.net', proxies=self.proxies, timeout=(5, 10)).text}")
                except:
                    pass
                time.sleep(5)
                self.proxies = proxy_list()
                if retry_func:
                    return retry_func()
                else:
                    raise ConnectionError("403状态码，需要重试")
            elif response.status_code == 400:
                with open("Node_control/unified_request_400.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                logger.warning(f"unified_request 400错误，链接:{url}")
                if retry_func:
                    return retry_func()
                else:
                    raise ConnectionError(f"400 Bad Request: {url}")
            else:
                with open(f"Node_control/unified_request_{response.status_code}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                raise ConnectionError(f"未识别unified_request请求验证码{response}:需要重试")
        except Exception as e:
            if retry_func:
                return retry_func()
            else:
                raise e
    @property
    def cookie(self):
        return self.get_fresh_cookie()


    def get_fresh_cookie(self):
        try: self.iv8_env(self._last_rs_content)
        except Exception as e: logger.error(f"get_fresh_cookie: {e}")
        return self.cookies.copy() if isinstance(self.cookies, dict) else {}

    def _ensure_session_fresh(self):
        """轻量级探测：GET首页检查cookie是否新鲜，遇521/412自动恢复"""
        for attempt in range(3):
            try:
                resp = requests.get(
                    "https://shiming.gsxt.gov.cn/index.html",
                    headers=self.headers, cookies=self.cookies,
                    proxies=self.proxies, timeout=(10, 15), verify=False
                )
                if resp.status_code == 200:
                    safe_update(self.cookies, resp.cookies.get_dict())
                    return True
                elif resp.status_code in (521, 412):
                    logger.warning(f"[Session] 收到{resp.status_code}, 刷新WAF...")
                    if resp.status_code == 521:
                        safe_update(self.cookies, resp.cookies.get_dict())
                        data = self.jsl(resp.text)
                        ct_content = self.resp_jsl(data)
                        self._last_rs_content = self.first_req(ct_content)
                    else:  # 412
                        safe_update(self.cookies, resp.cookies.get_dict())
                        self._last_rs_content = resp.text
                    self.iv8_env(self._last_rs_content)
                else:
                    logger.warning(f"[Session] 探测返回{resp.status_code}")
            except Exception as e:
                logger.warning(f"[Session] 探测异常(attempt {attempt+1}/3): {e}")
                time.sleep(2)
        logger.error("[Session] 刷新失败!")
        return False


    def loginuser(self, user, params):
        for _ in range(5):
            try:
                login_js = execjs.compile(open("login.js", "r", encoding="utf-8").read())
                enc = login_js.call("f", self._publicKey, user["pwd"], user["user"])
                data = {"un": enc["un"], "gp": enc["gp"], "lot_number": params["lot_number"],
                        "captcha_output": params["captcha_output"], "pass_token": params["pass_token"],
                        "gen_time": params["gen_time"], "captchaId": "b608ae7850d2e730b89b02a384d6b9cc",
                        "fiKxeghI": self.fiKxeghI}
                rt = lambda: self.unified_request(url=self.login_url, method="POST", data=data, timeout=(5, 15), retry_func=None,
                                                  allow_redirects=False)
                response = self.unified_request(url=self.login_url, method="POST", data=data, timeout=(5, 10), retry_func=rt,
                                         allow_redirects=False)
                logger.info(f"loginuser: status={response.status_code}")
                if response.status_code in (200, 302):
                    if response.status_code == 302:
                        logger.success("登录成功(302)")
                    elif response.status_code == 200:
                        try:
                            rj = response.json()
                            if rj.get("success") and rj.get("value") == "1":
                                logger.success("登录成功")
                            else:
                                logger.warning(f"登录异常: {rj}");
                                return False
                        except:
                            pass
                    ir = requests.get("https://shiming.gsxt.gov.cn/index.html", headers=self.headers,
                                      cookies=self.cookies,
                                      proxies=self.proxies, timeout=(10, 20), verify=False)
                    safe_update(self.cookies, ir.cookies.get_dict())
                    if ir.status_code == 200:
                        self._last_rs_content = ir.text
                        self.iv8_env(ir.text)
                        logger.success("首页cookie已更新")
                    return True
                else:
                    logger.error(f"登陆异常响应码:{response}")
            except Exception as e:
                logger.error(f"loginuser登陆失败: {e}")
        logger.error(f"登录失败: {response.status_code}")
        return False

    @retry(wait_fixed=1000)
    def nextcompany(self, data_list, company, param, page):
        while True:
            url = "https://shiming.gsxt.gov.cn/corp-query-search-advancetest.html"
            params = {"searchword": company, "lot_number": param["lot_number"], "captcha_output": param["captcha_output"],
                      "pass_token": param["pass_token"], "gen_time": param["gen_time"],
                      "captchaId": "b608ae7850d2e730b89b02a384d6b9cc", "token": "90117940",
                      "tab": "ent_tab", "province": "", "page": page,
                      "geetest_challenge": "", "geetest_validate": "", "geetest_seccode": ""}
            rt = lambda: self.unified_request(url=url, method="GET", params=params, timeout=(5, 15), retry_func=None)
            r = self.unified_request(url=url, method="GET", params=params, timeout=(5, 15), retry_func=rt)
            if r.status_code == 200:
                data_list += self.getdata(etree.HTML(r.text))
                if page >= 7: return data_list
                page += 1
            elif r.status_code == 403: time.sleep(30); raise Exception("ip检测")
            else: return data_list


    def searchcompany(self, company, page):
        for _ in range(5):
            try:
                p = self.send()
                url = "https://shiming.gsxt.gov.cn/corp-query-search-1.html"
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://shiming.gsxt.gov.cn",
                    "Pragma": "no-cache",
                    "Referer": "https://shiming.gsxt.gov.cn/index.html",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\""
                }
                data = {"tab": "ent_tab", "province": "", "geetest_challenge": "", "geetest_validate": "",
                        "geetest_seccode": "",
                        "lot_number": p["lot_number"], "captcha_output": p["captcha_output"],
                        "pass_token": p["pass_token"], "gen_time": p["gen_time"],
                        "captchaId": "b608ae7850d2e730b89b02a384d6b9cc", "token": "88379074",
                        "searchword": company, "page": page}
                def rt():
                    p2 = self.send()
                    for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]: data[k] = p2[k]
                    return self.unified_request(url=url, method="POST", data=data, timeout=(5, 15),custom_headers=headers,
                                                custom_cookie=self.cookie, retry_func=None)
                r = self.unified_request(url=url, method="POST", data=data,custom_headers=headers, timeout=(5, 15),custom_cookie=self.cookie, retry_func=rt)
                if r.status_code == 200:
                    if "NGIDERRORCODE" in r.text: raise ConnectionError("账号异常")
                    html = etree.HTML(r.text)
                    if html.xpath("//*[@id='advs']/div/div[2]"):
                        try:
                            tp = int(html.xpath("//div[@class='search_result']/span/text()")[0])
                        except:
                            try:
                                tp = int(html.xpath("//*[@id='advs']/div/div[1]/span/text()")[0])
                            except:
                                tp = 1
                        if tp >= 1000:
                            dl = self.getdata(html)
                            page += 1
                            return dl + (self.nextcompany([], company, p, page) or [])
                        return self.getdata(html)
                    return None
            except Exception as e:
                print(e)
        raise ConnectionError(f"searchcompany搜索公司异常!!")

    # ================================================================
    # 数据解析工具
    # ================================================================
    def is_chinese(self, text):
        """判断文本是否为纯中文"""
        chinese_pattern = re.compile(
            r'^[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]+$')
        if text.isdigit():
            return False
        else:
            if chinese_pattern.fullmatch(text):
                return text
            else:
                return text

    @staticmethod
    def contains_html_or_name_colon(text):
        """判断字符串中是否包含HTML标签或'名称:'"""
        text = "".join(text)
        html_tag_pattern = re.compile(r'<[^>]+>')
        name_colon_pattern = re.compile(r'名称[:：]')
        if html_tag_pattern.search(text):
            return True
        if name_colon_pattern.search(text):
            return True
        return False

    # ================================================================
    # 公司详情页提取 — 基本信息 + 各板块URL
    # ================================================================

    @retry(wait_fixed=1000)
    def vhpage(self, info):
        """获取公司详情页，提取基本工商信息 + 各数据板块API端点

        提取的板块URL(10个):
          bgurl   = alterInfoUrl        → 工商变更
          shaurl  = shareholderUrl      → 股东信息
          spurl   = getFoodChkInfoUrl   → 食品检测
          gdurl   = insInvinfoUrl       → 股东出资
          xlurl   = IntellectualInfoUrl → 知识产权
          nburl   = anCheYearInfo       → 年报年份列表
          banurl  = annRepDetailUrl     → 年报详情
          sburl   = allTrademarkUrl     → 商标
          cpjdurl = eproquacheckUrl     → 产品质量监督抽查
          ssjurl  = getDrRaninsResUrl   → 双随机抽查
          xzurl   = nLicUrl             → 行政许可

        Returns:
            tuple: (comlist URL字典, detailData 基本信息字典)
        """
        logger.info("------------------提取工商数据----------------")

        def retry_func():
            return self.unified_request(
                url=info["link"], method='GET',
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
            )

        response = self.unified_request(
            url=info["link"], method='GET',
            timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
        )
        logger.info(f"vhpage状态码:{response}")

        if response.status_code == 200:
            if response.text:
                soup = BeautifulSoup(response.text, "html.parser")
                self.cookies.update(response.cookies.get_dict())
                # --- 提取各板块API端点 ---
                def extract_url(var_name):
                    """从页面JS变量中提取API URL"""
                    try:
                        result = re.findall(f'var {var_name} = "(.*?)";', response.text, re.S)[0]
                        return "https://shiming.gsxt.gov.cn" + result
                    except:
                        match = re.search(rf'var\s+{var_name}\s*=\s*"(.*?)";', response.text)
                        if match:
                            return "https://shiming.gsxt.gov.cn" + match.group(1)
                        logger.info(f"未找到{var_name}")
                        return None
                bgurl = extract_url("alterInfoUrl")        # 工商变更
                shaurl = extract_url("shareholderUrl")      # 股东信息
                spurl = extract_url("getFoodChkInfoUrl")    # 食品检测
                gdurl = extract_url("insInvinfoUrl")        # 股东出资
                xlurl = extract_url("IntellectualInfoUrl")  # 知识产权
                nburl = extract_url("anCheYearInfo")        # 年报年份
                banurl = extract_url("annRepDetailUrl")     # 年报详情
                sburl = extract_url("allTrademarkUrl")      # 商标
                cpjdurl = extract_url("eproquacheckUrl")    # 产品质量
                ssjurl = extract_url("getDrRaninsResUrl")   # 双随机抽查
                xzurl = extract_url("nLicUrl")              # 行政许可

                # --- 提取基本工商信息 ---
                def clean_key(key):
                    key = re.sub(r'[\s\xa0\u2002\u2003\u2009\u00a0&emsp;&thinsp;]+', '', key)
                    key = key.replace("&nbsp;", "").replace(" ", "")
                    key = key.replace("：", "").replace(":", "")
                    return key

                field_map = {
                    "统一社会信用代码": "tyxydm",
                    "企业名称": "companyName", "名称": "companyName",
                    "注册号": "gszch",
                    "法定代表人": "legalName", "负责人": "legalName",
                    "经营者": "legalName", "投资人": "legalName",
                    "执行事务合伙人": "legalName",
                    "类型": "companyType",
                    "成立日期": "dateOfEstablishment", "注册日期": "dateOfEstablishment",
                    "注册资本": "registeredCapital",
                    "登记机关": "registrationAuthority",
                    "登记状态": "registrationStatus",
                    "住所": "registeredAddress", "经营场所": "registeredAddress",
                    "经营范围": "businessScope",
                    "营业期限": "yyqx",
                }

                result = {
                    "companyName": None, "companyType": None,
                    "registeredAddress": None, "legalName": None,
                    "dateOfEstablishment": None, "registrationAuthority": None,
                    "registrationStatus": None, "businessScope": None,
                    "tyxydm": None, "yyqx": None,
                    "gszch": "", "registeredCapital": ""
                }

                dls = soup.find_all("dl")
                for dl in dls:
                    dt = dl.find("dt")
                    dd = dl.find("dd")
                    if not dt or not dd:
                        continue
                    raw_key = dt.get_text(strip=True)
                    key = clean_key(raw_key)
                    value = dd.get_text(strip=True)
                    if not value and dd.has_attr("title"):
                        value = dd["title"].strip()
                    for k, v in field_map.items():
                        if k in key:
                            if v == "dateOfEstablishment":
                                date_match = re.match(r"(\d{4})年(\d{2})月(\d{2})日", value)
                                if date_match:
                                    result[v] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                                else:
                                    result[v] = value
                            else:
                                result[v] = value
                            break

                # 营业期限
                yyzz_all_div = soup.find("div", class_="yyzz-all")
                if yyzz_all_div:
                    table = yyzz_all_div.find("table", class_="yyzz-table")
                    if table:
                        trs = table.find_all("tr")
                        for tr in trs:
                            tds = tr.find_all("td")
                            if len(tds) >= 2:
                                key_text = tds[0].get_text(strip=True).replace('\xa0', '').replace('\u2003', '').replace('\u2002', '').replace('\u2009', '')
                                if "营业期限" in key_text or "合伙期限" in key_text:
                                    result["yyqx"] = tds[1].get_text(strip=True)
                                    break
                if result["yyqx"] == "至  长期":
                    result["yyqx"] = result['dateOfEstablishment'] + result["yyqx"]

                # 构建返回
                comlist = {
                    "company": info["name"],
                    "bgurl": bgurl,
                    "shaurl": shaurl,
                    "spurl": spurl,
                    "gdurl": gdurl,
                    "xlurl": xlurl,
                    "nburl": nburl,
                    "banurl": banurl,
                    "sburl": sburl,
                    "cpjdurl": cpjdurl,
                    "ssjurl": ssjurl,
                    "xzurl": xzurl
                }
                return comlist, result
        else:
            try:
                logger.info("vhpage代理信息:{}".format(requests.get("https://myip.ipip.net", proxies=self.proxies, timeout=(5, 10)).text))
            except:
                pass
            return self.vhpage(info)

    def getdata(self, html):
        """从搜索结果页HTML中提取公司列表"""
        elems = html.xpath('//a[contains(@class, "search_list_item")]')
        seen = set()
        herf_list = []
        for elem in elems:
            h_f = elem.xpath('./@href')
            h_f = h_f[0] if h_f else ""
            link = "https://shiming.gsxt.gov.cn" + h_f if h_f and h_f != "javascript:void(0)" else None
            # 公司名称
            name = "".join(elem.xpath('.//h1//text()')).replace('\n', '').strip()
            ## 企业状态
            status = elem.xpath('.//div[contains(@class,"wrap-corpStatus")]/span/text()')
            business_status = status[0].strip() if status else ""
            ## 统一社会信用代码
            uscc = elem.xpath('.//div[contains(@class,"div-map2")]//span[@class="g3"]/text()')
            tyxydm = uscc[0].strip() if uscc else ""

            regno = elem.xpath('.//div[contains(@class,"div-info-circle3")][contains(., "注册号")]//span[@class="g3"]/text()')
            gszch = regno[0].strip() if regno else ""
            date = elem.xpath('.//div[contains(@class,"div-info-circle2")]//span[@class="g3"]/text()')
            dateOfEstablishment = date[0].strip() if date else ""
            person = elem.xpath('.//div[contains(@class,"div-user2")]//span[@class="g3"]/text()')
            legalName = person[0].strip() if person else ""
            if not legalName:
                for key in ["法定代表人", "负责人", "经营者", "投资人", "执行事务合伙人"]:
                    divs = elem.xpath(f".//div[contains(text(), '{key}:') or contains(text(), '{key}：')]")
                    found = False
                    for div in divs:
                        spans = div.xpath(".//span[@class='g3']")
                        if spans:
                            content = ''.join(spans[0].itertext()).strip()
                            if content:
                                legalName = content
                                found = True
                                break
                        div_text = ''.join(div.itertext()).strip()
                        m = re.search(rf"{re.escape(key)}[:：]\s*(.*)", div_text)
                        if m:
                            legalName = m.group(1).strip()
                            found = True
                            break
                    if found:
                        break
            hist_name_div = elem.xpath('.//div[contains(@class,"div-info-circle3")][contains(text(), "历史名称") or contains(., "历史名称")]')
            oldCompanyNameList = []
            if hist_name_div:
                hist_name_span = hist_name_div[0].xpath('.//span[@class="g3"]')
                if hist_name_span:
                    hl = ''.join(hist_name_span[0].itertext()).replace('\n', '').strip()
                    hl = self.is_chinese(hl)
                    oldCompanyNameList = hl.replace("；", ",").split(",") if str(hl) else []
                    if self.contains_html_or_name_colon(oldCompanyNameList):
                        oldCompanyNameList = ["".join(oldCompanyNameList).split("名称:")[-1]]
            unique_key = (name, link, legalName, business_status, gszch, tyxydm, dateOfEstablishment, ",".join(oldCompanyNameList))
            if unique_key not in seen:
                seen.add(unique_key)
                hrefs = {
                    "name": name,
                    "link": link,
                    "legalName": legalName,
                    "business_status": business_status,
                    "gszch": gszch,
                    "tyxydm": tyxydm,
                    "dateOfEstablishment": dateOfEstablishment,
                    "oldCompanyNameList": oldCompanyNameList
                }
                herf_list.append(hrefs)
                logger.info(hrefs)
        return herf_list

    # ================================================================
    # 年报数据采集
    # ================================================================

    def get_anCheId(self, url):
        """获取年报年份列表，返回最新年份的 anCheId"""

        def retry_func():
            return self.unified_request(
                url=url, method='GET', timeout=(10, 20),
                custom_cookie=self.cookie, retry_func=None
            )

        response = self.unified_request(
            url=url, method='GET', timeout=(10, 20),
            custom_cookie=self.cookie, retry_func=retry_func
        )
        logger.info(f"get_anCheId状态码:{response}")
        if response.status_code == 200:
            if response.json():
                return response.json()[-1]
            return None
        return None

    def anreport(self, aninfo, url):
        """获取年报详情页的 ancheid（用于后续获取电话+规模）"""
        logger.info("-----------------年报获取采集------------------")
        anCheId = aninfo["anCheId"]
        year = aninfo["anCheYear"]
        params = {"anCheId": anCheId, "entType": "1", "anCheYear": year, "provinceid": "100000"}

        def retry_func():
            return self.unified_request(
                url=url, method='GET', params=params,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
            )

        try:
            response = self.unified_request(
                url=url, method='GET', params=params,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"anreport状态码:{response}")
            if response.status_code == 200:
                content_type = response.headers['Content-Type']
                if 'text/html' in content_type:
                    rs_content = response.text
                    self.iv8_env(response.text)
                match = re.search(r'id="ancheid"\s*value="(.*?)"', response.text)
                if match:
                    return match.group(1)
                return None
            return ""
        except Exception as e:
            logger.error(f"anreport:{e}")
            time.sleep(5)
            return self.anreport(aninfo, url)

    def anreport_f(self, code):
        """从年报中提取联系电话"""
        url = f"https://shiming.gsxt.gov.cn/corp-query-entprise-info-baseinfo-{code}.html"

        def retry_func():
            return self.unified_request(
                url=url, method='POST', timeout=(10, 15),
                custom_cookie=self.cookie, retry_func=None
            )

        response = self.unified_request(
            url=url, method='POST', timeout=(10, 15),
            retry_func=retry_func, custom_cookie=self.cookie,
        )
        if response.status_code == 200:
            phone = response.json()["data"][0]["tel"]
            return phone
        return ""

    def anreport_s(self, code):
        """从年报中提取参保人数（企业规模）"""
        for attm in range(10):
            url = f"https://shiming.gsxt.gov.cn/corp-query-entprise-info-AnnSocsecinfo-{code}.html"

            def retry_func():
                return self.unified_request(
                    url=url, method='POST', timeout=(10, 15),
                    custom_cookie=self.cookie, retry_func=None
                )

            response = self.unified_request(
                url=url, method='POST', timeout=(10, 15),
                custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"anreport_s状态码:{response}")
            if response.status_code == 200:
                if response.json()["data"]:
                    return response.json()["data"][0]["so110"]
                return ""
        return ""

    # ================================================================
    # 股东出资采集
    # ================================================================

    def equity_pledge(self, type, params, datalist, page):
        """股东出资数据提取并保存到MongoDB

        Args:
            type: "data"=出资明细 / "type"=股东类型
            params: [url, company_name]
        """
        while True:
            data = {"draw": page, "start": (page - 1) * 5, "length": "5"}

            def retry_func():
                return self.unified_request(
                    url=params[0], method='POST', data=data,
                    timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
                )

            response = self.unified_request(
                url=params[0], method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"equity_pledge:{response}")
            if response.status_code == 200:
                logger.info(f"股东出资：{response.json()}")
                totalPage = int(response.json()['totalPage'])
                items = response.json()["data"]
                if items:
                    for item in items:
                        item['created_at'] = datetime.now()
                        item['data_source'] = 'equity_pledge'
                        item['company_url'] = params[0]
                        item['company'] = params[1]
                        if type == "data":
                            self.shareholder_collection.insert_one(item)
                        else:
                            self.shareholder_coll2.insert_one(item)
                        item.pop('_id', None)  # 防止 ObjectId 污染后续序列化
                    datalist.extend(items)
                    if page >= totalPage:
                        return datalist
                else:
                    logger.warning(f"无 【{params[1]}】 股东出资信息！！")
                    return None
                page += 1
            else:
                logger.info(f"equity_pledge请求失败，状态码：{response}")
                break

    # ================================================================
    # 工商变更采集
    # ================================================================

    def Brchange(self, comlist, datalist, page):
        """工商变更数据提取并保存到MongoDB"""
        while True:
            data = {"draw": page, "start": (page - 1) * 5, "length": "5"}

            def retry_func():
                return self.unified_request(
                    url=comlist["bgurl"], method='POST', data=data,
                    timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
                )

            response = self.unified_request(
                url=comlist["bgurl"], method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"Brchange状态码:{response}")
            if response.status_code == 200:
                totalPage = int(response.json()['totalPage'])
                items = response.json()["data"]
                for item in items:
                    item['created_at'] = datetime.now()
                    item['data_source'] = 'business_change'
                    item['company_url'] = comlist["bgurl"]
                    item['company'] = comlist["company"]
                    self.equity_collection.insert_one(item)
                    item.pop('_id', None)  # 防止 ObjectId 污染
                datalist.extend(items)
                if page >= totalPage:
                    return datalist
                page += 1
            else:
                break

    # ================================================================
    # 知识产权采集
    # ================================================================

    def Intpro(self, comlist, datalist, page):
        """知识产权数据保存"""
        while True:
            data = {"draw": page, "start": (page - 1) * 5, "length": "5"}

            def retry_func():
                return self.unified_request(
                    url=comlist["xlurl"], method='POST', data=data,
                    timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
                )

            response = self.unified_request(
                url=comlist["xlurl"], method='POST', data=data,
                timeout=(5, 15), custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"Intpro状态码:{response}")
            if response.status_code == 200:
                totalPage = int(response.json()['totalPage'])
                items = response.json()["data"]
                if items:
                    for item in items:
                        item['created_at'] = datetime.now()
                        item['data_source'] = 'Intellectual_property'
                        item['company_url'] = comlist["xlurl"]
                        item['company'] = comlist["company"]
                        self.Intellectual_property.insert_one(item)
                        item.pop('_id', None)  # 防止 ObjectId 污染
                    datalist.extend(items)
                    if page >= totalPage:
                        return datalist
                else:
                    logger.warning(f"无 {comlist['company']} 知识产权信息！！")
                    return None
                page += 1
            else:
                break

    # ================================================================
    # 商标采集
    # ================================================================

    def Trademark_f(self, url):
        """通过allTrademarkUrl获取tradeMarkUrlData"""
        params = {"provinceid": "100000"}

        def retry_func():
            return self.unified_request(
                url=url, method='GET', params=params,
                custom_cookie=self.cookie, timeout=(10, 15), retry_func=None
            )

        try:
            response = self.unified_request(
                url=url, method='GET', params=params,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
            )
            logger.info(f"Trademark_f状态码:{response}")
            if response.status_code == 200:
                match = re.search(r'var\s+tradeMarkUrlData\s*=\s*"(.*?)";', response.text)
                if match:
                    return "https://shiming.gsxt.gov.cn" + match.group(1)
                logger.info("未找到tradeMarkUrlData")
                return None
        except Exception as e:
            logger.info(f"Trademark_f异常：{e}")
            return None

    def Trademark_send(self, url, page):
        """商标分页数据采集"""
        while True:
            data = {"draw": page, "start": (page - 1) * 4, "length": "4"}

            def retry_func():
                return self.unified_request(
                    url=url, method='POST', data=data,
                    timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
                )
            try:
                response = self.unified_request(
                    url=url, method='POST', data=data,
                    timeout=(5, 15), custom_cookie=self.cookie, retry_func=retry_func
                )
                logger.info(f"Trademark_send状态码:{response}")
                if response.status_code == 200:
                    totalPage = int(response.json()['totalPage'])
                    items = response.json()["data"]
                    if items:
                        if page >= totalPage:
                            return items
                    else:
                        return None
                    page += 1
                else:
                    continue
            except Exception as e:
                logger.info(f"Trademark_send异常：{e}")
                break

    def Trademark_main(self, comlist, datalist, page):
        """获取商标分页数据"""
        trade_mark_url = self.Trademark_f(comlist["sburl"])
        if not trade_mark_url:
            logger.info("无法获取tradeMarkUrlData")
            return datalist
        logger.info(f"最终数据接口url:{trade_mark_url}")
        data = self.Trademark_send(trade_mark_url, page)
        if data:
            self.trademark_info.insert_many(data)
            logger.info(f"最终商标数据:{data}")
            return data
        else:
            logger.warning(f"无 {comlist['company']} 商标信息！！")

    # ================================================================
    # 辅助包装器
    # ================================================================

    def safe_call(self, func, *args, **kwargs):
        """统一异常处理的函数调用包装器"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.info(f"{func.__name__} 调用异常: {e}")
            return None

    # ================================================================
    # 板块数据采集方法（供 _process_single_company 调用）
    # 每个 _collect_xxx 独立采集一个板块，失败不影响其他板块
    # ================================================================

    def _get_annual_report_info(self, comlist, detailData, company_name):
        """【板块1】年报信息 — 提取企业联系电话 + 参保人数(企业规模)

        数据流: anCheYearInfo -> get_anCheId -> anreport -> anreport_f/s
        """
        try:
            aninfo = self.get_anCheId(comlist.get("nburl"))
            logger.info(f"[年报] anCheId结果: {aninfo}")
            if not aninfo:
                logger.warning(f"[年报] {company_name} 无年报信息")
                return detailData

            code = self.anreport(aninfo, comlist.get("banurl"))
            if not code:
                logger.warning(f"[年报] {company_name} 年报详情为空")
                return detailData

            phone = ""; staff = ""
            try:
                phone = self.anreport_f(code)
            except Exception as e:
                logger.error(f"[年报] 电话获取失败: {e}")
            try:
                staff = self.anreport_s(code)
            except Exception as e:
                logger.error(f"[年报] 规模获取失败: {e}")

            logger.info(f"[年报] 电话={phone}, 参保人数={staff}")
            detailData.update({"legalTelephone": phone, "staffSize": staff})
            return detailData
        except Exception as e:
            logger.error(f"[年报] 整体异常: {e}")
            return detailData

    def _collect_shareholder_data(self, comlist):
        """【板块2】股东出资信息 — data(出资明细) + type(股东类型)"""
        result_data = None; result_type = None
        try:
            gdurl = comlist.get("gdurl"); shaurl = comlist.get("shaurl")
            company = comlist.get("company", "unknown")
            if gdurl:
                result_data = self.safe_call(self.equity_pledge, "data", [gdurl, company], [], 1)
            if shaurl:
                result_type = self.safe_call(self.equity_pledge, "type", [shaurl, company], [], 1)
            logger.info(f"[股东] 出资={bool(result_data)}, 类型={bool(result_type)}")
            return result_data, result_type
        except Exception as e:
            logger.error(f"[股东] {e}")
            return None, None

    def _collect_business_change(self, comlist):
        """【板块3】工商变更记录 — alterInfoUrl"""
        try:
            if not comlist.get("bgurl"):
                return None
            result = self.safe_call(self.Brchange, comlist, [], 1)
            logger.info(f"[工商变更] 采集到 {len(result) if result else 0} 条")
            return result
        except Exception as e:
            logger.error(f"[工商变更] {e}")
            return None

    def _collect_intellectual_property(self, comlist):
        """【板块4】知识产权 — IntellectualInfoUrl"""
        try:
            if not comlist.get("xlurl"):
                return None
            result = self.safe_call(self.Intpro, comlist, [], 1)
            logger.info(f"[知识产权] 采集到 {len(result) if result else 0} 条")
            return result
        except Exception as e:
            logger.error(f"[知识产权] {e}")
            return None

    def _collect_trademark_data(self, comlist):
        """【板块5】商标信息 — allTrademarkUrl"""
        try:
            if not comlist.get("sburl"):
                return None
            result = self.safe_call(self.Trademark_main, comlist, [], 1)
            logger.info(f"[商标] 采集到 {len(result) if result else 0} 条")
            return result
        except Exception as e:
            logger.error(f"[商标] {e}")
            return None

    def _collect_food_check(self, comlist):
        """【板块6】食品检测信息"""
        try:
            if not comlist.get("spurl"):
                return None
            def retry_func():
                return self._collect_food_check(comlist)
            resp = self.unified_request(
                url=comlist["spurl"], method='POST',
                data={"draw": 1, "start": 0, "length": "10"},
                timeout=(10, 15), retry_func=retry_func
            )
            if resp.status_code == 200:
                items = resp.json().get("data", [])
                for item in items:
                    item['created_at'] = datetime.now()
                    item['company'] = comlist.get('company', '')
                if items:
                    self.mongo_db["food_check"].insert_many(items)
                logger.info(f"[食品检测] 采集到 {len(items)} 条")
                return items
            return None
        except Exception as e:
            logger.error(f"[食品检测] {e}")
            return None

    def _collect_product_quality(self, comlist):
        """【板块7】产品质量监督抽查"""
        try:
            if not comlist.get("cpjdurl"):
                return None
            def retry_func():
                return self._collect_product_quality(comlist)
            resp = self.unified_request(
                url=comlist["cpjdurl"], method='POST',
                data={"draw": 1, "start": 0, "length": "10"},
                timeout=(10, 15), retry_func=retry_func
            )
            if resp.status_code == 200:
                items = resp.json().get("data", [])
                for item in items:
                    item['created_at'] = datetime.now()
                    item['company'] = comlist.get('company', '')
                if items:
                    self.mongo_db["product_quality"].insert_many(items)
                logger.info(f"[产品质量] 采集到 {len(items)} 条")
                return items
            return None
        except Exception as e:
            logger.error(f"[产品质量] {e}")
            return None

    def _collect_random_inspection(self, comlist):
        """【板块8】双随机抽查结果"""
        try:
            if not comlist.get("ssjurl"):
                return None
            def retry_func():
                return self._collect_random_inspection(comlist)
            resp = self.unified_request(
                url=comlist["ssjurl"], method='POST',
                data={"draw": 1, "start": 0, "length": "10"},
                timeout=(10, 15), retry_func=retry_func
            )
            if resp.status_code == 200:
                items = resp.json().get("data", [])
                for item in items:
                    item['created_at'] = datetime.now()
                    item['company'] = comlist.get('company', '')
                if items:
                    self.mongo_db["random_inspection"].insert_many(items)
                logger.info(f"[双随机抽查] 采集到 {len(items)} 条")
                return items
            return None
        except Exception as e:
            logger.error(f"[双随机抽查] {e}")
            return None

    def _collect_admin_license(self, comlist):
        """【板块9】行政许可信息"""
        try:
            if not comlist.get("xzurl"):
                return None
            def retry_func():
                return self._collect_admin_license(comlist)
            resp = self.unified_request(
                url=comlist["xzurl"], method='POST',
                data={"draw": 1, "start": 0, "length": "10"},
                timeout=(10, 15), retry_func=retry_func
            )
            if resp.status_code == 200:
                items = resp.json().get("data", [])
                for item in items:
                    item['created_at'] = datetime.now()
                    item['company'] = comlist.get('company', '')
                if items:
                    self.mongo_db["admin_license"].insert_many(items)
                logger.info(f"[行政许可] 采集到 {len(items)} 条")
                return items
            return None
        except Exception as e:
            logger.error(f"[行政许可] {e}")
            return None

    # ================================================================
    # 采集编排
    # ================================================================

    def _process_single_company(self, info):
        """处理单个公司的全板块数据采集

        板块清单(9个):
          1.年报(电话+规模)  2.股东出资  3.工商变更  4.知识产权
          5.商标  6.食品检测  7.产品质量  8.双随机抽查  9.行政许可

        每个板块独立采集，失败不阻断其他板块。使用线程池并行加速。
        """
        company_name = info.get("name", "unknown")
        logger.info(f"\n{'='*60}\n采集公司: {company_name}\n{'='*60}")

        result = {"company": company_name, "detail": {}, "sections": {}}

        try:
            # 第0步：确保session新鲜
            self._ensure_session_fresh()
            # 第一步：获取公司详情页，提取基本信息 + 各板块URL
            comlist, detailData = self.vhpage(info)
            logger.info(f"[详情页] URL提取完成, 板块数={len(comlist)}")
            result["detail"] = detailData

            # 第二步：年报 (电话+规模) — 必须先获取，为detailData补充字段
            try:
                detailData = self._get_annual_report_info(comlist, detailData, company_name)
                result["detail"] = detailData
                result["sections"]["annual_report"] = {
                    "phone": detailData.get("legalTelephone", ""),
                    "staff_size": detailData.get("staffSize", "")
                }
            except Exception as e:
                logger.error(f"[年报] 采集失败: {e}")

            # 第三步：串行采集各板块数据 (避免cookie竞争，稳定性优先)
            section_collectors = [
                ("shareholder", lambda: self._collect_shareholder_data(comlist)),
                ("business_change", lambda: self._collect_business_change(comlist)),
                ("intellectual_property", lambda: self._collect_intellectual_property(comlist)),
                ("trademark", lambda: self._collect_trademark_data(comlist)),
                ("food_check", lambda: self._collect_food_check(comlist)),
                ("product_quality", lambda: self._collect_product_quality(comlist)),
                ("random_inspection", lambda: self._collect_random_inspection(comlist)),
                ("admin_license", lambda: self._collect_admin_license(comlist)),
            ]

            for name, fn in section_collectors:
                try:
                    data = fn()
                    result["sections"][name] = data
                except Exception as e:
                    logger.error(f"[{name}] 采集异常: {e}")
                    result["sections"][name] = None

            # 第四步：汇总输出
            section_summary = {
                k: (f"{len(v)}条" if isinstance(v, list) else bool(v))
                for k, v in result["sections"].items()
            }
            logger.success(f"[{company_name}] 采集完成: {section_summary}")
            return result

        except Exception as e:
            logger.error(f"[{company_name}] 处理异常: {e}")
            return result


    def detilinfo(self, company):
        """企业信息采集主入口

        流程:
          1. 搜索公司 -> 获取公司列表
          2. 遍历每个公司 -> 采集全板块数据(9个板块)
          3. 结果汇总输出
        """
        logger.info("*" * 80)
        logger.info(f"开始采集: {company}")
        logger.info("*" * 80)

        try:
            # 第一步：搜索公司
            logger.info("[搜索] 正在搜索公司...")
            datalist = self.searchcompany(company, 1)
            if not datalist:
                logger.error(f"[搜索] {company}: 未找到匹配企业")
                with open("没有数据企业.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now().isoformat()}\t{company}\n")
                return None
            logger.info(f"[搜索] 找到 {len(datalist)} 家企业")

            # 第二步：逐个采集
            all_results = []
            for idx, info in enumerate(datalist, 1):
                if not info.get("link"):
                    logger.warning(f"[{idx}/{len(datalist)}] {info.get('name')} 无详情链接，跳过")
                    continue
                logger.info(f"\n[{idx}/{len(datalist)}] 处理: {info.get('name')}")
                company_result = self._process_single_company(info)
                if company_result:
                    all_results.append(company_result)
                    self.append_processed_code(info.get("name", ""))

            # 第三步：汇总
            logger.success(f"\n{'='*60}")
            logger.success(f"采集完成! 共处理 {len(all_results)}/{len(datalist)} 家企业")
            for r in all_results:
                sections = r.get("sections", {})
                summary = {k: (f"{len(v)}条" if isinstance(v, list) else str(type(v).__name__)) for k, v in sections.items()}
                logger.info(f"  {r['company']}: {summary}")
            return all_results

        except Exception as e:
            logger.error(f"[主流程] {company} 采集异常: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    # ================================================================
    # 已处理标记
    # ================================================================

    def append_processed_code(self, company):
        """添加已处理的公司代码到内存集合"""
        try:
            if company:
                company_str = str(company).strip()
                if company_str:
                    self.processed_codes.add(company_str)
                    logger.debug(f"已标记公司 {company_str} 为已处理")
        except Exception as e:
            logger.error(f"添加已处理代码失败: {e}")


    def is_processed(self, company):
        """检查公司是否已处理"""
        if not company:
            return False
        return str(company).strip() in self.processed_codes


    def close_mongo_connection(self):
        """关闭MongoDB连接"""
        try:
            self.mongo_client.close()
            logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.info(f"关闭MongoDB连接失败: {e}")

    # ================================================================
    # 登录编排
    # ================================================================

    def next_login(self, user):
        """登录流程: WAF穿透 -> 获取公钥+fiKxeghI -> 极验验证 -> 登录"""
        logger.info(f"使用账号: {user.get('user', 'Unknown')}")
        try:
            self._publicKey, self.fiKxeghI = self.main_qe()
            try:
                resp = self.send()
                try:
                    success = self.loginuser(user, resp)
                    if success:
                        logger.success(f"账号 {user['user']} 登录完成")
                    else:
                        logger.error(f"账号 {user['user']} 登录失败")
                except Exception as e:
                    logger.info(f"loginuser登陆异常:{e}")
            except Exception as e:
                logger.info(f"jy_shibie验证码异常:{e}")
                raise TypeError("验证码识别异常！！")
        except Exception as e:
            logger.info(f"main_qe pass盾异常:{e}")
            raise Exception("访问首页异常！！")


    def main(self):
        """主方法 — 处理账号登录和数据采集"""
        num = 1
        try:
            # user = {"user": "18050400868", "pwd": "Anbo123456"}
            # user = {"user": "18965736502", "pwd": "HNg786346"}
            user = {"user": "17359191389", "pwd": "ASl57456"}
            if not user:
                logger.info("无法获取可用账号，程序退出")
                return
            self.next_login(user)
            company = "阿里巴巴"
            logger.info(f">>> 正在处理公司: 【{company}】 <<<")
            try:
                self.detilinfo(company)
                self.append_processed_code(company)
                num += 1
                logger.info(f"已处理【{num}】家公司")
            except Exception as e:
                logger.info(f"detilinfo异常:{e}")
                self.append_processed_code(company)
        except Exception as e:
            logger.info(f"主流程异常: {e}")
        finally:
            self.close_mongo_connection()


if __name__ == '__main__':
    gov = Govspider()
    gov.main()
