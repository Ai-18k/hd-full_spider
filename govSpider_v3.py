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
from redis import Redis

def proxy_list():
    # return {
    #     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user":"17773711437", "pwd":"Qa9Uu2kf", "proxy": "t152.juliangip.cc:15041"},
    #     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user":"17773711437", "pwd":"Qa9Uu2kf", "proxy": "t152.juliangip.cc:15041"},
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
                logger.info(f"iv8_env: 412页面无r='m' JS(非标准页面), 跳过iv8执行")
                return

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
                # 保存200页面内容供后续cookie刷新使用
                self._last_rs_content = response.text
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
                safe_update(self.cookies, response.cookies.get_dict())
                if response.status_code == 521:
                    logger.info(f"加速乐第一次请求的状态码:{response}")
                    data = self.jsl(response.text)
                    if data is None:
                        raise RuntimeError("jsl返回None, 第一层521解析失败")
                    ct_content = self.resp_jsl(data)
                elif response.status_code == 412:
                    logger.info(f"瑞数第一次请求的状态码:{response}")
                    ct_content = response.text
                elif response.status_code == 200:
                    logger.info(f"直接200, 跳过WAF")
                    ct_content = None
                    # 保存200页面作为_last_rs_content，供后续cookie刷新使用
                    self._last_rs_content = response.text
                else:
                    raise RuntimeError(f"意外状态码: {response.status_code}")

                if ct_content:
                    rs_content = self.first_req(ct_content)
                    self._last_rs_content = rs_content  # 保存用于后续 cookie 刷新
                    self.iv8_env(rs_content)
                # 携带完整 cookie 重新请求页面，拿到带 XHR hook 的真实页面 JS。
                _publicKey, fiKxeghI = self.get_publicKey()
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
        resp = requests.post("http://api.jfbym.com/api/YmServer/customApi", headers={"Content-Type": "application/json"}, json=data, timeout=15).json()
        return resp["data"]["data"] if resp.get("code") == 10000 else "232,145|159,107|61,34"

    def load_jy(self):
        params = {"captcha_id": self.captcha_id, "client_type": "web", "lang": "zh-cn"}
        resp = json.loads(requests.get(url=self.url_wou, params=params, headers=self.headers, timeout=15).text.replace("(", "").replace(")", ""))
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
            bl = [requests.get("https://static.geetest.com/" + u, timeout=15).content for u in data["ques_list"]]
            click_list = get_word_position(requests.get(data["imgs_url"], timeout=15).content, bl)
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
            logger.info(f"文字点选坐标:{click_smark}")
        elif data.get("type_name") == "phrase":
            resp_bytes = requests.get(url=data["slice_xiao"], timeout=15).content
            coord_raw = get_info(resp_bytes)
            # logger.info(f"语序识别原始: {coord_raw}")
            # get_info 返回 list of [x1,y1,x2,y2] 或 string "x,y|x,y"
            if isinstance(coord_raw, list):
                # list of bounding boxes → 转中心点
                click_list = [[(b[0]+b[2])//2, (b[1]+b[3])//2] for b in coord_raw if len(b) >= 4]
            elif isinstance(coord_raw, str):
                click_list = [[int(x), int(y)] for p in coord_raw.split("|")
                             if len(parts := p.split(",")) == 2 for x, y in [parts]]
            else:
                logger.warning(f"未知语序结果类型: {type(coord_raw)}")
                click_list = []
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
            logger.info(f"语序点选坐标:{click_smark}")
        elif data.get("type_name") == "icon":
            bl = [requests.get("https://static.geetest.com/" + u, timeout=15).content for u in data["ques_list"]]
            click_list = get_icon_position(requests.get(data["imgs_url"], timeout=15).content, bl)
            click_smark = [[int(i[0]) * 33, int(int(i[1]) * 49.7)] for i in click_list]
            logger.info(f"图标点选坐标:{click_smark}")
        elif data.get("type_name") == "nine":
            tg = requests.get(data["bg_da"], timeout=15).content; bg = requests.get(data["slice_xiao"], timeout=15).content
            im = Image.open(BytesIO(bg)).convert("RGBA"); buf = BytesIO(); im.save(buf, format="PNG")
            click_smark, qc = get_nine_position(tg, split_image(buf.getvalue()), data["nine_nums"])
            logger.info(f"九宫格点选坐标:{click_smark}")
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
                logger.info(f"[验证码] 提交验证 (类型={data.get('type_name','?')})...")
                resp = json.loads(requests.get("https://gcaptcha4.geetest.com/verify", headers=h, params=params, timeout=15).text.replace("(", "").replace(")", ""))
                if resp["data"]["result"] == "success":
                    logger.success("验证码识别成功！！")
                    return {"captcha_output": resp["data"]["seccode"]["captcha_output"], "gen_time": resp["data"]["seccode"]["gen_time"],
                            "lot_number": resp["data"]["seccode"]["lot_number"], "pass_token": resp["data"]["seccode"]["pass_token"]}
                else:
                    logger.warning(f"[验证码] 结果: {resp['data'].get('result')}, 原因: {resp['data'].get('fail_reason', '?')}")
            except Exception as e:
                logger.warning(f"验证码识别失败 ({attempt+1}/10): {e}")
                if attempt == 9: raise


class Govspider(JY):

    def __init__(self):
        super().__init__()
        # self.conn = Redis(host='192.168.6.172', port=14771, db=10, password='fer@nhaweif576KUG')
        # self.local_conn = Redis("192.168.6.175", 15456, 0, "fer@nhaweif576KUG", socket_connect_timeout=1155)
        self.conn = Redis(host='192.168.6.167', port=10824, db=10, password='e8Mzr}$%jsuCxKn4r#mm')
        self.local_conn = Redis("192.168.6.167", 14228, 0, "uf$vU_1~wA0mB@Z+", socket_connect_timeout=1155)
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
        # MongoDB 连接超时 3s（避免阻塞采集流程），服务端超时 5s
        self.mongo_client = MongoClient(host="127.0.0.1", port=27017,
                                         serverSelectionTimeoutMS=3000,
                                         connectTimeoutMS=3000,
                                         socketTimeoutMS=5000)
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

        # 浏览器 RS6 Hook 会自动给所有 XHR 请求 URL 追加 ?fiKxeghI=<token>
        # Python 请求必须手动追加，否则被 400/412/创宇盾拦截
        # 登录和搜索请求例外：登录 POST body 已含 fiKxeghI；搜索 URL 加 fiKxeghI 反致 400
        # 详情页例外：fiKxeghI 值由 RS6 hook 变换生成(非原 cookie)，蜘蛛无法复现
        fi = self.fiKxeghI or self.cookies.get("dUs8TeLcaHgjP", "")
        if fi and "fiKxeghI" not in url and "shiming.gsxt.gov.cn" in url \
                and "login-request" not in url \
                and "corp-query-search" not in url \
                and "%7B" not in url:
            url = url + ("&" if "?" in url else "?") + "fiKxeghI=" + fi

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
            # 生成带时间戳的唯一文件名（避免覆盖）
            if response.status_code == 200:
                if "NGIDERRORCODE" in response.text:
                    logger.error("账号异常！！切换账号。。。。")
                    user = self.ltouser()
                    self.next_login(user)
                    raise ConnectionError("账号异常！！")
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
                # 保存412页面内容，供后续iv8刷新使用
                self._last_rs_content = response.text
                safe_update(self.cookies, response.cookies.get_dict())
                try:
                    self.iv8_env(response.text)
                except RuntimeError as e:
                    # iv8_env r='m' 匹配失败(非标准412页面如详情页) → 完整session恢复
                    logger.info(f"iv8_env跳过: {e}, 走完整session恢复...")
                except Exception as e:
                    logger.info(f"iv8_env失败({e}), 尝试full session恢复...")
                    try:
                        self._ensure_session_fresh()
                    except Exception as e2:
                        logger.warning(f"Session恢复也失败: {e2}")
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
                logger.info(f"unified_request收到521，触发session恢复...")
                safe_update(self.cookies, response.cookies.get_dict())
                self._ensure_session_fresh()
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
            elif response.status_code == 405:
                with open("Node_control/unified_request_405.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                logger.warning(f"[unified_request] 405 Method Not Allowed: {url}, 刷新session后重试...")
                self._ensure_session_fresh()
                if retry_func:
                    return retry_func()
                else:
                    raise ConnectionError("405状态码，需要重试")
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
        if self._last_rs_content is None:
            logger.warning("get_fresh_cookie: _last_rs_content is None, 跳过iv8刷新")
        elif not isinstance(self._last_rs_content, str):
            logger.error(f"get_fresh_cookie: _last_rs_content 类型异常 ({type(self._last_rs_content).__name__}), 跳过iv8刷新")
        else:
            try:
                self.iv8_env(self._last_rs_content)
            except Exception as e:
                logger.error(f"get_fresh_cookie: {e}")
        return self.cookies.copy() if isinstance(self.cookies, dict) else {}


    def _ensure_session_fresh(self):
        """轻量级探测：GET首页检查cookie是否新鲜，遇521/412自动恢复"""
        # 用文档请求头而非 XHR 头（index.html 是页面加载，不是 API）
        probe_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": self.headers.get("User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/148.0.0.0 Safari/537.36"),
            "sec-ch-ua": self.headers.get("sec-ch-ua", ""),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
        }
        for attempt in range(3):
            try:
                resp = requests.get(
                    "https://shiming.gsxt.gov.cn/index.html",
                    headers=probe_headers, cookies=self.cookies,
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
                        if data is None:
                            logger.error("[Session] jsl返回None, 跳过本次刷新")
                            continue
                        ct_content = self.resp_jsl(data)
                        self._last_rs_content = self.first_req(ct_content)
                    else:  # 412 — 需通过 first_req 生成 CT cookie 再拿 RS6 页面
                        safe_update(self.cookies, resp.cookies.get_dict())
                        try:
                            self._last_rs_content = self.first_req(resp.text)
                        except Exception as e:
                            logger.warning(f"[Session] first_req失败: {e}, 尝试直接用iv8...")
                            self._last_rs_content = resp.text
                    self.iv8_env(self._last_rs_content)
                elif resp.status_code in (403, 404):
                    logger.warning(f"[Session] 探测返回{resp.status_code}, 可能IP受限")
                    return False
                else:
                    # 302/405/500/503等 — 不一定是会话过期，返回True继续
                    logger.info(f"[Session] 探测返回{resp.status_code}, 视为会话正常")
                    safe_update(self.cookies, resp.cookies.get_dict())
                    return True
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
                                logger.warning(f"登录异常: {rj}")
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
                        # iv8_env 刷新了 dUs8TeLcaHgjP，必须同步更新 fiKxeghI
                        self.fiKxeghI = self.cookies.get("dUs8TeLcaHgjP", "")
                        logger.success("首页cookie已更新")
                    return True
                else:
                    logger.error(f"登陆异常响应码:{response}")
            except Exception as e:
                logger.error(f"loginuser登陆失败: {e}")
        logger.error(f"登录失败: {response.status_code}")
        return False


    # ================================================================
    # 搜索接口 — 动态 token + 稳定性增强
    # ================================================================
    def _extract_search_token(self, html=None):
        """从页面提取搜索 token（多模式 + 诊断日志）

        token 存在于 index.html 或搜索页面的 JS 变量中，每次会话不同。
        优先级：meta > JS变量 > input hidden
        """
        sources = []
        # 用文档请求头获取 index.html（不能用 XHR 头，会被 405）
        page_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": self.headers.get("User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/148.0.0.0 Safari/537.36"),
        }
        if html is None:
            # 优先尝试搜索页（登录后实际所在的页面），index.html可能被405拒绝
            for try_url in [
                "https://shiming.gsxt.gov.cn/corp-query-search-1.html",
                "https://shiming.gsxt.gov.cn/index.html",
            ]:
                try:
                    resp = requests.get(try_url,
                                        headers=page_headers, cookies=self.cookies,
                                        proxies=self.proxies, timeout=(10, 15), verify=False)
                    if resp.status_code == 200:
                        safe_update(self.cookies, resp.cookies.get_dict())
                        html = resp.text
                        sources.append(f"{try_url.split('/')[-1]}(200)")
                        break
                    else:
                        logger.warning(f"[Token] {try_url}返回{resp.status_code}")
                except Exception as e:
                    logger.warning(f"[Token] 获取{try_url}失败: {e}")
            if html is None:
                logger.warning("[Token] 所有页面获取失败，使用默认token=2016")
                return "2016"

        # Pattern 1: JS变量 var token = "..."
        m = re.search(r'var\s+token\s*=\s*"(\d+)"', html)
        if m:
            token = m.group(1)
            logger.info(f"[Token] 从JS变量提取: {token} (来源: {sources})")
            return token

        # Pattern 2: meta标签
        m = re.search(r'<meta[^>]+name=["\']token["\'][^>]+content=["\'](\d+)["\']', html)
        if m:
            token = m.group(1)
            logger.info(f"[Token] 从meta提取: {token}")
            return token

        # Pattern 3: input hidden
        m = re.search(r'<input[^>]+name=["\']token["\'][^>]+value=["\'](\d+)["\']', html)
        if m:
            token = m.group(1)
            logger.info(f"[Token] 从input提取: {token}")
            return token

        # Pattern 4: URL参数中的 token=
        m = re.search(r'[?&]token=(\d+)', html)
        if m:
            token = m.group(1)
            logger.info(f"[Token] 从URL参数提取: {token}")
            return token

        # 诊断日志
        all_vars = re.findall(r'var\s+(\w+)', html)
        logger.warning(f"[Token] 未找到token! 页面JS变量: {all_vars[:20]}")
        return ""


    def _get_search_token(self):
        """获取搜索 token，失败重试3次"""
        for attempt in range(3):
            token = self._extract_search_token()
            if token:
                return token
            logger.warning(f"[Token] 第{attempt+1}次提取失败，重试...")
            time.sleep(2)
        logger.error("[Token] 3次提取均失败，使用空字符串（可能不需要token）")
        return ""


    def _search_preflight(self):
        """浏览器搜索前的前置验证请求

        浏览器在搜索前会同步请求两个端点：
        1. /corp-query-custom-geetest-image.gif?v=TIMESTAMP — 设置 browser_version
        2. /corp-query-geetest-validate-input.html?token=TOKEN — 验证 token
        RS6 XHR hook 自动给请求加 fiKxeghI 参数。
        """
        import time as _time
        try:
            ts = str(int(_time.time() * 1000) % 1000)  # 分钟+秒的简化版
            fi = self.fiKxeghI or self.cookies.get("dUs8TeLcaHgjP", "")
            img_url = f"https://shiming.gsxt.gov.cn/corp-query-custom-geetest-image.gif?v={ts}"
            if fi:
                img_url += f"&fiKxeghI={fi}"
            resp = requests.get(img_url, headers=self.headers, cookies=self.cookies,
                                proxies=self.proxies, timeout=10)
            logger.info(f"[预检] image.gif: {resp.status_code}")
        except Exception as e:
            logger.warning(f"[预检] image.gif失败: {e}")


    def _search_paginate(self, company, params, data_template, page=1, max_pages=50):
        """统一的搜索分页方法

        第1页: POST /corp-query-search-1.html (初始搜索)
        第2+页: GET /corp-query-search-advancetest.html (翻页, 与浏览器一致)
        """
        all_data = []
        seen_names = set()

        for pg in range(page, page + max_pages):
            if pg == 1:
                # 首页：POST 搜索
                url = "https://shiming.gsxt.gov.cn/corp-query-search-1.html"
                method = "POST"
                req_data = dict(data_template)
                req_data["page"] = str(pg)
                req_data["fiKxeghI"] = self.fiKxeghI or self.cookies.get("dUs8TeLcaHgjP", "")
                for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]:
                    req_data[k] = params.get(k, "")
                rt = lambda: self._search_paginate_retry(company, params, data_template, pg)
                r = self.unified_request(
                    url=url, method=method, data=req_data,
                    timeout=(10, 20), custom_cookie=self.cookie, retry_func=rt)
            else:
                # 翻页：GET advancetest.html
                url = "https://shiming.gsxt.gov.cn/corp-query-search-advancetest.html"
                method = "GET"
                req_params = {
                    "searchword": company, "page": str(pg),
                    "tab": data_template.get("tab", "ent_tab"),
                    "province": data_template.get("province", ""),
                    "captchaId": "b608ae7850d2e730b89b02a384d6b9cc",
                    "token": data_template.get("token", ""),
                    "geetest_challenge": "", "geetest_validate": "", "geetest_seccode": "",
                }
                for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]:
                    req_params[k] = params.get(k, "")
                rt = lambda: self._search_paginate_retry(company, params, data_template, pg)
                r = self.unified_request(
                    url=url, method=method, params=req_params,
                    timeout=(10, 20), retry_func=rt)

            if r.status_code != 200:
                logger.warning(f"[搜索] {company} 第{pg}页返回{r.status_code}，终止翻页")
                break

            if "NGIDERRORCODE" in r.text:
                logger.error(f"[搜索] 账号异常，终止翻页")
                user = self.ltouser()
                self.next_login(user)
                return self.searchcompany(company, page)

            html = etree.HTML(r.text)

            # 检查是否有结果
            if not html.xpath("//*[@id='advs']/div/div[2]"):
                logger.info(f"[搜索] {company} 第{pg}页无结果，终止翻页")
                break

            page_data = self.getdata(html)
            if not page_data:
                logger.info(f"[搜索] {company} 第{pg}页解析为空，终止翻页")
                break

            # 跨页去重
            new_count = 0
            for item in page_data:
                name = item.get("name", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_data.append(item)
                    new_count += 1

            logger.info(f"[搜索] {company} 第{pg}页: {new_count}条新数据 (累计{len(all_data)})")

            # 检查总页数（从HTML提取）
            try:
                tp = int(html.xpath("//div[@class='search_result']/span/text()")[0])
            except:
                try:
                    tp = int(html.xpath("//*[@id='advs']/div/div[1]/span/text()")[0])
                except:
                    tp = -1

            # 计算总页数：每页约10条
            if tp > 0:
                total_pages = (tp + 9) // 10
                logger.info(f"[搜索] {company} 共{tp}条结果, 约{total_pages}页")
                if pg >= total_pages:
                    logger.info(f"[搜索] {company} 已到最后一页")
                    break
            else:
                # 无法获取总数，保守判断：本页少于10条即为最后一页
                if len(page_data) < 10:
                    logger.info(f"[搜索] {company} 本页不足10条，判定为最后一页")
                    break

        logger.info(f"[搜索] {company} 完成: 共{len(all_data)}条, {pg - page + 1}页")
        return all_data


    def _search_paginate_retry(self, company, params, data_template, page):
        """搜索翻页的重试函数（刷新验证码+RS6 cookie后重试）

        第1页 POST /corp-query-search-1.html
        第2+页 GET /corp-query-search-advancetest.html
        """
        try:
            p2 = self.send()
            for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]:
                params[k] = p2[k]
        except Exception as e:
            logger.warning(f"[搜索] 刷新验证码失败: {e}")

        if page == 1:
            data = dict(data_template)
            data["page"] = str(page)
            data["fiKxeghI"] = self.fiKxeghI or self.cookies.get("dUs8TeLcaHgjP", "")
            for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]:
                data[k] = params.get(k, "")
            return self.unified_request(
                url="https://shiming.gsxt.gov.cn/corp-query-search-1.html",
                method="POST", data=data,
                timeout=(10, 20), retry_func=None)
        else:
            req_params = {
                "searchword": company, "page": str(page),
                "tab": data_template.get("tab", "ent_tab"),
                "province": data_template.get("province", ""),
                "captchaId": "b608ae7850d2e730b89b02a384d6b9cc",
                "token": data_template.get("token", ""),
                "geetest_challenge": "", "geetest_validate": "", "geetest_seccode": "",
            }
            for k in ["lot_number", "captcha_output", "pass_token", "gen_time"]:
                req_params[k] = params.get(k, "")
            return self.unified_request(
                url="https://shiming.gsxt.gov.cn/corp-query-search-advancetest.html",
                method="GET", params=req_params,
                timeout=(10, 20), retry_func=None)


    def searchcompany(self, company, page=1):
        """搜索公司 — 自动翻页获取全量结果

        流程: 提取token → 获取极验验证码 → POST搜索 → 自动翻页
        使用 Govspider 默认 XHR headers + 每次刷新 RS6 cookie
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Step 1: 获取动态 token
                token = self._get_search_token()
                if not token:
                    # 尝试从已缓存的 _last_rs_content 提取
                    if self._last_rs_content:
                        token = self._extract_search_token(self._last_rs_content)
                    if not token:
                        logger.warning(f"[搜索] 未获取到token，使用空值尝试")

                # Step 2: 获取极验验证码
                p = self.send()
                logger.info(f"[搜索] 验证码获取成功")

                # Step 2.5: 浏览器前置验证请求（corp-query-custom-geetest-image.gif）
                self._search_preflight()

                # Step 3: 首次搜索 — 用 Govspider 默认 XHR headers
                data_template = {
                    "tab": "ent_tab", "tab_ekeyareas": "0", "province": "100000",
                    "geetest_challenge": "", "geetest_validate": "", "geetest_seccode": "",
                    "captchaId": "b608ae7850d2e730b89b02a384d6b9cc",
                    "token": token, "searchword": company, "page": str(page)
                }

                # 翻页采集
                result = self._search_paginate(
                    company=company, params=p,
                    data_template=data_template, page=page
                )
                return result

            except Exception as e:
                logger.warning(f"[搜索] {company} 第{attempt+1}次尝试失败: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"[搜索] {company} {max_retries}次尝试均失败")
                    return []
                time.sleep(3)

        return []


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
    def vhpage(self, info, _retry=0):
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

        # 重试前先刷新session，避免无限递归
        if _retry > 0:
            logger.warning(f"[vhpage] 第{_retry}次重试，刷新session...")
            time.sleep(2 * _retry)
            self._ensure_session_fresh()

        # 最大重试次数限制
        MAX_VHPAGE_RETRIES = 5
        if _retry >= MAX_VHPAGE_RETRIES:
            logger.error(f"[vhpage] {info.get('name','?')} 详情页{MAX_VHPAGE_RETRIES}次重试均失败，放弃")
            return None, None

        # 浏览器 RS6 Hook 自动给 XHR URL 追加 fiKxeghI，但 GET 请求的
        # fiKxeghI 值由 RS6 hook 内部函数变换生成(非 dUs8TeLcaHgjP 原值)
        # 蜘蛛无法复现该变换 → 不追加 fiKxeghI，直接请求原始 URL
        detail_url = info["link"]

        # 详情页在浏览器中是通过 RS6 XHR 加载的，使用和搜索相同的 XHR 头
        def retry_func():
            return self.unified_request(
                url=detail_url, method='GET',
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None
            )

        response = self.unified_request(
            url=detail_url, method='GET',
            timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func
        )
        logger.info(f"vhpage状态码:{response}")

        if response and response.status_code == 200:
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
                # spurl = extract_url("getFoodChkInfoUrl")    # 食品检测
                gdurl = extract_url("insInvinfoUrl")        # 股东出资
                xlurl = extract_url("IntellectualInfoUrl")  # 知识产权
                nburl = extract_url("anCheYearInfo")        # 年报年份
                banurl = extract_url("annRepDetailUrl")     # 年报详情
                sburl = extract_url("allTrademarkUrl")      # 商标
                # cpjdurl = extract_url("eproquacheckUrl")    # 产品质量
                # ssjurl = extract_url("getDrRaninsResUrl")   # 双随机抽查
                xzurl = extract_url("nLicUrl")              # 行政许可

                logger.info(f"工商变更:{bgurl}\n股东信息:{shaurl}\n股东出资:{gdurl}\n知识产权:{xlurl}\n"
                            f"年报年份:{nburl}\n年报详情:{banurl}\n商标:{sburl}\n行政许可:{xzurl}\n")
                # --- 提取基本工商信息 （页面结构: div.yyzz-all > div.top + table.yyzz-table）---
                result = {
                    "companyName": "",
                    "companyType": "",
                    "registeredAddress": "",
                    "legalName": "",
                    "dateOfEstablishment": "",
                    "registrationAuthority": "",
                    "registrationStatus": "",
                    "businessScope": "",
                    "tyxydm": "",
                    "yyqx": "",
                    "gszch": "",
                    "registeredCapital": ""
                }

                # 字段映射（clean后的key → result key）
                field_map = {
                    "统一社会信用代码": "tyxydm",
                    "名称": "companyName",
                    "企业名称": "companyName",
                    "注册号": "gszch",
                    "类型": "companyType",
                    "住所": "registeredAddress",
                    "经营场所": "registeredAddress",
                    "营业场所": "registeredAddress",
                    "法定代表人": "legalName",
                    "负责人": "legalName",
                    "经营者": "legalName",
                    "投资人": "legalName",
                    "执行事务合伙人": "legalName",
                    "注册资本": "registeredCapital",
                    "成立日期": "dateOfEstablishment",
                    "注册日期": "dateOfEstablishment",
                    "登记机关": "registrationAuthority",
                    "登记状态": "registrationStatus",
                    "经营范围": "businessScope",
                    "营业期限": "yyqx",
                }

                def clean_key(text):
                    """清洗字段名中的特殊空白字符（BeautifulSoup已将&emsp;/&thinsp;/&nbsp;解码为Unicode）"""
                    text = re.sub(r'[\s\u00a0\u2002\u2003\u2009]+', '', text)
                    text = text.replace("：", "").replace(":", "").strip()
                    return text

                yyzz_div = soup.find("div", class_="yyzz-all")
                if yyzz_div:
                    # 1. 从 div.top 提取统一社会信用代码
                    top_div = yyzz_div.find("div", class_="top")
                    if top_div:
                        top_b = top_div.find("b")
                        if top_b:
                            key_clean = clean_key(top_b.get_text())
                            # 值在 <b> 后面的文本节点
                            val_text = top_div.get_text().replace(top_b.get_text(), "").strip()
                            if "统一社会信用代码" in key_clean and val_text:
                                result["tyxydm"] = val_text

                    # 2. 从 table.yyzz-table 提取所有字段
                    table = yyzz_div.find("table", class_="yyzz-table")
                    if table:
                        for tr in table.find_all("tr"):
                            tds = tr.find_all("td")
                            if len(tds) >= 2:
                                key_text = clean_key(tds[0].get_text())
                                val_text = tds[1].get_text(strip=True)
                                if not key_text or not val_text:
                                    continue
                                matched = False
                                for fk, fv in field_map.items():
                                    if fk in key_text:
                                        if fv == "dateOfEstablishment":
                                            dm = re.match(r"(\d{4})年(\d{2})月(\d{2})日", val_text)
                                            result[fv] = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}" if dm else val_text
                                        else:
                                            result[fv] = val_text
                                        matched = True
                                        break
                                if not matched:
                                    logger.debug(f"[vhpage] 未匹配字段: key='{key_text}' val='{val_text[:50]}'")

                # 3. 营业期限后处理
                if result.get("yyqx") and "至  长期" in str(result["yyqx"]):
                    result["yyqx"] = (result.get("dateOfEstablishment") or "") + result["yyqx"]

                # 构建返回
                comlist = {
                    "company": info["name"],
                    "bgurl": bgurl,
                    "shaurl": shaurl,
                    # "spurl": spurl,
                    "gdurl": gdurl,
                    "xlurl": xlurl,
                    "nburl": nburl,
                    "banurl": banurl,
                    "sburl": sburl,
                    # "cpjdurl": cpjdurl,
                    # "ssjurl": ssjurl,
                    "xzurl": xzurl
                }
                return comlist, result
        else:
            try:
                logger.info("vhpage代理信息:{}".format(requests.get("https://myip.ipip.net", proxies=self.proxies, timeout=(5, 10)).text))
            except:
                pass
            return self.vhpage(info, _retry=_retry + 1)

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

    def anreport(self, aninfo, url, _retry=0):
        """获取年报详情页的 ancheid（用于后续获取电话+规模）"""
        MAX_ANREPORT_RETRIES = 5
        if _retry >= MAX_ANREPORT_RETRIES:
            logger.error(f"anreport: {MAX_ANREPORT_RETRIES}次重试均失败")
            return None
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
            if response and response.status_code == 200:
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
            return self.anreport(aninfo, url, _retry=_retry + 1)

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
                return datalist if datalist else None

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
                    logger.info(f"【*】工商变更：{item}")
                    self.equity_collection.insert_one(item)
                    item.pop('_id', None)  # 防止 ObjectId 污染
                datalist.extend(items)
                if page >= totalPage:
                    return datalist
                page += 1
            else:
                return datalist if datalist else None
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
                        logger.info(f"【*】知识产权：{item}")
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
                return datalist if datalist else None
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
                    logger.info(f"【*】商标：{items}")
                    if items:
                        if page >= totalPage:
                            return items
                    else:
                        return None
                    page += 1
                else:
                    logger.warning(f"Trademark_send非200状态码: {response.status_code}")
                    return None
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
            url = comlist["spurl"]
            data = {"draw": 1, "start": 0, "length": "10"}
            retry_func = lambda: self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None)
            resp = self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func)
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
            url = comlist["cpjdurl"]
            data = {"draw": 1, "start": 0, "length": "10"}
            retry_func = lambda: self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None)
            resp = self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func)
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
            url = comlist["ssjurl"]
            data = {"draw": 1, "start": 0, "length": "10"}
            retry_func = lambda: self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None)
            resp = self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func)
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
            url = comlist["xzurl"]
            data = {"draw": 1, "start": 0, "length": "10"}
            retry_func = lambda: self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=None)
            resp = self.unified_request(
                url=url, method='POST', data=data,
                timeout=(10, 15), custom_cookie=self.cookie, retry_func=retry_func)
            if resp.status_code == 200:
                items = resp.json().get("data", [])
                if items:
                    for item in items:
                        item['created_at'] = datetime.now()
                        item['company'] = comlist.get('company', '')
                        logger.info(f"【*】行政许可数据:{item}")
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
            # 第一步：获取公司详情页，提取基本信息 + 各板块URL
            # 注意：不调用 _ensure_session_fresh()——它可能改变cookie导致搜索返回的详情页链接失效
            comlist, detailData = self.vhpage(info)
            if comlist is None:
                logger.error(f"[详情页] {company_name} 详情页获取失败，跳过该公司")
                return result
            logger.info(f"[详情页] URL提取完成, 板块数={len(comlist)}")
            # 第二步：年报 (电话+规模) — 必须先获取，为detailData补充字段
            try:
                iphone = self._get_annual_report_info(comlist, detailData, company_name)
                detailData["staff_size"] = iphone .get("staffSize", "")
                detailData["legalTelephone"]= iphone .get("legalTelephone", "")
            except Exception as e:
                logger.error(f"[年报] 采集失败: {e}")
            result["detail"] = detailData
            logger.info(f"【*】工商数据结果:{detailData}")
            # 第三步：串行采集各板块数据 (避免cookie竞争，稳定性优先)
            section_collectors = [
                ("shareholder", lambda: self._collect_shareholder_data(comlist)),
                ("business_change", lambda: self._collect_business_change(comlist)),
                ("intellectual_property", lambda: self._collect_intellectual_property(comlist)),
                ("trademark", lambda: self._collect_trademark_data(comlist)),
                # ("food_check", lambda: self._collect_food_check(comlist)),
                # ("product_quality", lambda: self._collect_product_quality(comlist)),
                # ("random_inspection", lambda: self._collect_random_inspection(comlist)),
                ("admin_license", lambda: self._collect_admin_license(comlist)),
            ]

            # 每2个板块后刷新session（RS6 cookie TTL<1s）
            for i, (name, fn) in enumerate(section_collectors):
                if i > 0 and i % 2 == 0:
                    self._ensure_session_fresh()
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
                    logger.success(f"【*】最终工商数据:{company_result['detail']}")
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
    # 已处理标记 (内存 + MongoDB 持久化)
    # ================================================================
    @property
    def processed_collection(self):
        """获取或创建 processed_companies 集合"""
        if not hasattr(self, '_processed_collection'):
            self._processed_collection = self.mongo_db["processed_companies"]
            # 确保有索引加速查询
            try:
                self._processed_collection.create_index("company", unique=True)
            except Exception:
                pass
        return self._processed_collection


    def _load_processed_from_mongo(self):
        """从 MongoDB 加载已处理公司名单到内存"""
        try:
            cursor = self.processed_collection.find({}, {"company": 1, "_id": 0})
            count = 0
            for doc in cursor:
                name = doc.get("company", "")
                if name:
                    self.processed_codes.add(name)
                    count += 1
            logger.info(f"[去重] 从MongoDB加载 {count} 条已处理记录")
        except Exception as e:
            logger.warning(f"[去重] 加载MongoDB记录失败: {e}")


    def append_processed_code(self, company):
        """添加已处理公司到内存 + MongoDB（持久化断点）"""
        try:
            if company:
                company_str = str(company).strip()
                if company_str:
                    self.processed_codes.add(company_str)
                    # 持久化写入 MongoDB
                    try:
                        self.processed_collection.update_one(
                            {"company": company_str},
                            {"$set": {"company": company_str, "processed_at": datetime.now()}},
                            upsert=True
                        )
                    except Exception as e:
                        logger.warning(f"[去重] MongoDB写入失败: {e}")
                    logger.info(f"[去重] 已标记: {company_str}")
        except Exception as e:
            logger.error(f"[去重] 标记失败: {e}")


    def is_processed(self, company):
        """检查公司是否已处理（先查内存，再查MongoDB兜底）"""
        if not company:
            return False
        company_str = str(company).strip()
        if company_str in self.processed_codes:
            return True
        # 兜底：查 MongoDB（内存集合可能在重启后为空）
        try:
            if self.processed_collection.find_one({"company": company_str}):
                self.processed_codes.add(company_str)  # 回填内存
                return True
        except Exception:
            pass
        return False

    # ================================================================
    # 公司列表输入
    # ================================================================

    @staticmethod
    def _load_companies_from_file(filepath="companies.txt"):
        """从文件读取公司名列表（每行一个）"""
        companies = []
        try:
            if not os.path.exists(filepath):
                logger.warning(f"[输入] {filepath} 不存在，使用默认测试公司")
                return ["测试公司"]
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    name = line.strip()
                    if name and not name.startswith("#"):  # 支持注释行
                        companies.append(name)
            logger.info(f"[输入] 从 {filepath} 读取 {len(companies)} 家公司")
        except Exception as e:
            logger.error(f"[输入] 读取文件失败: {e}")
        return companies

    def close_mongo_connection(self):
        """关闭MongoDB连接"""
        try:
            self.mongo_client.close()
            logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.info(f"关闭MongoDB连接失败: {e}")


    def ltouser(self):
        # 如果没有当前账号，从主队列获取
        user = self.conn.lpop("gov:user")
        if user is None:
            # 检查是否有可重用的账号（24小时过期）
            current_time = int(time.time())
            for user_data in self.conn.smembers("gov:already"):
                # 检查是否超过24小时
                # if current_time - user_obj.get("end_time", 0) > 86400:
                self.conn.lpush("gov:user", user_data)
            user = self.conn.lpop("gov:user")
            self.conn.srem("gov:already", user)
            user_obj = json.loads(user.decode("utf-8"))
            # user_obj["end_time"] = int(time.time())
            old_user = self.conn.get(self.CURRENT_ACCOUNT_KEY)
            self.conn.sadd("gov:already", old_user)
            self.conn.set(self.CURRENT_ACCOUNT_KEY, json.dumps(user_obj))
            return user_obj
        else:
            user_obj = json.loads(user.decode("utf-8"))
            self.conn.srem("gov:already", user)
            # 更新使用时间
            # user_obj["end_time"] = int(time.time())
            # 检查并移除重复账号
            # self.remove_duplicate_from_used_set(user_obj)
            # 设置当前账号
            old_user=self.conn.get(self.CURRENT_ACCOUNT_KEY)
            self.conn.sadd("gov:already", old_user)
            self.conn.set(self.CURRENT_ACCOUNT_KEY, json.dumps(user_obj))
            return user_obj

    def swich_user(self):
        """获取可用账号，如果没有可用账号则重新分配"""
        # 首先尝试从当前账号key获取账号
        current_account = self.conn.get(self.CURRENT_ACCOUNT_KEY)
        if current_account:
            user_obj = json.loads(current_account.decode("utf-8"))
            return user_obj


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

    # ================================================================
    # 批量采集主循环
    # ================================================================
    def main(self, companies=None, company_file="companies.txt",
             user=None, continuous=False, interval_range=(5, 15)):
        """批量采集主入口

        Args:
            companies: 公司名列表（None则从文件读取）
            company_file: 公司名文件路径（每行一个）
            user: 登录账号 dict 如 {"user": "...", "pwd": "..."}
            continuous: True=持续运行（即使列表处理完也等待新公司）
            interval_range: 公司之间休眠秒数范围 (min, max)
        """
        # 默认账号
        if user is None:
            # user = {"user": "17359191389", "pwd": "ASl57456"}
            # user = {"user": "19225906427", "pwd": "hjS564789"}
            # user = {"user": "18965736502", "pwd": "HNg786346"}
            # user = {"user": "18060829306", "pwd": "Kof989345"}
            # user = {"user": "15391558490", "pwd": "Dlj199106"}
            user = self.swich_user()

        # 加载已处理记录（断点续采）
        self._load_processed_from_mongo()

        # 加载公司列表
        if companies is None:
            companies = self._load_companies_from_file(company_file)

        if not companies:
            logger.error("[主流程] 没有可处理的公司")
            return

        total = len(companies)
        success_count = 0
        fail_count = 0
        skipped_count = 0

        logger.info("=" * 60)
        logger.info(f"批量采集启动: 共 {total} 家公司")
        logger.info(f"已处理(跳过): {len(self.processed_codes)} 家")
        logger.info(f"账号: {user.get('user', 'N/A')}")
        logger.info("=" * 60)

        logged_in = False

        for idx, company in enumerate(companies, 1):
            company = company.strip()
            if not company:
                continue

            # 去重检查
            # if self.is_processed(company):
            if False:
                logger.info(f"[{idx}/{total}] {company} — 已处理，跳过")
                skipped_count += 1
                continue

            logger.info(f"\n{'=' * 50}")
            logger.info(f"[{idx}/{total}] 处理: {company}")
            logger.info(f"进度: 成功{success_count} 失败{fail_count} 跳过{skipped_count}")
            logger.info(f"{'=' * 50}")

            # 尝试登录（首次或检测到会话过期时）
            if not logged_in:
                try:
                    self.next_login(user)
                    logged_in = True
                except Exception as e:
                    logger.error(f"[登录] 失败: {e}，休眠后重试...")
                    time.sleep(30)
                    continue

            # 会话健康检查
            if not self._ensure_session_fresh():
                logger.warning(f"[会话] {company} 前会话过期，重新登录...")
                logged_in = False
                time.sleep(10)
                continue

            # 采集数据
            try:
                self.detilinfo(company)
                self.append_processed_code(company)
                success_count += 1
                logger.success(f"[{company}] 采集完成 ✓")
            except Exception as e:
                logger.error(f"[{company}] 采集失败: {e}")
                fail_count += 1
                # 失败后标记会话可能失效
                logged_in = False

            # 公司之间休眠
            if idx < total:
                delay = random.uniform(*interval_range)
                logger.info(f"[休眠] {delay:.1f}s ...")
                time.sleep(delay)

        # 汇总
        logger.info("\n" + "=" * 60)
        logger.info(f"批量采集完成!")
        logger.info(f"  总计: {total}  成功: {success_count}  失败: {fail_count}  跳过: {skipped_count}")
        logger.info("=" * 60)

        self.close_mongo_connection()


if __name__ == '__main__':
    import os
    gov = Govspider()
    gov.main()
