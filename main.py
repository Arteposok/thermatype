import dateutil
from loguru import logger
import cv2 as cv
import numpy as np
import requests
from io import BytesIO
from escpos.printer import Usb
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from PIL import Image

from sqlalchemy import create_engine
import feedparser
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy import String, Integer, Column, DateTime, select, asc
from sqlalchemy.orm import sessionmaker
import datetime as dt


engine = create_engine("sqlite:///data.db")
logger.success("database engine created")


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    details = Column(String, nullable=False)
    due = Column(DateTime, default=dt.datetime.now() + dt.timedelta(days=7))


Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
s = SessionLocal()
app = FastAPI()
logger.success("created application")


class NewTask(BaseModel):
    title: str
    details: str
    due: str


@app.post("/add_task")
def add_task(f: NewTask):
    logger.debug(f)
    due = dateutil.parser.isoparse(f.due)
    task = Task(title=f.title, details=f.details, due=due)
    s.add(task)
    s.commit()
    logger.success("success")


class RemoveTask(BaseModel):
    title: str


@app.post("/remove_task")
def remove_task(f: RemoveTask):
    task = s.query(Task).filter_by(title=f.title).first()
    s.delete(task)
    s.commit()

    logger.success("success")


@app.get("/get_tasks")
def get_tasks():
    return get_all_tasks()

    logger.success("success")


def get_all_tasks():
    return list(select(Task).order_by(asc(Task.due)))


@app.get("/print_tasks")
def print_tasks():
    tasks = list(get_all_tasks())
    for task in tasks:
        print(f"{task.id} - {task.title}")

    logger.success("success")


def rss(p):
    feeds = [
        "https://realpython.com/podcasts/rpp/feed",
        "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "https://feeds.bbci.co.uk/news/england/rss.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://news.ycombinator.com/rss",
        "https://www.reddit.com/r/programming/.rss",
        "https://blog.python.org/feeds/posts/default?alt=rss",
        "https://www.linux.com/feed/",
        "https://www.sciencedaily.com/rss/top.xml",
        "https://feeds.feedburner.com/brainyquote/QUOTEBR",
        "https://www.raspberrypi.com/feed/",
    ]
    print("Printing Started rss initiated")
    for i, url in enumerate(feeds):
        d = feedparser.parse(url)
        try:
            print(d.entries[0].get("title", ""))
        except:
            continue
        p.text(
            f"""===={i+1}====
\t{d.entries[0].get("title", "no title")}
published {d.entries[0].get("published", "no date")}
by {d.feed.get("title", "no name")}

{d.entries[0].get("description", "no description")[:250]}...

{d.entries[0].get("link", "no link")}
=============\n"""
        )
        p.qr(d.entries[0].get("link", "no link"))
        p.cut()

    logger.success("success")


class TextBody(BaseModel):
    text: str


class URLBody(BaseModel):
    url: str


# 0x0FE6 pid 0x811E
VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E
p = Usb(VENDOR_ID, PRODUCT_ID)


@app.get("/")
def index():
    with open("index.html") as html:
        html_text = html.read()
    return HTMLResponse(content=html_text, status_code=200)

    logger.success("success")


def process(image, f):
    imgcv = np.array(image)

    if len(imgcv.shape) == 2:
        imgcv = cv.cvtColor(imgcv, cv.COLOR_GRAY2BGR)

    imgcv = cv.cvtColor(imgcv, cv.COLOR_BGR2GRAY)
    # imgcv = cv.GaussianBlur(imgcv, (3, 3), 0)
    imgcv = cv.resize(imgcv, (f, (int(image.height * f / image.width))))

    image = Image.fromarray(imgcv)
    logger.success("success")
    return image


@app.post("/print_image")
async def print_image(img: UploadFile = File(...)):
    images = BytesIO(await img.read())
    images.seek(0)
    image = Image.open(images)
    f = 550
    image = process(image, f)
    p.image(image)
    p.text("\n" * 3)
    p.cut()
    logger.success("success")


@app.post("/print_img_url")
async def print_url(body: URLBody):
    response = requests.get(body.url)
    response.raise_for_status()

    images = BytesIO(response.content)
    images.seek(0)
    image = Image.open(images)
    f = 550
    image = process(image, f)
    p.image(image)
    p.text("\n" * 3)
    p.cut()
    logger.success("success")


@app.post("/print_text")
async def print_text(body: TextBody):
    logger.debug(str(body))
    p.text(body.text)
    p.cut()
    logger.success("success")
