# -*- coding: utf-8 -*-
"""从 Windows 版 game_data.py 导出网页版数据 -> web/js/data.js

用法（在任意目录执行均可）：
    D:\\Anaconda\\envs\\mike\\python.exe D:\\code\\0901ICBCTI\\web\\tools\\export_data.py

说明：只读 Windows 版数据，不做任何修改；网页版与桌面版共用同一份题库与人格档案。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.abspath(os.path.join(HERE, ".."))
WINDOWS_DIR = os.path.abspath(os.path.join(WEB_DIR, "..", "windows"))

sys.path.insert(0, WINDOWS_DIR)
import game_data as D  # noqa: E402

data = {
    "dimensions": D.DIMENSIONS,
    "questions": D.QUESTIONS,
    "bonus": D.BONUS_QUESTION,
    "personalities": D.PERSONALITIES,
    "hidden": D.HIDDEN_PERSONALITIES,
    "groupColors": D.GROUP_COLORS,
    "defaultGroupColor": D.DEFAULT_GROUP_COLOR,
    "poleEn": D.POLE_EN,
}

out_path = os.path.join(WEB_DIR, "js", "data.js")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with io.open(out_path, "w", encoding="utf-8") as f:
    f.write("// 本文件由 tools/export_data.py 自动生成，请勿手动编辑。\n")
    f.write("// 数据源：windows/game_data.py\n")
    f.write("window.ICBCTI_DATA = ")
    f.write(json.dumps(data, ensure_ascii=False, indent=2))
    f.write(";\n")

print("已生成:", out_path)
print("题目数:", len(data["questions"]), "| 人格数:", len(data["personalities"]),
      "| 隐藏人格:", len(data["hidden"]))
