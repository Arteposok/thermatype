import click
from sqlalchemy import create_engine
from escpos.printer import Usb
import feedparser
import lorem
import gpiozero
import signal
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy import String, Integer, Column, DateTime, select, asc
from sqlalchemy.orm import sessionmaker
import datetime as dt




engine = create_engine("sqlite:///data.db")


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


def add_task(title, details, due):
    task = Task(title=title, details=details, due=due)
    s.add(task)
    s.commit()


def remove_task(title):
    task = s.query(Task).filter_by(title=title).first()
    s.delete(task)
    s.commit()


def get_tasks():
    return select(Task).order_by(asc(Task.due)).all()


@click.group()
def main():
    pass


@main.command()
@click.argument("title")
@click.argument("detail")
@click.argument("due")
def add(title, detail, due):
    pass


@main.command()
@click.argument("id")
def remove(id):
    pass


@main.command()
def get():
    tasks = list(get_tasks())
    for task in tasks:
        print(f"{task.id} - {task.title}")


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


VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E
p = Usb(VENDOR_ID, PRODUCT_ID)
rss_bth = gpiozero.Button("GPIO5", pull_up=True, bounce_time=0.04)
rss(p)
rss_bth.when_held = lambda: rss(p)
signal.pause()
