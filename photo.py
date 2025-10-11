import cv2 as cv
import numpy as np
import requests
from io import BytesIO
from escpos.printer import Usb
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from PIL import Image

app = FastAPI()

class TextBody(BaseModel):
    text: str

class URLBody(BaseModel):
    url: str

VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E
p = Usb(VENDOR_ID, PRODUCT_ID)

@app.post("/print_image")
async def print(img: UploadFile = File(...)):
    images = BytesIO(await img.read())
    images.seek(0)
    image = Image.open(images)
    f = 550
    image = image.resize((f, (int(image.height * f / image.width))))
    imgcv = np.array(image)
    imgcv = cv.GaussianBlur(imgcv, (3, 3), 0)
    imgcv = cv.cvtColor(imgcv, cv.COLOR_BGR2GRAY)
    image = Image.fromarray(imgcv)
    p.image(image)
    p.text("\n" * 3)
    p.cut()

@app.post("/print_img_url")
async def print(body: URLBody):
    response = requests.get(body.url)
    response.raise_for_status()

    images = BytesIO(response.content)
    images.seek(0)
    image = Image.open(images)
    f = 550
    image = image.resize((f, (int(image.height * f / image.width))))
    imgcv = np.array(image)
    imgcv = cv.GaussianBlur(imgcv, (3, 3), 0)
    imgcv = cv.cvtColor(imgcv, cv.COLOR_BGR2GRAY)
    image = Image.fromarray(imgcv)
    p.image(image)
    p.text("\n" * 3)
    p.cut()

@app.post("/print_text")
async def print(body: TextBody):
    p.text(body.text)
    p.cut()

