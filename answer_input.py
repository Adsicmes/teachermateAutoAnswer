"""
使用ocr对比文字，找到答案位置并标记，还没有做点击操作
仅支持单多选和判断题

使用阿里云
"""

import difflib
import json
import time

from alibabacloud_ocr_api20210707.models import RecognizeGeneralResponse
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_darabonba_stream.client import Client as StreamClient
import subprocess
from PIL import Image
from PIL import ImageDraw

import settings


def screenshot(local_file, remote_file="/sdcard/screenshot.png"):
    subprocess.run(["adb", "shell", "screencap", "-p", remote_file])
    subprocess.run(["adb", "pull", remote_file, local_file])


def ali_ocr(file_path, conf: open_api_models.Config) -> RecognizeGeneralResponse:
    client = ocr_api20210707Client(conf)

    body = StreamClient.read_from_file_path(file_path)
    recognize_general_request = ocr_api_20210707_models.RecognizeGeneralRequest(
        body=body
    )
    return client.recognize_general(recognize_general_request)


def mark_ocr_text(image_path, output_path, ocr_result: dict):
    if ocr_result["prism_wnum"] == 0:
        return
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    for item in ocr_result["prism_wordsInfo"]:
        pos = item["pos"]
        draw.polygon([
            (pos[0]["x"], pos[0]["y"]),
            (pos[1]["x"], pos[1]["y"]),
            (pos[2]["x"], pos[2]["y"]),
            (pos[3]["x"], pos[3]["y"])
        ], fill=None, outline="red", width=4)

    img.save(output_path)


def find_center_point(points):
    x_sum = 0
    y_sum = 0
    for point in points:
        x_sum += point["x"]
        y_sum += point["y"]
    return {"x": x_sum / 4, "y": y_sum / 4}


def mark_dest_text(image_path, output_path, text, ocr_result: dict):
    if ocr_result["prism_wnum"] == 0:
        return
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    found = False
    for item in ocr_result["prism_wordsInfo"]:
        word_diff = difflib.SequenceMatcher(None, item["word"], text).ratio()
        if word_diff > 0.6:
            pos = item["pos"]
            draw.polygon([
                (pos[0]["x"], pos[0]["y"]),
                (pos[1]["x"], pos[1]["y"]),
                (pos[2]["x"], pos[2]["y"]),
                (pos[3]["x"], pos[3]["y"])
            ], fill=None, outline="blue", width=4)
            center = find_center_point(pos)
            radius = 15
            draw.ellipse((center["x"] - radius, center["y"] - radius, center["x"] + radius, center["y"] + radius),
                         fill="yellow", outline="black")
            found = True
    if not found:
        print(f"text: {text.strip()} not found in ocr result")
        return False

    img.save(output_path)
    return True


if __name__ == "__main__":

    ali_conf = open_api_models.Config(
        access_key_id=settings.ali_access_key_id,
        access_key_secret=settings.ali_access_key_secret,
        # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
        endpoint=f'ocr-api.cn-hangzhou.aliyuncs.com'
    )
    local_file = "screenshot.png"
    # screenshot(local_file)
    #
    # result = ali_ocr("screenshot.png", ali_conf)
    # result_body = result.body.to_map()
    # data = json.loads(result_body['Data'])

    # mark_ocr_text("screenshot.png", "marked_ocr.png", data)

    step = 0
    swipe = True
    for text in open("answer-paper-662477.json.txt", "r", encoding="utf-8").readlines():
        while True:
            if swipe:
                print(f"swipe, index: {step}")
                swipe = False
                screenshot(local_file)
                time.sleep(0.5)
                result = ali_ocr("screenshot.png", ali_conf)
                result_body = result.body.to_map()
                data = json.loads(result_body['Data'])
                mark_ocr_text("screenshot.png", f"marked_ocr_{step}.png", data)

            if mark_dest_text("screenshot.png", f"marked_dest_{step}.png", text, data):
                step += 1
                break
            else:
                subprocess.run(["adb", "shell", "input", "swipe", "540", "1500", "540", "800"])
                time.sleep(0.5)
                swipe = True
                step += 1



