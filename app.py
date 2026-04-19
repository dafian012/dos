from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import string
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
from protobuf_decoder.protobuf_decoder import Parser
import codecs
import time
from datetime import datetime
import urllib3
import base64
import concurrent.futures
import threading
import os
import requests
import sys
import hmac
import hashlib
import time

VERIFY_API = "https://xanaf-legacy-authorised-checker.vercel.app/verify"
SECRET_KEY = "XANAF_SUPER_SECRET_KEY"
OWNER_NAME = "XANAF LEGACY"
BOT_ID = "TEAM X GST GENERATOR API"

def verify_owner():
    try:
        r = requests.get(VERIFY_API, params={"bot_id": BOT_ID}, timeout=10).json()

        if r.get("owner") != OWNER_NAME:
            sys.exit("❌ Owner mismatch. Bot stopped.")

        ts = r.get("timestamp")
        sig = r.get("signature")

        msg = f"{BOT_ID}:{ts}"
        local_sig = hmac.new(SECRET_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()

        if local_sig != sig:
            sys.exit("❌ Signature invalid. Bot stopped.")

        if abs(int(time.time()) - int(ts)) > 60:
            sys.exit("❌ Token expired. Bot stopped.")

    except Exception as e:
        sys.exit(f"❌ Verification failed: {e}")

verify_owner()
#THIS BOT MAKE BY XANAF LEGACY YOU CAN CHANGE ENETHING BOT CAN'T WORKED.
# Disable only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ---------------- KEYS ---------------- #
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)

REGION_LANG = {"ME": "ar","IND": "hi","ID": "id","VN": "vi","TH": "th","BD": "bn","PK": "ur","TW": "zh","EU": "en","RU": "ru","NA": "en","SAC": "es","BR": "pt"}
REGION_URLS = {
    "IND": "https://client.ind.freefiremobile.com/",
    "ID": "https://clientbp.ggblueshark.com/",
    "BR": "https://client.us.freefiremobile.com/",
    "ME": "https://clientbp.common.ggbluefox.com/",
    "VN": "https://clientbp.ggblueshark.com/",
    "TH": "https://clientbp.common.ggbluefox.com/",
    "RU": "https://clientbp.ggblueshark.com/",
    "BD": "https://clientbp.ggblueshark.com/",
    "PK": "https://clientbp.ggblueshark.com/",
    "SG": "https://clientbp.ggblueshark.com/",
    "NA": "https://client.us.freefiremobile.com/",
    "SAC": "https://client.us.freefiremobile.com/",
    "EU": "https://clientbp.ggblueshark.com/",
    "TW": "https://clientbp.ggblueshark.com/"
}

def get_region(language_code: str) -> str:
    return REGION_LANG.get(language_code)

def get_region_url(region_code: str) -> str:
    return REGION_URLS.get(region_code, None)

# Thread-local storage for requests
thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        # Add retry mechanism
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        thread_local.session.mount("http://", adapter)
        thread_local.session.mount("https://", adapter)
        
    return thread_local.session

# ---------------- PROTOBUF ENCODING ---------------- #
def EnC_Vr(N):
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

# ---------------- AES ENCRYPTION ---------------- #
def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    key_bytes = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
    iv = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
    K = AES.new(key_bytes, AES.MODE_CBC, iv)
    R = K.encrypt(pad(Z, AES.block_size))
    return bytes.fromhex(R.hex())

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key_bytes = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
    iv = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

# ---------------- NAME / PASSWORD ---------------- #
def generate_random_name(name_prefix):
    characters = string.ascii_letters + string.digits
    return name_prefix + ''.join(random.choice(characters) for _ in range(6)).upper()

def generate_custom_password():
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(9)).upper()
    return f"HRE-{random_part}-CODEX"

# ---------------- Account creation (register/token) ---------------- #
def create_single_account(args):
    name_prefix, region = args
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = create_acc(region, name_prefix)
            if result and result.get('uid') and result.get('password') and result.get('status') == "full_login":
                return result
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
    return None

def create_acc(region, name_prefix):
    """
    Complete account creation flow - exactly like gen.py
    """
    password = generate_custom_password()
    session = get_session()
    
    # Step 1: Guest Register
    data = f"password={password}&client_type=2&source=2&app_id=100067"
    message = data.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()

    url = "https://100067.connect.garena.com/oauth/guest/register"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
        "Authorization": "Signature " + signature,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }

    try:
        response = session.post(url, headers=headers, data=data, timeout=30)
        resp_json = response.json()
        uid = resp_json.get('uid')
        if not uid:
            return None
        return token(uid, password, region, name_prefix)
    except Exception as e:
        return None

def token(uid, password, region, name_prefix):
    # Step 2: Token Grant
    session = get_session()
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
    }

    body = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": key,
        "client_id": "100067"
    }

    try:
        response = session.post(url, headers=headers, data=body, timeout=30)
        resp_json = response.json()
        open_id = resp_json.get('open_id')
        access_token = resp_json.get("access_token")

        if not open_id or not access_token:
            return None

        result = encode_string(open_id)
        field = to_unicode_escaped(result['field_14'])
        field = codecs.decode(field, 'unicode_escape').encode('latin1')

        return Major_Regsiter(access_token, open_id, field, uid, password, region, name_prefix)
    except Exception as e:
        return None

# ---------------- Encode helpers ---------------- #
def encode_string(original):
    keystream = [
        0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,
        0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
        0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,
        0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30
    ]
    encoded = ""
    for i in range(len(original)):
        orig_byte = ord(original[i])
        key_byte = keystream[i % len(keystream)]
        result_byte = orig_byte ^ key_byte
        encoded += chr(result_byte)
    return {"open_id": original, "field_14": encoded}

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

# ---------------- Major register -> login flow ---------------- #
def Major_Regsiter(access_token, open_id, field, uid, password, region, name_prefix):
    # Step 3: Major Register
    session = get_session()
    url = "https://loginbp.ggblueshark.com/MajorRegister"
    internal_name = generate_random_name(name_prefix)

    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB52",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }

    payload = {
        1: internal_name,
        2: access_token,
        3: open_id,
        5: 102000007,
        6: 4,
        7: 1,
        13: 1,
        14: field,
        15: "en",
        16: 1,
        17: 1
    }

    try:
        payload_hex = CrEaTe_ProTo(payload).hex()
        payload_enc = E_AEs(payload_hex).hex()
        body = bytes.fromhex(payload_enc)
        response = session.post(url, headers=headers, data=body, verify=False, timeout=30)
        
        # Step 4: Proceed to Login - EXACTLY like gen.py
        return login(uid, password, access_token, open_id, response.content.hex(), response.status_code, internal_name, region)
    except Exception as e:
        return None

def chooseregion(data_bytes, jwt_token):
    url = "https://loginbp.ggblueshark.com/ChooseRegion"
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'Authorization': f"Bearer {jwt_token}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    try:
        session = get_session()
        response = session.post(url, data=data_bytes, headers=headers, verify=False, timeout=30)
        return response.status_code
    except Exception:
        return None

def login(uid, password, access_token, open_id, response_hex, status_code, name, region):
    # Step 4: Major Login - EXACTLY like gen.py
    lang = get_region(region)
    if not lang:
        lang = "en"
    lang_b = lang.encode("ascii")
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB52",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }

    # This payload is reused from original gen.py
    payload = b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02' + lang_b + b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
    data = payload
    try:
        data = data.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
    except Exception:
        pass

    d = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)

    if region.lower() == "me":
        URL = "https://loginbp.common.ggbluefox.com/MajorLogin"
    else:
        URL = "https://loginbp.ggblueshark.com/MajorLogin"
    
    try:
        session = get_session()
        RESPONSE = session.post(URL, headers=headers, data=Final_Payload, verify=False, timeout=30)
    except Exception:
        return None

    # If login successful, extract JWT token and proceed to GetLoginData
    if RESPONSE.status_code == 200:
        # If text length small, it's probably an error
        if len(RESPONSE.text) < 10:
            return None

        # Try to use protobuf parser path for non-ar/en languages
        if lang.lower() not in ["ar", "en"]:
            json_result = get_available_room(RESPONSE.content.hex())
            parsed_data = json.loads(json_result) if json_result else {}
            BASE64_TOKEN = parsed_data.get('8', {}).get('data')
            if BASE64_TOKEN:
                # region mapping for cis
                if region.lower() == "ru":
                    region = "RU"
                fields = {1: region}
                fields_h = bytes.fromhex(encrypt_api(CrEaTe_ProTo(fields).hex()))
                r = chooseregion(fields_h, BASE64_TOKEN)
                if r == 200:
                    return login_server(uid, password, access_token, open_id, RESPONSE.content.hex(), RESPONSE.status_code, name, region)
        
        # Try extract embedded JWT token substring for typical responses
        try:
            start_idx = RESPONSE.text.find("eyJhbGci")
            if start_idx != -1:
                BASE64_TOKEN = RESPONSE.text[start_idx:-1]
                # trim to expected length (original did a cut)
                second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
                time.sleep(0.2)
                BASE64_TOKEN = BASE64_TOKEN[:second_dot_index+44] if second_dot_index != -1 else BASE64_TOKEN
                dat = GET_PAYLOAD_BY_DATA(BASE64_TOKEN, access_token, 1, response_hex, status_code, name, uid, password, region)
                return dat
        except Exception:
            pass

    return None

def login_server(uid, password, access_token, open_id, response, status_code, name, region):
    lang = get_region(region)
    if not lang: lang = "en"
    lang_b = lang.encode("ascii")

    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB52",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }

    payload = b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02' + lang_b + b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
    data = payload
    try:
        data = data.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
    except Exception:
        pass

    d = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)
    if region.lower() == "me":
        URL = "https://loginbp.common.ggbluefox.com/MajorLogin"
    else:
        URL = "https://loginbp.ggblueshark.com/MajorLogin"

    try:
        session = get_session()
        RESPONSE = session.post(URL, headers=headers, data=Final_Payload, verify=False, timeout=30)
    except Exception:
        return None

    if RESPONSE.status_code == 200:
        if len(RESPONSE.text) < 10:
            return None

        json_result = get_available_room(RESPONSE.content.hex())
        parsed_data = json.loads(json_result) if json_result else {}
        BASE64_TOKEN = parsed_data.get('8', {}).get('data')
        if BASE64_TOKEN:
            second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
            time.sleep(0.2)
            if second_dot_index != -1:
                BASE64_TOKEN = BASE64_TOKEN[:second_dot_index+44]
            dat = GET_PAYLOAD_BY_DATA(BASE64_TOKEN, access_token, 1, response, status_code, name, uid, password, region)
            return dat

    return None

# ---------------- Protobuf parse helpers ---------------- #
def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def get_available_room(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        return None

# ---------------- GET LOGIN DATA ---------------- #
def GET_LOGIN_DATA(JWT_TOKEN, PAYLOAD, region):
    link = get_region_url(region)
    if not link:
        link = "https://clientbp.ggblueshark.com/"
    url = f"{link}GetLoginData"
    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {JWT_TOKEN}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB52',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; G011A Build/PI)',
        'Host': 'clientbp.common.ggblueshark.com',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        try:
            session = get_session()
            response = session.post(url, headers=headers, data=PAYLOAD, verify=False, timeout=20)
            response.raise_for_status()
            x = response.content.hex()
            json_result = get_available_room(x)
            parsed_data = json.loads(json_result) if json_result else None
            return parsed_data
        except requests.RequestException:
            attempt += 1
            time.sleep(2)
    return None

# ---------------- GET_PAYLOAD_BY_DATA (decode JWT payload & craft final payload) ---------------- #
def GET_PAYLOAD_BY_DATA(JWT_TOKEN, NEW_ACCESS_TOKEN, date, response, status_code, name, uid, password, region):
    try:
        token_payload_base64 = JWT_TOKEN.split('.')[1]
        token_payload_base64 += '=' * ((4 - len(token_payload_base64) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode('utf-8')
        decoded_payload = json.loads(decoded_payload)
        NEW_EXTERNAL_ID = decoded_payload.get('external_id', '')
        SIGNATURE_MD5 = decoded_payload.get('signature_md5', '')
        now = datetime.now()
        now = str(now)[:len(str(now))-7]

        PAYLOAD = b':\x071.111.2\xaa\x01\x02ar\xb2\x01 55ed759fcf94f85813e57b2ec8492f5c\xba\x01\x014\xea\x01@6fb7fdef8658fd03174ed551e82b71b21db8187fa0612c8eaf1b63aa687f1eae\x9a\x06\x014\xa2\x06\x014'
        PAYLOAD = PAYLOAD.replace(b"2023-12-24 04:21:34", str(now).encode())
        PAYLOAD = PAYLOAD.replace(b"15f5ba1de5234a2e73cc65b6f34ce4b299db1af616dd1dd8a6f31b147230e5b6", NEW_ACCESS_TOKEN.encode("UTF-8"))
        PAYLOAD = PAYLOAD.replace(b"4666ecda0003f1809655a7a8698573d0", NEW_EXTERNAL_ID.encode("UTF-8"))
        PAYLOAD = PAYLOAD.replace(b"7428b253defc164018c604a1ebbfebdf", SIGNATURE_MD5.encode("UTF-8"))
        PAYLOAD = PAYLOAD.hex()
        PAYLOAD = encrypt_api(PAYLOAD)
        PAYLOAD = bytes.fromhex(PAYLOAD)
        data = GET_LOGIN_DATA(JWT_TOKEN, PAYLOAD, region)
        
        # Return final account data with full login status - EXACTLY like gen.py
        return {
            "uid": uid,
            "password": password,
            "name": name,
            "region": region,
            "status": "full_login",
            "stage": "complete",
            
        }
    except Exception as e:
        return None

# ---------------- FLASK API ---------------- #
@app.route('/gen', methods=['GET'])
def generate_accounts():
    # Get parameters
    name = request.args.get('name', 'HUSTLER')
    count = request.args.get('count', '1')
    region = request.args.get('region', 'IND')
    
    # Validate and convert count
    try:
        count = int(count)
        if count > 15:
            count = 15
        if count < 1:
            count = 1
    except:
        count = 1
    
    # Validate region
    region = region.upper()
    if region not in REGION_LANG:
        region = "IND"
    
    print(f"Starting creation of {count} FULL LOGIN accounts for region {region} with name prefix {name}")
    
    # Use thread pool with limited workers
    max_workers = 5  # Reduced for stability
    
    # Create accounts with retry mechanism until we get exactly the requested count of FULL LOGIN accounts
    results = []
    attempts = 0
    max_total_attempts = count * 10
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        while len(results) < count and attempts < max_total_attempts:
            needed = count - len(results)
            current_batch = min(needed, max_workers)
            
            futures = []
            for i in range(current_batch):
                future = executor.submit(create_single_account, (name, region))
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                attempts += 1
                result = future.result()
                if result and result.get('status') == "full_login":
                    results.append(result)
                    print(f"Successfully created FULL LOGIN account {len(results)}/{count}: UID {result['uid']}")
                
                if len(results) >= count:
                    break
            
            if len(results) < count:
                time.sleep(2)  # Increased delay for stability
    
    # Return response
    response_data = {
        "success": True,
        "total_requested": count,
        "total_created": len(results),
        "accounts": results,
        "attempts_made": attempts
    }
    
    print(f"Completed: Created {len(results)} FULL LOGIN accounts out of {count} requested")
    return jsonify(response_data)

@app.route('/')
def home():
    return jsonify({
        "message": "FreeFire Account Generator API - FULL LOGIN ONLY",
        "endpoint": "/gen?name=NAME&count=COUNT&region=REGION",
        "max_count": 15,
        "available_regions": list(REGION_LANG.keys()),
        "note": "Complete account creation with ALL steps: register -> token -> major register -> major login -> getlogindata"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "API is running"})

# For Vercel - WSGI compatible
def application(environ, start_response):
    return app(environ, start_response)

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)



# ---------------- MODIFICATIONS: API FRIENDLY EXTRAS ---------------- #
try:
    from flask_cors import CORS
    CORS(app)
except Exception:
    pass

@app.route('/api/gen', methods=['POST'])
def generate_accounts_post():
    """
    JSON Body:
    {
        "name": "HUSTLER",
        "count": 1,
        "region": "IND"
    }
    """
    data = request.get_json(silent=True) or {}
    name = data.get('name', 'HUSTLER')
    count = data.get('count', 1)
    region = data.get('region', 'IND')

    # Validate and convert count
    try:
        count = int(count)
        if count > 15:
            count = 15
        if count < 1:
            count = 1
    except:
        count = 1

    # Validate region
    region = str(region).upper()
    if region not in REGION_LANG:
        region = "IND"

    print(f"[POST] Starting creation of {count} FULL LOGIN accounts for region {region} with name prefix {name}")

    max_workers = 5

    results = []
    attempts = 0
    max_total_attempts = count * 10

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        while len(results) < count and attempts < max_total_attempts:
            needed = count - len(results)
            current_batch = min(needed, max_workers)

            futures = []
            for i in range(current_batch):
                future = executor.submit(create_single_account, (name, region))
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                attempts += 1
                result = future.result()
                if result and result.get('status') == "full_login":
                    results.append(result)
                    print(f"[POST] Successfully created FULL LOGIN account {len(results)}/{count}: UID {result['uid']}")

                if len(results) >= count:
                    break

            if len(results) < count:
                time.sleep(2)

    response_data = {
        "success": True,
        "total_requested": count,
        "total_created": len(results),
        "accounts": results,
        "attempts_made": attempts,
        "method": "POST"
    }

    print(f"[POST] Completed: Created {len(results)} FULL LOGIN accounts out of {count} requested")
    return jsonify(response_data)

@app.route('/version')
def version():
    return jsonify({
        "name": "FreeFire Account Generator API",
        "version": "1.1",
        "endpoints": {
            "GET /gen": "Generate accounts via query params",
            "POST /api/gen": "Generate accounts via JSON body",
            "GET /health": "Health check",
            "GET /": "Info"
        }
    })
