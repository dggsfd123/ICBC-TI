# -*- coding: utf-8 -*-
"""ICBCTI 人格测试小游戏（pygame，竖屏 9:16）。

逻辑画布 1080x1920（手机海报比例），窗口按屏幕高度等比缩放，电脑/手机预览都合适。

运行：
    conda activate mike
    python D:\\code\\0901ICBCTI\\windows\\icbcti_game.py
    或双击 启动ICBCTI测试.bat

流程：开始页 -> 37 道情境题（前 36 题随机打乱顺序与选项，第 37 题固定最后）
      -> 报告页（人格图 + 解读 + 四维星级 + 隐藏人格，可另存为图片 / 再测一次）
全程鼠标操作。
"""

import os
import random
import sys
from datetime import datetime

import pygame

import game_data
from game_data import (BONUS_QUESTION, DEFAULT_GROUP_COLOR, DIMENSIONS, GROUP_COLORS,
                       PERSONALITIES, POLE_EN, QUESTIONS, find_hidden, star_level)
from game_ui import (ACCENT, ACCENT_SOFT, CARD, CARD_BORDER, OPTION_BG,
                     OPTION_BORDER, PRIMARY, PRIMARY_SOFT, TEXT, TEXT_LIGHT,
                     TEXT_SUB, Button, clip_circle, clip_rounded, draw_card,
                     draw_paragraph, draw_rounded_rect, draw_stars_row,
                     draw_text, fit_surface, get_font, make_gradient_background,
                     wrap_text)

# 逻辑分辨率（9:16 竖屏）
LOGICAL_W, LOGICAL_H = 1080, 1920
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISCLAIMER = "ICBC-TI仅供娱乐，无参考意义。"

FROZEN = getattr(sys, "frozen", False)   # 是否为 PyInstaller 打包后的 exe


def resource_dir():
    """只读资源目录：打包后为临时解压目录，开发时为脚本目录。"""
    return getattr(sys, "_MEIPASS", BASE_DIR)


def app_dir():
    """可写目录：打包后为 exe 所在目录，开发时为脚本目录。"""
    return os.path.dirname(sys.executable) if FROZEN else BASE_DIR


IMAGE_DIR = os.path.join(resource_dir(), "icbcti")
EXPORT_DIR = os.path.join(app_dir(), "报告导出")

# 选择后的反馈/翻页延迟（毫秒）
FEEDBACK_DELAY = 430
TOAST_DURATION = 3600

LETTERS = "ABCDEFGH"

# 报告页按钮栏（位于卡片下方）
REPORT_BTN_Y = 1780
REPORT_BTN_H = 80
EXPORT_CARD_BOTTOM = 1760


# ---------------------------------------------------------------- 题目对象

class Option:
    def __init__(self, text, pole=None, hidden_key=None):
        self.text = text
        self.pole = pole                # 所属极（进取/自保/...）
        self.hidden_key = hidden_key    # 第 37 题选项 A/B/C/D
        self.letter = ""
        self.rect = None


class Question:
    def __init__(self, text, options, dim=None, bonus=False):
        self.text = text
        self.options = options
        self.dim = dim
        self.bonus = bonus
        self.chosen = None

    @property
    def is_answered(self):
        return self.chosen is not None


def build_quiz():
    """生成一次测试的题目顺序：前 36 题整体乱序，每题选项也乱序；第 37 题固定最后。"""
    quiz = []
    pool = list(QUESTIONS)
    random.shuffle(pool)
    for raw in pool:
        opts = [Option(o["text"], pole=o["pole"]) for o in raw["options"]]
        random.shuffle(opts)
        quiz.append(Question(raw["text"], opts, dim=game_data.DIM_BY_KEY[raw["dim"]]))

    bonus_opts = [Option(o["text"], hidden_key=o["key"]) for o in BONUS_QUESTION["options"]]
    random.shuffle(bonus_opts)
    quiz.append(Question(BONUS_QUESTION["text"], bonus_opts, bonus=True))
    return quiz


class Quiz:
    def __init__(self):
        self.questions = build_quiz()
        self.index = 0
        self.locked = False
        self.selected_at = 0
        self.layout = []          # [(rect, option), ...]
        self.question_rect = None

    @property
    def current(self):
        return self.questions[self.index]

    @property
    def total(self):
        return len(self.questions)

    def choose(self, option):
        if self.locked or self.current.is_answered:
            return
        self.current.chosen = option
        self.locked = True
        self.selected_at = pygame.time.get_ticks()

    def advance(self):
        """翻到下一题；答完最后一题返回 False。"""
        self.locked = False
        if self.index >= self.total - 1:
            return False
        self.index += 1
        self.layout = []          # 触发重新排版
        return True


# ---------------------------------------------------------------- 计分

def compute_result(quiz):
    scores = {d["key"]: 0 for d in DIMENSIONS}
    for q in quiz.questions:
        if q.bonus or q.chosen is None:
            continue
        if q.chosen.pole == q.dim["score_pole"]:
            scores[q.dim["key"]] += 1

    code = ""
    poles = []
    stars = {}
    for d in DIMENSIONS:
        s = scores[d["key"]]
        if s >= 5:
            code += d["high_code"]
            poles.append(d["high_pole"])
        else:
            code += d["low_code"]
            poles.append(d["low_pole"])
        stars[d["key"]] = star_level(s)

    bonus = quiz.questions[-1].chosen
    bonus_key = bonus.hidden_key if bonus else None
    hidden = find_hidden(bonus_key, code, stars)

    return {
        "code": code,
        "profile": PERSONALITIES[code],
        "scores": scores,
        "stars": stars,
        "poles": poles,
        # 极名可能带字母后缀（如“进取(A)”），取中文部分查英文
        "poles_en": " · ".join(POLE_EN.get(p.split("(")[0].strip(), p) for p in poles),
        "hidden": hidden,
        "bonus_key": bonus_key,
        "bonus_text": bonus.text if bonus else "",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }


# ---------------------------------------------------------------- 绘制小工具

def draw_check(surface, x, y, size, color, width=4):
    """绘制对勾（不依赖字体字形）。"""
    pts = [(x, y + size * 0.52), (x + size * 0.34, y + size * 0.86), (x + size, y + size * 0.12)]
    pygame.draw.lines(surface, color, False, pts, width)


def draw_pill(surface, rect, text, font, bg, fg, radius=None):
    rect = pygame.Rect(rect)
    draw_rounded_rect(surface, rect, bg, rect.height // 2 if radius is None else radius)
    draw_text(surface, text, font, fg, rect.center, anchor="center")


def export_default_dir():
    """默认导出目录：优先程序目录，只读时依次回退到桌面 / 用户目录。"""
    candidates = [EXPORT_DIR,
                  os.path.join(os.path.join(os.path.expanduser("~"), "Desktop"), "报告导出"),
                  os.path.join(os.path.expanduser("~"), "报告导出")]
    for folder in candidates:
        try:
            os.makedirs(folder, exist_ok=True)
            return folder
        except Exception:
            continue
    return app_dir()


def shorten_to_width(text, font, max_width):
    """文本过长时从头部截断（保留文件名等尾部信息）。"""
    if font.size(text)[0] <= max_width:
        return text
    tail = text
    while len(tail) > 6 and font.size(tail + "…")[0] > max_width:
        tail = tail[1:]
    return tail + "…"


# ---------------------------------------------------------------- 另存为对话框

def ask_save_path(default_name):
    """弹出系统另存为对话框，返回用户选择的路径；取消或不可用时返回 None。"""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.asksaveasfilename(
            title="导出 ICBC-TI 报告",
            defaultextension=".png",
            initialdir=EXPORT_DIR if os.path.isdir(EXPORT_DIR) else app_dir(),
            initialfile=default_name,
            filetypes=[("PNG 图片", "*.png"), ("JPEG 图片", "*.jpg"), ("所有文件", "*.*")],
        )
        if isinstance(path, tuple):
            path = path[0] if path else ""
        return path or None
    except Exception:
        return None
    finally:
        if root is not None:
            try:
                root.update()
                root.destroy()
            except Exception:
                pass


# ---------------------------------------------------------------- 主程序

class Game:
    def __init__(self, canvas):
        self.canvas = canvas
        self.bg = make_gradient_background((LOGICAL_W, LOGICAL_H))
        self.state = "start"
        self.quiz = None
        self.result = None
        self.toast = None
        self.image_cache = {}

        # 开始页按钮
        self.start_btn = Button((280, 1340, 520, 110), "开始测试", "primary", 42, 30)
        # 报告页按钮（卡片下方）
        self.export_btn = Button((220, REPORT_BTN_Y, 300, REPORT_BTN_H), "导出报告", "primary", 30, 22)
        self.again_btn = Button((560, REPORT_BTN_Y, 300, REPORT_BTN_H), "再测一次", "ghost", 30, 22)
        self.hovering = False
        self._last_hover = None

    # ---------------- 状态切换

    def start_quiz(self):
        self.quiz = Quiz()
        self.state = "quiz"

    def finish_quiz(self):
        self.result = compute_result(self.quiz)
        self.state = "report"

    def restart(self):
        self.result = None
        self.quiz = None
        self.toast = None
        self.state = "start"

    def show_toast(self, text):
        self.toast = {"text": text, "until": pygame.time.get_ticks() + TOAST_DURATION}

    # ---------------- 资源

    def get_image(self, filename, size):
        key = (filename, size)
        if key not in self.image_cache:
            raw = pygame.image.load(os.path.join(IMAGE_DIR, filename)).convert_alpha()
            self.image_cache[key] = fit_surface(raw, size)
        return self.image_cache[key]

    # ---------------- 事件

    def on_click(self, pos):
        if self.state == "start":
            if self.start_btn.hit(pos):
                self.start_quiz()
        elif self.state == "quiz":
            self.on_click_quiz(pos)
        elif self.state == "report":
            if self.export_btn.hit(pos):
                self.export_report()
            elif self.again_btn.hit(pos):
                self.restart()

    def on_click_quiz(self, pos):
        if self.quiz.locked:
            return
        for rect, option in self.quiz.layout:
            if rect.collidepoint(pos):
                self.quiz.choose(option)
                return

    # ---------------- 每帧更新

    def update(self, mouse_pos):
        self.hovering = False
        now = pygame.time.get_ticks()

        if self.state == "start":
            self.start_btn.update(mouse_pos)
            self.hovering = self.start_btn.hover
        elif self.state == "quiz":
            self.update_quiz(mouse_pos, now)
        elif self.state == "report":
            self.export_btn.update(mouse_pos)
            self.again_btn.update(mouse_pos)
            self.hovering = self.export_btn.hover or self.again_btn.hover

        if self.toast and now > self.toast["until"]:
            self.toast = None

        if self.hovering != self._last_hover:
            self._last_hover = self.hovering
            try:
                cursor = (pygame.SYSTEM_CURSOR_HAND if self.hovering
                          else pygame.SYSTEM_CURSOR_ARROW)
                pygame.mouse.set_cursor(cursor)
            except pygame.error:
                pass

    def update_quiz(self, mouse_pos, now):
        q = self.quiz
        if q.locked:
            if now - q.selected_at >= FEEDBACK_DELAY:
                if not q.advance():
                    self.finish_quiz()
            return
        for rect, _option in q.layout:
            if rect.collidepoint(mouse_pos):
                self.hovering = True
                break

    # ---------------- 绘制入口

    def draw(self):
        self.canvas.blit(self.bg, (0, 0))
        if self.state == "start":
            self.draw_start()
            self.draw_footer(self.canvas)
        elif self.state == "quiz":
            self.draw_quiz()
            self.draw_footer(self.canvas)
        elif self.state == "report":
            self.draw_report(self.canvas, self.result, show_buttons=True)
        if self.toast:
            self.draw_toast()

    def draw_footer(self, surface, y=None):
        y = LOGICAL_H - 20 if y is None else y
        draw_text(surface, DISCLAIMER, get_font(21), TEXT_LIGHT,
                  (LOGICAL_W // 2, y), anchor="midbottom")

    # ---------------- 开始页

    def draw_start(self):
        # 顶部四个头像装饰
        names = ["1730下班守门员_觉醒.png", "PPT战略刺客_觉醒.png", "资源召唤师_觉醒.png", "兜底老黄牛_觉醒.png"]
        r, gap = 64, 34
        total = len(names) * r * 2 + gap * (len(names) - 1)
        x = (LOGICAL_W - total) // 2 + r
        for name in names:
            img = self.get_image(name, (r * 2, r * 2))
            clip_circle(self.canvas, img, (x, 210), r)
            pygame.draw.circle(self.canvas, (255, 255, 255), (x, 210), r, width=4)
            x += r * 2 + gap

        card = pygame.Rect(56, 300, 968, 1240)
        draw_card(self.canvas, card, radius=36)
        cx = card.centerx

        draw_text(self.canvas, "ICBC-TI", get_font(130, bold=True), PRIMARY,
                  (cx, 390), anchor="midtop")
        draw_text(self.canvas, "工行 16 型人格测试", get_font(46, bold=True), TEXT,
                  (cx, 620), anchor="midtop")
        draw_text(self.canvas, "37 道职场情境题，测出你的隐藏人格", get_font(30), TEXT_SUB,
                  (cx, 712), anchor="midtop")

        chips = ["%s / %s" % (d["high_pole"], d["low_pole"]) for d in DIMENSIONS]
        chip_w, chip_h, chip_gap = 400, 84, 28
        x0 = cx - (chip_w * 2 + chip_gap) // 2
        for i, text in enumerate(chips):
            col, row = i % 2, i // 2
            rect = pygame.Rect(x0 + col * (chip_w + chip_gap), 800 + row * (chip_h + chip_gap),
                               chip_w, chip_h)
            draw_pill(self.canvas, rect, text, get_font(30, bold=True), PRIMARY_SOFT, PRIMARY)

        pygame.draw.line(self.canvas, CARD_BORDER, (220, 1096), (860, 1096), 2)

        tips = [
            "点选即可作答",
            "约 3 分钟，37 道情境题",
            "测试结果仅供参考，不构成任何建议",
        ]
        y = 1146
        for tip in tips:
            draw_text(self.canvas, tip, get_font(25), TEXT_SUB, (cx, y), anchor="midtop")
            y += 58

        self.start_btn.draw(self.canvas)

    # ---------------- 答题页

    def layout_quiz(self):
        """计算当前题目的题干卡片与选项矩形。"""
        q = self.quiz.current
        card_x, card_w = 56, 968
        q_font = get_font(40, bold=True)
        text_w = card_w - 104
        line_h = q_font.get_height() + 14

        lines = len(wrap_text(q.text, q_font, text_w))
        card_h = 118 + lines * line_h + 44

        n = len(q.options)
        if n <= 2:
            opt_h, opt_gap = 170, 30
        else:
            opt_h, opt_gap = 150, 30
        opts_h = n * opt_h + (n - 1) * opt_gap

        total_h = card_h + 44 + opts_h
        top = 150 + max(0, (1700 - total_h) // 2)

        q_rect = pygame.Rect(card_x, top, card_w, card_h)
        layout = []
        y = q_rect.bottom + 44
        for i, opt in enumerate(q.options):
            opt.rect = pygame.Rect(card_x, y, card_w, opt_h)
            opt.letter = LETTERS[i]
            layout.append((opt.rect, opt))
            y += opt_h + opt_gap
        self.quiz.layout = layout
        self.quiz.question_rect = q_rect

    def draw_quiz(self):
        q = self.quiz
        if not q.layout:
            self.layout_quiz()
        cur = q.current

        # 顶部进度
        done = q.index + (1 if cur.is_answered else 0)
        draw_text(self.canvas, "第 %d / %d 题" % (q.index + 1, q.total),
                  get_font(28, bold=True), TEXT, (56, 62), anchor="midleft")
        draw_text(self.canvas, "已完成 %d / %d" % (done, q.total),
                  get_font(23), TEXT_SUB, (1024, 62), anchor="midright")
        track = pygame.Rect(56, 100, 968, 14)
        draw_rounded_rect(self.canvas, track, (230, 233, 241), 7)
        ratio = done / float(q.total)
        if ratio > 0:
            draw_rounded_rect(self.canvas, pygame.Rect(56, 100, max(14, int(968 * ratio)), 14),
                              PRIMARY, 7)

        # 题干卡片
        draw_card(self.canvas, q.question_rect, radius=32)
        pill = pygame.Rect(q.question_rect.x + 32, q.question_rect.y + 30, 168, 44)
        draw_pill(self.canvas, pill, "第 %d / %d 题" % (q.index + 1, q.total),
                  get_font(23, bold=True), PRIMARY_SOFT, PRIMARY)
        if cur.bonus:
            tag = pygame.Rect(pill.right + 16, pill.y, 168, 44)
            draw_pill(self.canvas, tag, "隐藏人格彩蛋", get_font(21, bold=True),
                      ACCENT_SOFT, (176, 118, 12))
        q_font = get_font(40, bold=True)
        draw_paragraph(self.canvas, cur.text, q_font, TEXT,
                       pygame.Rect(q.question_rect.x + 52, q.question_rect.y + 118,
                                   q.question_rect.width - 104, 0), line_gap=14)

        # 选项（竖屏单列）
        mouse = pygame.mouse.get_pos()
        selected = cur.chosen
        opt_font = get_font(34) if len(cur.options) <= 2 else get_font(31)
        for rect, option in q.layout:
            if selected is not None:
                state = "selected" if option is selected else "dim"
            elif rect.collidepoint(mouse):
                state = "hover"
            else:
                state = "idle"
            self.draw_option(rect, option, state, opt_font)

        if selected is not None:
            self.draw_feedback_badge(selected)
        else:
            draw_text(self.canvas, "点击选项即刻作答，选择后自动进入下一题",
                      get_font(21), TEXT_LIGHT, (LOGICAL_W // 2, 1836), anchor="center")

    def draw_option(self, rect, option, state, font):
        if state == "selected":
            bg, border, fg = PRIMARY, PRIMARY, (255, 255, 255)
            badge_bg, badge_fg = (255, 255, 255), PRIMARY
        elif state == "dim":
            bg, border, fg = (250, 250, 252), (234, 236, 242), (196, 199, 208)
            badge_bg, badge_fg = (236, 238, 244), (206, 209, 218)
        elif state == "hover":
            bg, border, fg = CARD, PRIMARY, TEXT
            badge_bg, badge_fg = PRIMARY_SOFT, PRIMARY
        else:
            bg, border, fg = OPTION_BG, OPTION_BORDER, TEXT
            badge_bg, badge_fg = (238, 240, 246), TEXT_SUB

        draw_card(self.canvas, rect, radius=28, bg=bg, border=border,
                  shadow=(state in ("hover", "selected")), border_width=3)

        cx = rect.x + 56
        cy = rect.centery
        pygame.draw.circle(self.canvas, badge_bg, (cx, cy), 32)
        draw_text(self.canvas, option.letter, get_font(30, bold=True), badge_fg,
                  (cx, cy), anchor="center")

        lines = wrap_text(option.text, font, rect.width - 168)
        line_h = font.get_height() + 10
        start_y = rect.centery - (len(lines) * line_h - 10) / 2
        for i, line in enumerate(lines):
            draw_text(self.canvas, line, font, fg, (rect.x + 112, start_y + i * line_h))

    def draw_feedback_badge(self, option):
        rect = option.rect
        font = get_font(21, bold=True)
        text = "已记录"
        w = font.size(text)[0] + 62
        box = pygame.Rect(rect.right - w - 24, rect.bottom - 52, w, 38)
        draw_rounded_rect(self.canvas, box, (255, 255, 255), 19)
        draw_check(self.canvas, box.x + 17, box.y + 9, 20, PRIMARY)
        draw_text(self.canvas, text, font, PRIMARY, (box.x + 44, box.centery), anchor="midleft")

    # ---------------- 报告页

    def draw_report(self, surface, result, show_buttons=True):
        card = pygame.Rect(44, 34, 992, EXPORT_CARD_BOTTOM - 34)
        draw_card(surface, card, radius=36)

        profile = result["profile"]
        hidden = result["hidden"]
        inner_x, inner_w = 78, 924
        cx = LOGICAL_W // 2

        # 报告头
        draw_text(surface, "ICBC-TI 人格测试报告", get_font(26, bold=True), TEXT,
                  (inner_x, 76), anchor="midleft")
        draw_text(surface, result["date"], get_font(21), TEXT_LIGHT,
                  (inner_x + inner_w, 76), anchor="midright")
        pygame.draw.line(surface, CARD_BORDER, (inner_x, 128), (inner_x + inner_w, 128), 2)

        # 人格图（觉醒人格使用觉醒图）
        img_name = hidden["image"] if hidden else profile["image"]
        img = self.get_image(img_name, (360, 360))
        img_rect = pygame.Rect((LOGICAL_W - 360) // 2, 142, 360, 360)
        clip_rounded(surface, img, img_rect, radius=28)
        draw_rounded_rect(surface, img_rect, CARD_BORDER, 28, width=3)

        # 类型代码（分组配色） + 英文名 + 中文名 + 分组
        group_color = GROUP_COLORS.get(profile["group"], DEFAULT_GROUP_COLOR)
        draw_text(surface, result["code"], get_font(68, bold=True), group_color["main"],
                  (cx, 534), anchor="midtop")
        draw_text(surface, result["poles_en"], get_font(23), TEXT_SUB,
                  (cx, 636), anchor="midtop")
        name = hidden["name"] if hidden else profile["name"]
        draw_text(surface, "【%s】" % name, get_font(40, bold=True),
                  (168, 118, 12) if hidden else TEXT, (cx, 676), anchor="midtop")

        group_font = get_font(24, bold=True)
        group_w = group_font.size(profile["group"])[0] + 60
        draw_pill(surface, pygame.Rect(cx - group_w // 2, 738, group_w, 44),
                  profile["group"], group_font, group_color["soft"], group_color["main"])

        draw_text(surface, " · ".join(result["poles"]), get_font(26), TEXT_SUB,
                  (cx, 798), anchor="midtop")

        # 隐藏人格 / 未解锁
        y = self.draw_hidden_block(surface, result, pygame.Rect(inner_x, 842, inner_w, 0))

        # 四维星级（一行四格）
        y += 40
        cell_w = (inner_w - 20 * 3) // 4
        for i, d in enumerate(DIMENSIONS):
            x = inner_x + i * (cell_w + 20)
            draw_text(surface, d["name"], get_font(22, bold=True), TEXT,
                      (x + cell_w // 2, y), anchor="midtop")
            draw_stars_row(surface, x + (cell_w - 170) // 2, y + 36,
                           result["stars"][d["key"]], size=13, gap=10)
            draw_text(surface, "%d / 9" % result["scores"][d["key"]], get_font(19), TEXT_LIGHT,
                      (x + cell_w // 2, y + 68), anchor="midtop")
        y += 104

        # 人格解读
        y += 48
        draw_text(surface, "人格解读", get_font(27, bold=True), TEXT,
                  (inner_x, y), anchor="topleft")
        draw_rounded_rect(surface, pygame.Rect(inner_x, y + 42, 56, 5), PRIMARY, 3)
        y += 92

        items = [
            ("关键词", profile["keyword"]),
            ("核心技能", profile["skill"]),
            ("大招", profile["ultimate"]),
            ("名场面", profile["scene"]),
            ("经典台词", profile["line"]),
        ]
        self.draw_profile_items(surface, items, pygame.Rect(inner_x, y, inner_w, 0),
                                bottom_limit=card.bottom - 34)

        # 底部按钮 + 免责声明
        if show_buttons:
            self.export_btn.draw(surface)
            self.again_btn.draw(surface)
        self.draw_footer(surface, surface.get_height() - 20)

    def draw_profile_items(self, surface, items, rect, bottom_limit):
        """自适应字号/间距，保证 5 条解读完整落在 bottom_limit 之内。"""
        rect = pygame.Rect(rect)
        label_font = get_font(19, bold=True)
        label_h = label_font.get_height() + 4
        available = bottom_limit - rect.y

        value_font, line_h, gap = get_font(24), 0, 10
        for size in (32, 30, 28, 26, 24, 22):
            font = get_font(size)
            lh = font.get_height() + 8
            total = sum(label_h + len(wrap_text(v, font, rect.width)) * lh for _k, v in items)
            if total + 10 * len(items) <= available:
                value_font, line_h = font, lh
                break
        if line_h == 0:
            value_font, line_h = get_font(22), get_font(22).get_height() + 8

        total = sum(label_h + len(wrap_text(v, value_font, rect.width)) * line_h
                    for _k, v in items)
        gap = max(10, min(28, (available - total) // len(items)))

        y = rect.y
        for label, value in items:
            draw_text(surface, label, label_font, TEXT_LIGHT, (rect.x, y), anchor="topleft")
            y += label_h
            y = draw_paragraph(surface, value, value_font, TEXT,
                               pygame.Rect(rect.x, y, rect.width, 0), line_gap=8) + gap

    def draw_hidden_block(self, surface, result, rect):
        rect = pygame.Rect(rect)
        hidden = result["hidden"]
        inner_w = rect.width - 44
        if hidden:
            blocks = [
                (get_font(25, bold=True), (168, 118, 12), "隐藏人格 · %s" % hidden["name"]),
                (get_font(25, bold=True), TEXT, hidden["desc"]),
                (get_font(19), TEXT_SUB,
                 "解锁条件：第37题选 %s ＋ %s 型指定星级组合" % (result["bonus_key"], hidden["code"])),
            ]
            bg, border = ACCENT_SOFT, ACCENT
        else:
            blocks = [
                (get_font(25, bold=True), TEXT_SUB, "隐藏人格未解锁"),
            ]
            bg, border = (248, 249, 252), OPTION_BORDER

        padding, gap = 22, 12
        heights = [len(wrap_text(t, f, inner_w)) * (f.get_height() + 4) for f, _c, t in blocks]
        box = pygame.Rect(rect.x, rect.y, rect.width,
                          padding * 2 + sum(heights) + gap * (len(blocks) - 1))
        draw_card(surface, box, radius=22, bg=bg, border=border, shadow=False, border_width=3)
        y = box.y + padding
        for (font, color, text), height in zip(blocks, heights):
            draw_paragraph(surface, text, font, color,
                           pygame.Rect(box.x + 22, y, inner_w, 0), line_gap=4)
            y += height + gap
        return box.bottom

    # ---------------- 导出

    def export_report(self):
        result = self.result
        shown_name = result["hidden"]["name"] if result["hidden"] else result["profile"]["name"]
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = "ICBC-TI_%s_%s_%s.png" % (result["code"], shown_name, stamp)

        path = ask_save_path(default_name)
        pygame.event.pump()

        if not path:
            # 没有可用对话框时，回退到默认目录自动保存（exe 所在目录只读时用桌面）
            path = os.path.join(export_default_dir(), default_name)

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".bmp"):
            path += ".png"

        height = EXPORT_CARD_BOTTOM + 90
        surface = pygame.Surface((LOGICAL_W, height))
        surface.blit(self.bg.subsurface(pygame.Rect(0, 0, LOGICAL_W, height)), (0, 0))
        self.draw_report(surface, result, show_buttons=False)
        pygame.image.save(surface, path)
        self.show_toast("已保存到 %s" % shorten_to_width(path, get_font(22), LOGICAL_W - 160))

    def draw_toast(self):
        font = get_font(24)
        w = min(LOGICAL_W - 80, font.size(self.toast["text"])[0] + 72)
        rect = pygame.Rect((LOGICAL_W - w) // 2, LOGICAL_H - 320, w, 96)
        mask = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
        pygame.draw.rect(mask, (20, 24, 40, 44), (12, 18, rect.width, rect.height), border_radius=26)
        self.canvas.blit(mask, (rect.x - 12, rect.y - 12))
        draw_rounded_rect(self.canvas, rect, (32, 36, 48), 26)
        text = shorten_to_width(self.toast["text"], font, rect.width - 56)
        draw_text(self.canvas, text, font, (255, 255, 255), rect.center, anchor="center")


# ---------------------------------------------------------------- 窗口与入口

def pick_window_size():
    """按屏幕高度等比缩放逻辑画布，保证窗口完整可见。"""
    info = pygame.display.Info()
    max_h = max(480, info.current_h - 120)
    max_w = max(320, info.current_w - 80)
    scale = min(1.0, max_h / float(LOGICAL_H), max_w / float(LOGICAL_W))
    return max(300, int(LOGICAL_W * scale)), max(520, int(LOGICAL_H * scale))


def main():
    pygame.init()
    pygame.display.set_caption("ICBC-TI 人格测试 · 工行16型人格")
    win_size = pick_window_size()
    screen = pygame.display.set_mode(win_size)
    try:
        icon = fit_surface(
            pygame.image.load(os.path.join(IMAGE_DIR, "未来行长.png")).convert_alpha(), (32, 32))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    canvas = pygame.Surface((LOGICAL_W, LOGICAL_H))
    game = Game(canvas)
    clock = pygame.time.Clock()
    scale_x = LOGICAL_W / float(win_size[0])
    scale_y = LOGICAL_H / float(win_size[1])
    scaled = win_size != (LOGICAL_W, LOGICAL_H)
    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        logical_mouse = (mouse[0] * scale_x, mouse[1] * scale_y)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.on_click((event.pos[0] * scale_x, event.pos[1] * scale_y))

        game.update(logical_mouse)
        game.draw()
        if scaled:
            pygame.transform.smoothscale(canvas, win_size, screen)
        else:
            screen.blit(canvas, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
