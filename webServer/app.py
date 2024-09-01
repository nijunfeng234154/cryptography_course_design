import base64

import flask.cli
from PIL import Image
from flask import Flask, request
from flask_cors import CORS, cross_origin
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
from random import randint, seed
from io import BytesIO
from decode_image import decode_main
from encode_image import encode_main


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

save_path = Path(app.root_path) / 'encoded_image'
test_pic = save_path / "static/pic.jpg"

def CV2_encode():
    text = request.form['text']
    pic_bytes = request.files['file'].read()
    buffer = np.fromstring(pic_bytes, np.uint8)
    pic = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    _, buffer = cv2.imencode('.jpg', gray)
    return base64.b64encode(buffer)

@app.route('/encode', methods=['POST'])
@cross_origin()
def encode():
    flag, text = check_text(request.form['text'])
    pic_bytes = request.files['file'].read()
    img = Image.open(BytesIO(pic_bytes))
    filename = get_filename(img.format)
    img.save(filename, "PNG")
    if flag == "1":
        print("加密模式")
        status, img_path = encode_main(filename, text)
        if status:
            return insert_text("ook") + base64_encode(img_path, "PNG")
        else:
            print("加密失败")
            return '500'
    else:
        resp = "yes" + str(randint(1, 100))
        print("解密模式", resp)
        status, msg = decode_main(filename)
        # status,msg = decode_main('F:\\code\\mystamp1\\ClassWorkMix\\密码编码学课程设计\\webServer\\encoded_image\\202312210931_hidden.png')
        if status:
            return insert_text(msg) + base64_encode(filename, "PNG")
        else:
            return '500'

def insert_text(text: str):
    _res = text[1:] + "####"
    return _res.encode("utf-8")


def check_text(txt: str):
    if txt == "":
        return "0", ""
    _txt = txt[:49]
    flag = _txt[0]
    return flag, _txt

def img2cv2(img: Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def base64_encode(img_path, format_: str):
    # Ensure the format is one that OpenCV supports
    if format_.lower() not in ['jpeg', 'png', 'bmp', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'tiff', 'tif']:
        format_ = 'jpeg'
    img = Image.open(img_path)
    img = img2cv2(img)
    return base64.b64encode(cv2.imencode(f".{format_}", img)[1])

def get_filename(suffix: str) -> str:
    # rice_path = lambda: f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{randint(1, 9999)}"
    rice_path = lambda: f"{datetime.now().strftime('%Y%m%d%H%M')}"
    rand_path = save_path / rice_path()
    while rand_path.exists():
        rand_path = save_path / rice_path()
    return str(rand_path.absolute()) + "." + suffix.lower()
    # return 'F:\\code\\mystamp1\\ClassWorkMix\\密码编码学课程设计\\webServer\\encoded_image\\20231221091056_4672_hidden.png'

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=False)
