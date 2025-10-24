from escpos.printer import Usb
from prompt_toolkit import prompt
VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E
p = Usb(VENDOR_ID, PRODUCT_ID)
text = prompt("\nstart typing ... \n>", multiline=True, vi_mode=True)
i = int(prompt("how much to print:) "))
for _ in range(i):
    p.text(text)
    p.cut()
