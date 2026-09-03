# -*- coding: utf-8 -*-
"""通用绘制与交互组件：中文字体、文本换行、圆角卡片、按钮、星级。"""

import math
import os
import pygame

# ---------------------------------------------------------------- 主题配色

BG_TOP = (253, 248, 244)
BG_BOT = (238, 241, 247)
CARD = (255, 255, 255)
CARD_BORDER = (231, 233, 240)
TEXT = (28, 30, 41)
TEXT_SUB = (110, 116, 134)
TEXT_LIGHT = (150, 156, 172)
PRIMARY = (196, 18, 45)
PRIMARY_DARK = (163, 12, 36)
PRIMARY_SOFT = (255, 240, 242)
ACCENT = (232, 168, 40)
ACCENT_SOFT = (255, 247, 230)
OPTION_BG = (248, 249, 252)
OPTION_BORDER = (222, 226, 235)
OPTION_HOVER_BORDER = (196, 18, 45)
SHADOW = (26, 32, 56)

# ---------------------------------------------------------------- 字体

_FONT_FILES = [
    (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"),
    (r"C:\Windows\Fonts\msyhl.ttc", r"C:\Windows\Fonts\msyh.ttc"),
    (r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"),
]
_font_cache = {}


def _font_path(bold):
    for regular, bold_file in _FONT_FILES:
        path = bold_file if bold else regular
        if path and os.path.exists(path):
            return path
    return None


def get_font(size, bold=False):
    """获取指定字号的中文字体（优先微软雅黑，带缓存）。"""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]

    font = None
    path = _font_path(bold)
    if path:
        try:
            font = pygame.font.Font(path, size)
        except Exception:
            font = None
    if font is None:
        font = pygame.font.SysFont(["microsoftyahei", "simhei", "dengxian", "arial"], size)
        try:
            font.set_bold(bold)
        except Exception:
            pass
    _font_cache[key] = font
    return font


# ---------------------------------------------------------------- 文本工具

_NO_LINE_START = "。，、；：？！”』」）】》…—·.,;:!?)]}%"

def wrap_text(text, font, max_width):
    """按字符换行（兼容中文），支持手动 \\n，并避免标点落在行首。"""
    lines = []
    for paragraph in str(text).split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            if not current or font.size(current + ch)[0] <= max_width:
                current += ch
            elif ch in _NO_LINE_START and len(current) >= 2:
                lines.append(current[:-1])       # 回退一个字，让标点不落行首
                current = current[-1] + ch
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_text(surface, text, font, color, pos, anchor="topleft"):
    """绘制单行文本，anchor 同 pygame Rect 的属性名。"""
    img = font.render(str(text), True, color)
    rect = img.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    surface.blit(img, rect)
    return rect


def draw_paragraph(surface, text, font, color, rect, line_gap=8, align="left"):
    """在 rect 内绘制自动换行的段落，返回绘制结束后的 y 坐标。"""
    rect = pygame.Rect(rect)
    lines = wrap_text(text, font, rect.width)
    line_h = font.get_height() + line_gap
    y = rect.y
    for line in lines:
        img = font.render(line, True, color)
        if align == "center":
            x = rect.x + (rect.width - img.get_width()) // 2
        elif align == "right":
            x = rect.x + rect.width - img.get_width()
        else:
            x = rect.x
        surface.blit(img, (x, y))
        y += line_h
    return y


def measure_paragraph(text, font, width, line_gap=8):
    lines = wrap_text(text, font, width)
    return len(lines) * (font.get_height() + line_gap)


# ---------------------------------------------------------------- 图形工具

def draw_rounded_rect(surface, rect, color, radius, width=0):
    rect = pygame.Rect(rect)
    if rect.width <= 0 or rect.height <= 0:
        return
    radius = max(0, min(radius, rect.width // 2, rect.height // 2))
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def draw_card(surface, rect, radius=22, bg=CARD, border=CARD_BORDER, shadow=True, border_width=1):
    """带柔和阴影的圆角卡片。"""
    rect = pygame.Rect(rect)
    if shadow:
        pad = 10
        shadow_surf = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf, (SHADOW[0], SHADOW[1], SHADOW[2], 28),
            (pad, pad + 4, rect.width, rect.height), border_radius=radius,
        )
        surface.blit(shadow_surf, (rect.x - pad, rect.y - pad))
    draw_rounded_rect(surface, rect, bg, radius)
    if border:
        draw_rounded_rect(surface, rect, border, radius, width=border_width)


def draw_star(surface, cx, cy, radius, color, hollow_color=None):
    """绘制五角星；hollow_color 为空心星描边色。"""
    pts = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    if hollow_color:
        pygame.draw.polygon(surface, hollow_color, pts, width=2)
    else:
        pygame.draw.polygon(surface, color, pts)


def draw_stars_row(surface, x, y, level, size=11, gap=9,
                   filled=ACCENT, empty=(224, 227, 234)):
    """绘制 5 颗星的评分行，返回整行宽度。"""
    for i in range(5):
        cx = x + i * (size * 2 + gap) + size
        cy = y + size
        if i < level:
            draw_star(surface, cx, cy, size, filled)
        else:
            draw_star(surface, cx, cy, size, empty)
    return 5 * (size * 2 + gap)


def make_gradient_background(size, top=BG_TOP, bottom=BG_BOT, circles=True):
    """生成一次性的渐变背景（含装饰圆），避免每帧重绘。"""
    w, h = size
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, color, (0, y), (w, y))
    if circles:
        deco = pygame.Surface((w, h), pygame.SRCALPHA)
        for cx, cy, r, color in (
            (80, 90, 190, (196, 18, 45, 12)),
            (w - 60, h - 40, 240, (60, 90, 180, 12)),
            (w - 120, 120, 130, (232, 168, 40, 16)),
            (120, h - 120, 150, (196, 18, 45, 10)),
        ):
            pygame.draw.circle(deco, color, (cx, cy), r)
        surf.blit(deco, (0, 0))
    return surf


def load_image_fit(path, size):
    """按给定尺寸等比缩放并居中裁剪加载图片。"""
    img = pygame.image.load(path).convert_alpha()
    return fit_surface(img, size)


def fit_surface(img, size):
    w, h = size
    iw, ih = img.get_size()
    scale = max(w / iw, h / ih)
    img = pygame.transform.smoothscale(img, (max(1, int(iw * scale)), max(1, int(ih * scale))))
    rect = img.get_rect(center=(w // 2, h // 2))
    canvas = pygame.Surface((w, h), pygame.SRCALPHA)
    canvas.blit(img, rect.topleft)
    return canvas


def clip_circle(surface, image, center, radius):
    """把图片裁剪成圆形后绘制。"""
    size = radius * 2
    img = fit_surface(image, (size, size))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    img = img.copy()
    img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(img, (center[0] - radius, center[1] - radius))


def clip_rounded(surface, image, rect, radius=18):
    """把图片按圆角矩形裁剪后绘制。"""
    rect = pygame.Rect(rect)
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=radius)
    image = pygame.transform.smoothscale(image, rect.size)
    image = image.copy()
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(image, rect.topleft)


# ---------------------------------------------------------------- 按钮

class Button:
    STYLES = {
        "primary": {"bg": PRIMARY, "bg_hover": PRIMARY_DARK, "fg": (255, 255, 255), "border": None},
        "gold": {"bg": ACCENT, "bg_hover": (214, 150, 26), "fg": (74, 48, 4), "border": None},
        "ghost": {"bg": CARD, "bg_hover": PRIMARY_SOFT, "fg": TEXT, "border": OPTION_BORDER},
    }

    def __init__(self, rect, label, style="primary", font_size=24, radius=16):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.style = self.STYLES.get(style, self.STYLES["primary"])
        self.font = get_font(font_size, bold=True)
        self.radius = radius
        self.hover = False
        self.enabled = True

    def update(self, mouse_pos):
        self.hover = self.enabled and self.rect.collidepoint(mouse_pos)

    def hit(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def draw(self, surface):
        style = self.style
        bg = style["bg_hover"] if (self.hover and self.enabled) else style["bg"]
        if not self.enabled:
            bg = (206, 209, 218)
        draw_rounded_rect(surface, self.rect, bg, self.radius)
        if style["border"]:
            draw_rounded_rect(surface, self.rect, style["border"], self.radius, width=2)
        color = (255, 255, 255) if not self.enabled else style["fg"]
        draw_text(surface, self.label, self.font, color, self.rect.center, anchor="center")
