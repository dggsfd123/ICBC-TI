# -*- coding: utf-8 -*-
"""把 Windows 版的 2048x2048 人格图压缩为网页版使用的 512x512 PNG。

用法：
    D:\\Anaconda\\envs\\mike\\python.exe D:\\code\\0901ICBCTI\\web\\tools\\resize_images.py

可选参数：python resize_images.py 640   （指定输出边长，默认 512）
"""
import os
import sys

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.abspath(os.path.join(HERE, ".."))
SRC_DIR = os.path.abspath(os.path.join(WEB_DIR, "..", "windows", "icbcti"))
DST_DIR = os.path.join(WEB_DIR, "images")

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 512


def main():
    if not os.path.isdir(SRC_DIR):
        print("未找到源图目录:", SRC_DIR)
        return 1
    os.makedirs(DST_DIR, exist_ok=True)

    pygame.init()
    pygame.display.set_mode((1, 1))

    names = sorted(n for n in os.listdir(SRC_DIR) if n.lower().endswith(".png"))
    total = 0
    for name in names:
        img = pygame.image.load(os.path.join(SRC_DIR, name)).convert_alpha()
        img = pygame.transform.smoothscale(img, (SIZE, SIZE))
        dst = os.path.join(DST_DIR, name)
        pygame.image.save(img, dst)
        size_kb = os.path.getsize(dst) / 1024.0
        total += size_kb
        print("%-28s %6.0f KB" % (name, size_kb))

    print("-" * 40)
    print("共 %d 张，输出 %dx%d，合计 %.1f MB" % (len(names), SIZE, SIZE, total / 1024.0))
    print("输出目录:", DST_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
