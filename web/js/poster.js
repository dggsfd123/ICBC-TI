/* 报告海报绘制（Canvas 自绘）
 * 屏幕上的报告 DOM 与导出的 PNG 海报共用同一套 LAYOUT 坐标，
 * 改排版时只改这里，两边同步生效。
 */
(function (global) {
  'use strict';

  var FONT_STACK = '"PingFang SC","Microsoft YaHei","Hiragino Sans GB","Heiti SC",' +
    '"Source Han Sans SC","Noto Sans CJK SC",sans-serif';

  var COLORS = {
    bgTop: '#FDF8F4', bgBot: '#EEF1F7',
    card: '#FFFFFF', cardBorder: '#E7E9F0',
    text: '#1C1E29', textSub: '#6E7486', textLight: '#969CAC',
    primary: '#C4122D',
    accent: '#E8A828', accentSoft: '#FFF7E6', accentText: '#A8760C',
    optionBorder: '#DEE2EB', softFill: '#F8F9FC',
    starOn: '#E8A828', starOff: '#E0E3EA',
    shadow: 'rgba(26,32,56,0.11)'
  };

  // 与 Windows 版报告页一致的布局坐标（逻辑画布 1080 宽）
  var LAYOUT = {
    width: 1080,
    cardX: 44, cardY: 34, cardW: 992, cardBottom: 1760, posterH: 1850,
    innerX: 78, innerW: 924,
    headerY: 76, titleFont: 26, dateFont: 21, dividerY: 128,
    imgSize: 360, imgY: 142,
    codeY: 534, codeFont: 68,
    enY: 636, enFont: 23,
    nameY: 676, nameFont: 40,
    groupY: 738, groupH: 44, groupFont: 24,
    polesY: 798, polesFont: 26,
    hiddenY: 842, hiddenPad: 22, hiddenGap: 12,
    hiddenTitleFont: 25, hiddenDescFont: 25, hiddenTipFont: 19, hiddenLine2Font: 22,
    starsGap: 40, cellW: 216, cellGap: 20, starSize: 13, starGap: 10,
    starsLabelFont: 22, starsScoreFont: 19, starsH: 104,
    readingGap: 48, readingTitleFont: 27, readingBodyGap: 92,
    itemLabelFont: 19, itemSizes: [32, 30, 28, 26, 24, 22], itemLineGap: 8,
    itemGapMin: 10, itemGapMax: 28,
    footerFont: 21, footerBottom: 20,
    buttonY: 1780, buttonH: 80
  };

  var NO_LINE_START = '。，、；：？！”』」）】》…—·.,;:!?)]}%';

  var measureCtx = null;
  function getMeasureCtx() {
    if (!measureCtx) {
      measureCtx = document.createElement('canvas').getContext('2d');
    }
    return measureCtx;
  }

  function setFont(ctx, size, bold) {
    ctx.font = (bold ? 'bold ' : '') + size + 'px ' + FONT_STACK;
  }

  // canvas 没有 getHeight()，用 1.35 倍字号近似中文字体的行高
  function lh(size, extra) {
    return Math.round(size * 1.35) + (extra || 0);
  }

  function wrapText(ctx, text, maxWidth) {
    var lines = [];
    var paragraphs = String(text).split('\n');
    for (var p = 0; p < paragraphs.length; p++) {
      var para = paragraphs[p];
      if (para === '') { lines.push(''); continue; }
      var cur = '';
      for (var i = 0; i < para.length; i++) {
        var ch = para.charAt(i);
        if (cur === '' || ctx.measureText(cur + ch).width <= maxWidth) {
          cur += ch;
        } else if (NO_LINE_START.indexOf(ch) >= 0 && cur.length >= 2) {
          lines.push(cur.slice(0, -1));
          cur = cur.slice(-1) + ch;
        } else {
          lines.push(cur);
          cur = ch;
        }
      }
      if (cur !== '') lines.push(cur);
    }
    return lines;
  }

  function drawParagraph(ctx, text, x, y, maxWidth, lineHeight, align) {
    var lines = wrapText(ctx, text, maxWidth);
    var cx = x;
    for (var i = 0; i < lines.length; i++) {
      if (align === 'center') {
        cx = x + (maxWidth - ctx.measureText(lines[i]).width) / 2;
      } else if (align === 'right') {
        cx = x + maxWidth - ctx.measureText(lines[i]).width;
      }
      ctx.fillText(lines[i], cx, y + i * lineHeight);
    }
    return y + lines.length * lineHeight;
  }

  function roundRectPath(ctx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function fillRoundRect(ctx, x, y, w, h, r, color) {
    roundRectPath(ctx, x, y, w, h, r);
    ctx.fillStyle = color || ctx.fillStyle;
    ctx.fill();
  }

  function strokeRoundRect(ctx, x, y, w, h, r, color, width) {
    roundRectPath(ctx, x, y, w, h, r);
    ctx.strokeStyle = color;
    ctx.lineWidth = width || 2;
    ctx.stroke();
  }

  function drawStar(ctx, cx, cy, r, filled) {
    var pts = [];
    for (var i = 0; i < 10; i++) {
      var rr = (i % 2 === 0) ? r : r * 0.45;
      var a = -Math.PI / 2 + i * Math.PI / 5;
      pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]);
    }
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (var j = 1; j < pts.length; j++) ctx.lineTo(pts[j][0], pts[j][1]);
    ctx.closePath();
    ctx.fillStyle = filled ? COLORS.starOn : COLORS.starOff;
    ctx.fill();
  }

  function drawStarsRow(ctx, x, y, level, size, gap) {
    for (var i = 0; i < 5; i++) {
      drawStar(ctx, x + size + i * (size * 2 + gap), y + size, size, i < level);
    }
  }

  function drawBackground(ctx, w, h) {
    var g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, COLORS.bgTop);
    g.addColorStop(1, COLORS.bgBot);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    var deco = [[80, 90, 190, '196,18,45'], [w - 60, h - 40, 240, '60,90,180'],
      [w - 120, 120, 130, '232,168,40'], [120, h - 120, 150, '196,18,45']];
    for (var i = 0; i < deco.length; i++) {
      ctx.beginPath();
      ctx.fillStyle = 'rgba(' + deco[i][3] + ',0.05)';
      ctx.arc(deco[i][0], deco[i][1], deco[i][2], 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function itemPairs(profile) {
    return [['关键词', profile.keyword], ['核心技能', profile.skill],
      ['大招', profile.ultimate], ['名场面', profile.scene], ['经典台词', profile.line]];
  }

  function hiddenBlocks(result) {
    var hidden = result.hidden;
    if (hidden) {
      return {
        bg: COLORS.accentSoft, border: COLORS.accent,
        blocks: [
          { font: LAYOUT.hiddenTitleFont, bold: true, color: COLORS.accentText,
            text: '隐藏人格 · ' + hidden.name },
          { font: LAYOUT.hiddenDescFont, bold: true, color: COLORS.text, text: hidden.desc },
          { font: LAYOUT.hiddenTipFont, bold: false, color: COLORS.textSub,
            text: '解锁条件：第37题选 ' + result.bonusKey + ' ＋ ' + hidden.code + ' 型指定星级组合' }
        ]
      };
    }
    return {
      bg: COLORS.softFill, border: COLORS.optionBorder,
      blocks: [
        { font: LAYOUT.hiddenTitleFont, bold: true, color: COLORS.textSub, text: '隐藏人格未解锁' },
        { font: LAYOUT.hiddenLine2Font, bold: false, color: COLORS.textSub,
          text: '第37题你选择了「' + result.bonusText + '」' },
        { font: LAYOUT.hiddenTipFont, bold: false, color: COLORS.textLight,
          text: '极端作答并达成指定星级组合，才能触发 4 种隐藏人格之一' }
      ]
    };
  }

  function measureHiddenHeight(result) {
    var ctx = getMeasureCtx();
    var info = hiddenBlocks(result);
    var innerW = LAYOUT.innerW - 44;
    var total = 0;
    for (var i = 0; i < info.blocks.length; i++) {
      var b = info.blocks[i];
      setFont(ctx, b.font, b.bold);
      total += wrapText(ctx, b.text, innerW).length * lh(b.font, 4);
    }
    return { h: LAYOUT.hiddenPad * 2 + total + LAYOUT.hiddenGap * (info.blocks.length - 1), info: info };
  }

  /* 计算报告正文的自适应布局：供 DOM 渲染与海报绘制共用 */
  function computeLayout(result) {
    var L = LAYOUT;
    var ctx = getMeasureCtx();
    var m = measureHiddenHeight(result);
    var starsY = L.hiddenY + m.h + L.starsGap;
    var readingY = starsY + L.starsH + L.readingGap;
    var itemsY = readingY + L.readingBodyGap;

    var items = itemPairs(result.profile);
    var labelH = lh(L.itemLabelFont, 4);
    var available = (L.cardBottom - 34) - itemsY;
    var valueFont = L.itemSizes[L.itemSizes.length - 1];
    var lineH = lh(valueFont, L.itemLineGap);
    for (var s = 0; s < L.itemSizes.length; s++) {
      var size = L.itemSizes[s];
      setFont(ctx, size, false);
      var total = 0;
      for (var i = 0; i < items.length; i++) {
        total += labelH + wrapText(ctx, items[i][1], L.innerW).length * lh(size, L.itemLineGap);
      }
      if (total + L.itemGapMin * items.length <= available) {
        valueFont = size;
        lineH = lh(size, L.itemLineGap);
        break;
      }
    }
    setFont(ctx, valueFont, false);
    var body = 0;
    for (var k = 0; k < items.length; k++) {
      body += labelH + wrapText(ctx, items[k][1], L.innerW).length * lineH;
    }
    var gap = Math.floor((available - body) / items.length);
    gap = Math.max(L.itemGapMin, Math.min(L.itemGapMax, gap));

    return {
      hiddenH: m.h, hiddenInfo: m.info,
      starsY: starsY, readingY: readingY, itemsY: itemsY,
      valueFont: valueFont, lineH: lineH, itemGap: gap, labelH: labelH
    };
  }

  /* 把报告画到 canvas 上，返回 Promise */
  function draw(ctx, result, getImage) {
    var L = LAYOUT;
    var p = result.profile;
    var hidden = result.hidden;
    var gc = result.groupColor.main;
    var gcSoft = result.groupColor.soft;
    var cx = L.width / 2;
    var plan = computeLayout(result);

    drawBackground(ctx, L.width, L.posterH);

    ctx.save();
    ctx.shadowColor = COLORS.shadow;
    ctx.shadowBlur = 30;
    ctx.shadowOffsetY = 8;
    fillRoundRect(ctx, L.cardX, L.cardY, L.cardW, L.cardBottom - L.cardY, 36, COLORS.card);
    ctx.restore();

    ctx.textBaseline = 'top';

    // 头部
    ctx.textAlign = 'left';
    setFont(ctx, L.titleFont, true);
    ctx.fillStyle = COLORS.text;
    ctx.fillText('ICBC-TI 人格测试报告', L.innerX, L.headerY);
    setFont(ctx, L.dateFont, false);
    ctx.fillStyle = COLORS.textLight;
    ctx.textAlign = 'right';
    ctx.fillText(result.date, L.innerX + L.innerW, L.headerY);
    ctx.strokeStyle = COLORS.cardBorder;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(L.innerX, L.dividerY);
    ctx.lineTo(L.innerX + L.innerW, L.dividerY);
    ctx.stroke();

    // 人格图
    var imgX = (L.width - L.imgSize) / 2;
    return Promise.resolve(getImage(hidden ? hidden.image : p.image)).then(function (img) {
      ctx.save();
      roundRectPath(ctx, imgX, L.imgY, L.imgSize, L.imgSize, 28);
      ctx.clip();
      ctx.drawImage(img, imgX, L.imgY, L.imgSize, L.imgSize);
      ctx.restore();
      strokeRoundRect(ctx, imgX, L.imgY, L.imgSize, L.imgSize, 28, COLORS.cardBorder, 3);

      // 类型代码 / 英文 / 名称
      ctx.textAlign = 'center';
      setFont(ctx, L.codeFont, true);
      ctx.fillStyle = gc;
      ctx.fillText(result.code, cx, L.codeY);
      setFont(ctx, L.enFont, false);
      ctx.fillStyle = COLORS.textSub;
      ctx.fillText(result.polesEn, cx, L.enY);
      setFont(ctx, L.nameFont, true);
      ctx.fillStyle = hidden ? COLORS.accentText : COLORS.text;
      ctx.fillText('【' + (hidden ? hidden.name : p.name) + '】', cx, L.nameY);

      // 分组胶囊
      setFont(ctx, L.groupFont, true);
      var gw = ctx.measureText(p.group).width + 60;
      fillRoundRect(ctx, cx - gw / 2, L.groupY, gw, L.groupH, L.groupH / 2, gcSoft);
      ctx.fillStyle = gc;
      ctx.textBaseline = 'middle';
      ctx.fillText(p.group, cx, L.groupY + L.groupH / 2 + 1);
      ctx.textBaseline = 'top';

      // 四极
      setFont(ctx, L.polesFont, false);
      ctx.fillStyle = COLORS.textSub;
      ctx.fillText(result.poles.join(' · '), cx, L.polesY);

      // 隐藏人格
      var info = plan.hiddenInfo;
      var innerW = L.innerW - 44;
      fillRoundRect(ctx, L.innerX, L.hiddenY, L.innerW, plan.hiddenH, 22, info.bg);
      strokeRoundRect(ctx, L.innerX, L.hiddenY, L.innerW, plan.hiddenH, 22, info.border, 3);
      var by = L.hiddenY + L.hiddenPad;
      for (var i = 0; i < info.blocks.length; i++) {
        var b = info.blocks[i];
        setFont(ctx, b.font, b.bold);
        ctx.fillStyle = b.color;
        ctx.textAlign = 'left';
        by = drawParagraph(ctx, b.text, L.innerX + 22, by, innerW, lh(b.font, 4));
        if (i < info.blocks.length - 1) by += L.hiddenGap;
      }

      // 四维星级
      for (var d = 0; d < result.dimensions.length; d++) {
        var dim = result.dimensions[d];
        var cellX = L.innerX + d * (L.cellW + L.cellGap);
        var level = result.stars[dim.key];
        ctx.textAlign = 'center';
        setFont(ctx, L.starsLabelFont, true);
        ctx.fillStyle = COLORS.text;
        ctx.fillText(dim.name, cellX + L.cellW / 2, plan.starsY);
        drawStarsRow(ctx, cellX + (L.cellW - 170) / 2, plan.starsY + 36, level, L.starSize, L.starGap);
        setFont(ctx, L.starsScoreFont, false);
        ctx.fillStyle = COLORS.textLight;
        ctx.fillText(result.scores[dim.key] + ' / 9', cellX + L.cellW / 2, plan.starsY + 68);
      }

      // 人格解读
      ctx.textAlign = 'left';
      setFont(ctx, L.readingTitleFont, true);
      ctx.fillStyle = COLORS.text;
      ctx.fillText('人格解读', L.innerX, plan.readingY);
      fillRoundRect(ctx, L.innerX, plan.readingY + 42, 56, 5, 3, COLORS.primary);

      var items = itemPairs(p);
      var y = plan.itemsY;
      for (var k = 0; k < items.length; k++) {
        setFont(ctx, L.itemLabelFont, true);
        ctx.fillStyle = COLORS.textLight;
        ctx.textAlign = 'left';
        ctx.fillText(items[k][0], L.innerX, y);
        y += plan.labelH;
        setFont(ctx, plan.valueFont, false);
        ctx.fillStyle = COLORS.text;
        y = drawParagraph(ctx, items[k][1], L.innerX, y, L.innerW, plan.lineH) + plan.itemGap;
      }

      // 免责声明
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      setFont(ctx, L.footerFont, false);
      ctx.fillStyle = COLORS.textLight;
      ctx.fillText(result.disclaimer, cx, L.posterH - L.footerBottom);
      ctx.textBaseline = 'top';
    });
  }

  global.Poster = {
    LAYOUT: LAYOUT,
    COLORS: COLORS,
    FONT_STACK: FONT_STACK,
    computeLayout: computeLayout,
    hiddenBlocks: hiddenBlocks,
    draw: draw
  };
})(window);
