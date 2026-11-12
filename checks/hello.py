# Hello World: python -m mpremote connect COM6 resume run checks/hello.py
import M5, sys, os, gc

M5.begin()
d = M5.Display
d.clear(0x000000)
d.setTextColor(0xFFFFFF, 0x000000)
d.setTextSize(3)
d.drawCenterString("Hello World", 160, 90)
d.setTextSize(2)
d.setTextColor(0xFFA500, 0x000000)
d.drawCenterString("Clippy", 160, 140)
print("impl", sys.implementation)
print("disp", d.width(), d.height())
print("free", gc.mem_free())
print("fs", os.statvfs("/flash"))
print("ls", os.listdir("/"), os.listdir("/flash"))
