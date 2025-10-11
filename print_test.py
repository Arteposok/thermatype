from prompt_toolkit import prompt
from escpos.printer import Usb
import feedparser
import lorem

VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E

p = Usb(VENDOR_ID, PRODUCT_ID)
paragraphs = [lorem.get_paragraph() for i in range(2)]
print("Welcome to the typewriter machine controller app!")
print("Start typing now!")

#text = prompt(">", multiline=True)
#p.text(text)
p.cut()

