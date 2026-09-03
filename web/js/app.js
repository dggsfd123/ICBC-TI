/* ICBC-TI 人格测试 —— 网页版主逻辑
 * 数据来自 js/data.js（由 tools/export_data.py 从 Windows 版导出）
 */
(function () {
  'use strict';

  var D = window.ICBCTI_DATA;
  var P = window.Poster;
  var L = P.LAYOUT;
  var DISCLAIMER = 'ICBC-TI仅供娱乐，无参考意义。';
  // 开始页用 4 张觉醒图（与 Windows 版一致）
  var AVATARS = [D.personalities['PSGD'].file, D.personalities['PCGL'].file,
    D.personalities['ASVD'].file, D.personalities['ACVL'].file];
  var FEEDBACK_DELAY = 430;
  var LETTERS = 'ABCDEFGH';

  var dimByKey = {};
  D.dimensions.forEach(function (d) { dimByKey[d.key] = d; });

  var quiz = null;
  var result = null;
  var locked = false;

  // ---------------------------------------------------------------- 工具

  function $(id) { return document.getElementById(id); }

  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // 数据里的颜色是 [r,g,b] 数组，转成 CSS 可用的 rgb(...) 字符串
  function cssColor(c) {
    return { main: 'rgb(' + c.main.join(',') + ')', soft: 'rgb(' + c.soft.join(',') + ')' };
  }

  function titleHtml() {
    return P.titleParts().map(function (part) {
      return '<span style="color:' + part.color + '">' + escapeHtml(part.text) + '</span>';
    }).join('');
  }

  function pad2(n) { return n < 10 ? '0' + n : '' + n; }

  function today() {
    var d = new Date();
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
  }

  function starLevel(score) {
    if (score >= 8) return 5;
    if (score >= 6) return 4;
    if (score >= 4) return 3;
    if (score >= 2) return 2;
    return 1;
  }

  var imageCache = {};
  function loadImage(file) {
    if (imageCache[file]) return Promise.resolve(imageCache[file]);
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () { imageCache[file] = img; resolve(img); };
      img.onerror = function () { reject(new Error(file)); };
      img.src = 'images/' + file;
    });
  }

  var toastTimer = null;
  function showToast(msg, duration) {
    var el = $('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, duration || 2200);
  }

  function showScreen(name) {
    ['start', 'quiz', 'report'].forEach(function (s) {
      $('screen-' + s).classList.toggle('active', s === name);
    });
  }

  // ---------------------------------------------------------------- 出题与计分

  function buildQuiz() {
    var qs = D.questions.map(function (q) {
      var opts = q.options.map(function (o) { return { text: o.text, pole: o.pole }; });
      shuffle(opts);
      return { text: q.text, options: opts, dim: q.dim, bonus: false, chosen: null };
    });
    shuffle(qs);
    var bonusOpts = D.bonus.options.map(function (o) { return { text: o.text, hiddenKey: o.key }; });
    shuffle(bonusOpts);
    qs.push({ text: D.bonus.text, options: bonusOpts, dim: null, bonus: true, chosen: null });
    return qs;
  }

  function findHidden(bonusKey, code, stars) {
    var h = D.hidden[bonusKey];
    if (!h || h.code !== code) return null;
    for (var k in h.stars) {
      if (h.stars.hasOwnProperty(k) && stars[k] !== h.stars[k]) return null;
    }
    return h;
  }

  function computeResult(questions) {
    var scores = {}, stars = {}, code = '', poles = [], polesEn = [], i;

    for (i = 0; i < D.dimensions.length; i++) scores[D.dimensions[i].key] = 0;

    for (i = 0; i < questions.length; i++) {
      var q = questions[i];
      if (q.bonus || !q.chosen) continue;
      if (q.chosen.pole === dimByKey[q.dim].score_pole) scores[q.dim] += 1;
    }

    for (i = 0; i < D.dimensions.length; i++) {
      var dim = D.dimensions[i];
      var s = scores[dim.key];
      if (s >= 5) { code += dim.high_code; poles.push(dim.high_pole); }
      else { code += dim.low_code; poles.push(dim.low_pole); }
      stars[dim.key] = starLevel(s);
      polesEn.push(D.poleEn[dim.high_pole.split('(')[0]]);
    }
    // polesEn 需按实际取的极来翻译
    polesEn = poles.map(function (p) { return D.poleEn[p.split('(')[0]]; });

    var bonusQ = questions[questions.length - 1];
    var bonusKey = bonusQ.chosen ? bonusQ.chosen.hiddenKey : null;
    var hidden = findHidden(bonusKey, code, stars);
    var profile = D.personalities[code];

    return {
      code: code,
      profile: profile,
      scores: scores,
      stars: stars,
      poles: poles,
      polesEn: polesEn.join(' · '),
      hidden: hidden,
      bonusKey: bonusKey,
      bonusText: bonusQ.chosen ? bonusQ.chosen.text : '',
      groupColor: cssColor(D.groupColors[profile.group] || D.defaultGroupColor),
      dimensions: D.dimensions,
      date: today(),
      disclaimer: DISCLAIMER
    };
  }

  // ---------------------------------------------------------------- 开始页

  function renderStart() {
    var row = $('avatar-row');
    row.innerHTML = AVATARS.map(function (f) {
      return '<img class="avatar" src="images/' + f + '" alt="">';
    }).join('');

    $('chip-row').innerHTML = D.dimensions.map(function (d) {
      return '<div class="chip">' + escapeHtml(d.high_pole.split('(')[0]) + ' / ' +
        escapeHtml(d.low_pole.split('(')[0]) + '</div>';
    }).join('');

    document.querySelectorAll('.disclaimer').forEach(function (el) {
      el.textContent = DISCLAIMER;
    });
  }

  // ---------------------------------------------------------------- 答题页

  function renderQuiz() {
    var q = quiz[quizIndex];
    var total = quiz.length;
    var done = quizIndex + (q.chosen ? 1 : 0);

    $('q-index').textContent = '第 ' + (quizIndex + 1) + ' / ' + total + ' 题';
    $('q-done').textContent = '已完成 ' + done + ' / ' + total;
    $('q-progress-fill').style.width = (done / total * 100) + '%';
    $('q-index-pill').textContent = '第 ' + (quizIndex + 1) + ' / ' + total + ' 题';
    $('q-tag').style.display = q.bonus ? '' : 'none';
    $('q-text').textContent = q.text;

    var box = $('q-options');
    box.className = 'q-options' + (q.bonus ? ' bonus' : '');
    box.innerHTML = '';
    q.options.forEach(function (opt, i) {
      var el = document.createElement('div');
      el.className = 'option' + (q.chosen === opt ? ' selected' : '');
      if (q.chosen && q.chosen !== opt) el.classList.add('dim');
      el.innerHTML = '<span class="opt-badge">' + LETTERS.charAt(i) + '</span>' +
        '<span class="opt-text">' + escapeHtml(opt.text) + '</span>' +
        '<span class="opt-flag">已记录</span>';
      el.addEventListener('click', function () { chooseOption(opt); });
      box.appendChild(el);
    });

    $('q-hint').style.visibility = q.chosen ? 'hidden' : 'visible';
  }

  var quizIndex = 0;

  function chooseOption(opt) {
    var q = quiz[quizIndex];
    if (locked || q.chosen) return;
    q.chosen = opt;
    locked = true;
    renderQuiz();
    setTimeout(function () {
      locked = false;
      if (quizIndex >= quiz.length - 1) {
        result = computeResult(quiz);
        renderReport();
        showScreen('report');
      } else {
        quizIndex += 1;
        renderQuiz();
      }
    }, FEEDBACK_DELAY);
  }

  function startQuiz() {
    quiz = buildQuiz();
    quizIndex = 0;
    locked = false;
    result = null;
    renderQuiz();
    showScreen('quiz');
  }

  // ---------------------------------------------------------------- 报告页

  function starsHtml(level) {
    var out = '';
    for (var i = 0; i < 5; i++) {
      out += '<span class="star' + (i < level ? ' on' : '') + '">★</span>';
    }
    return out;
  }

  function renderReport() {
    var r = result;
    var p = r.profile;
    var gc = r.groupColor;
    var plan = P.computeLayout(r);
    var name = r.hidden ? r.hidden.name : p.name;
    var imgFile = r.hidden ? r.hidden.file : p.file;
    var cx = L.width / 2;
    var html = '';

    html += '<div class="r-title" style="left:' + L.innerX + 'px;top:' + L.headerY + 'px">' +
      titleHtml() + '</div>';
    html += '<div class="r-date" style="right:78px;top:' + L.headerY + 'px">' + r.date + '</div>';
    html += '<div class="r-divider" style="left:' + L.innerX + 'px;top:' + L.dividerY +
      'px;width:' + L.innerW + 'px"></div>';
    html += '<img class="r-img" src="images/' + imgFile +
      '" style="left:' + ((L.width - L.imgSize) / 2) + 'px;top:' + L.imgY +
      'px;width:' + L.imgSize + 'px;height:' + L.imgSize + 'px" alt="">';
    html += '<div class="r-code" style="top:' + L.codeY + 'px;color:' + gc.main + '">' +
      escapeHtml(r.code) + '</div>';
    html += '<div class="r-en" style="top:' + L.enY + 'px">' + escapeHtml(r.polesEn) + '</div>';
    html += '<div class="r-name" style="top:' + L.nameY + 'px;color:' +
      (r.hidden ? P.COLORS.accentText : P.COLORS.text) + '">【' + escapeHtml(name) + '】</div>';

    html += '<div class="r-group" style="top:' + L.groupY + 'px;background:' + gc.soft +
      ';color:' + gc.main + '">' + escapeHtml(p.group) + '</div>';
    html += '<div class="r-poles" style="top:' + L.polesY + 'px">' +
      escapeHtml(r.poles.join(' · ')) + '</div>';

    // 隐藏人格
    var info = plan.hiddenInfo;
    html += '<div class="r-hidden" style="left:' + L.innerX + 'px;top:' + L.hiddenY +
      'px;width:' + L.innerW + 'px;height:' + plan.hiddenH + 'px;background:' + info.bg +
      ';border-color:' + info.border + '">';
    info.blocks.forEach(function (b, i) {
      html += '<div class="r-hidden-line" style="font-size:' + b.font + 'px;color:' + b.color +
        ';font-weight:' + (b.bold ? '700' : '400') + ';line-height:' + (b.font + 4) + 'px' +
        (i < info.blocks.length - 1 ? ';margin-bottom:' + L.hiddenGap + 'px' : '') + '">' +
        escapeHtml(b.text) + '</div>';
    });
    html += '</div>';

    // 四维星级
    r.dimensions.forEach(function (dim, i) {
      var x = L.innerX + i * (L.cellW + L.cellGap);
      html += '<div class="star-cell" style="left:' + x + 'px;top:' + plan.starsY +
        'px;width:' + L.cellW + 'px">' +
        '<div class="star-label">' + escapeHtml(dim.name) + '</div>' +
        '<div class="star-row">' + starsHtml(r.stars[dim.key]) + '</div>' +
        '<div class="star-score">' + r.scores[dim.key] + ' / 9</div></div>';
    });

    // 人格解读
    html += '<div class="r-reading-title" style="left:' + L.innerX + 'px;top:' + plan.readingY +
      'px">人格解读</div>';
    html += '<div class="r-reading-bar" style="left:' + L.innerX + 'px;top:' +
      (plan.readingY + 42) + 'px"></div>';

    html += '<div class="r-items" style="left:' + L.innerX + 'px;top:' + plan.itemsY +
      'px;width:' + L.innerW + 'px">';
    [['关键词', p.keyword], ['核心技能', p.skill], ['大招', p.ultimate],
      ['名场面', p.scene], ['经典台词', p.line]].forEach(function (it) {
      html += '<div class="r-item" style="margin-bottom:' + plan.itemGap + 'px">' +
        '<div class="r-item-label">' + escapeHtml(it[0]) + '</div>' +
        '<div class="r-item-value" style="font-size:' + plan.valueFont + 'px;line-height:' +
        plan.lineH + 'px">' + escapeHtml(it[1]) + '</div></div>';
    });
    html += '</div>';

    $('report-card').innerHTML = html;
  }

  // ---------------------------------------------------------------- 导出海报

  function exportPoster() {
    showToast('正在生成海报…', 5000);
    var canvas = document.createElement('canvas');
    canvas.width = L.width;
    canvas.height = L.posterH;
    var ctx = canvas.getContext('2d');
    P.draw(ctx, result, loadImage).then(function () {
      var url;
      try {
        url = canvas.toDataURL('image/png');
      } catch (e) {
        showToast('浏览器安全限制：请通过网址访问，不要直接双击打开 HTML', 4000);
        return;
      }
      showShare(url);
      showToast('海报已生成，可下载或长按保存', 2600);
    }).catch(function (err) {
      showToast('生成失败：' + err.message, 3500);
    });
  }

  function showShare(url) {
    var name = result.hidden ? result.hidden.name : result.profile.name;
    $('share-img').src = url;
    $('btn-save').setAttribute('data-url', url);
    $('btn-save').setAttribute('data-name',
      'ICBC-TI_' + result.code + '_' + name + '.png');
    $('share-layer').classList.add('active');
  }

  function saveShare() {
    var btn = $('btn-save');
    var a = document.createElement('a');
    a.href = btn.getAttribute('data-url');
    a.download = btn.getAttribute('data-name');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // ---------------------------------------------------------------- 舞台缩放

  function resize() {
    var scale = Math.min(window.innerWidth / L.width, window.innerHeight / 1920);
    $('stage').style.transform = 'scale(' + scale + ')';
  }

  // ---------------------------------------------------------------- 启动

  function init() {
    renderStart();
    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('orientationchange', resize);

    $('btn-start').addEventListener('click', startQuiz);
    $('btn-export').addEventListener('click', exportPoster);
    $('btn-again').addEventListener('click', function () {
      showScreen('start');
    });
    $('btn-save').addEventListener('click', saveShare);
    $('btn-share-close').addEventListener('click', function () {
      $('share-layer').classList.remove('active');
    });
    $('share-layer').addEventListener('click', function (e) {
      if (e.target === $('share-layer')) $('share-layer').classList.remove('active');
    });

    // 预加载：先加载开始页头像，再后台加载其余人格图
    AVATARS.forEach(function (f) { loadImage(f).catch(function () {}); });
    setTimeout(function () {
      Object.keys(D.personalities).forEach(function (code) {
        loadImage(D.personalities[code].file).catch(function () {});
      });
      Object.keys(D.hidden).forEach(function (k) {
        loadImage(D.hidden[k].file).catch(function () {});
      });
    }, 800);

    showScreen('start');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
