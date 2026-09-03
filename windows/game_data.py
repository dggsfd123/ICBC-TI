# -*- coding: utf-8 -*-
"""ICBCTI 人格测试数据层。

包含：四个维度定义、36 道正式题目 + 1 道彩蛋题、16 型人格档案、4 个隐藏人格。
题目与人格档案内容均来自 questions.md 与 ICBCTI.md。
"""

# ---------------------------------------------------------------- 维度定义

# score_pole：选择该极计 1 分
# high_pole / high_code：该维度得分 >= 5 时取的一极与类型字母
# low_pole  / low_code ：该维度得分 <  5 时取的一极与类型字母
DIMENSIONS = [
    {
        "key": "manage",
        "name": "向上管理",
        "score_pole": "进取",
        "high_pole": "进取(A)", "high_code": "A",
        "low_pole": "自保(P)", "low_code": "P",
        "en": "Ambitious / Preserving",
    },
    {
        "key": "clash",
        "name": "对线能力",
        "score_pole": "硬刚",
        "high_pole": "硬刚(C)", "high_code": "C",
        "low_pole": "斡旋(S)", "low_code": "S",
        "en": "Clapback / Smooth-talk",
    },
    {
        "key": "blame",
        "name": "背锅风险",
        "score_pole": "搬砖",
        "high_pole": "搬砖(G)", "high_code": "G",
        "low_pole": "画饼(V)", "low_code": "V",
        "en": "Vision-bait / Grind-work",
    },
    {
        "key": "slack",
        "name": "摸鱼指数",
        "score_pole": "躺平",
        "high_pole": "躺平(L)", "high_code": "L",
        "low_pole": "卷王(D)", "low_code": "D",
        "en": "Deadline-chaser / Last-miner",
    },
]

DIM_BY_KEY = {d["key"]: d for d in DIMENSIONS}

# 八个极的英文名（用于报告页展示）
POLE_EN = {
    "进取": "Ambitious",
    "自保": "Preserving",
    "硬刚": "Clapback",
    "斡旋": "Smooth-talk",
    "画饼": "Vision-bait",
    "搬砖": "Grind-work",
    "卷王": "Deadline-chaser",
    "躺平": "Last-miner",
}

# 四个分组的配色（主色 / 浅底）
GROUP_COLORS = {
    "红人组": {"main": (196, 18, 45), "soft": (255, 240, 242)},
    "黄人组": {"main": (198, 132, 12), "soft": (255, 246, 224)},
    "蓝人组": {"main": (40, 102, 214), "soft": (233, 241, 255)},
    "绿人组": {"main": (26, 143, 92), "soft": (231, 247, 238)},
}
DEFAULT_GROUP_COLOR = {"main": (196, 18, 45), "soft": (255, 240, 242)}

# ---------------------------------------------------------------- 题库

# 每题格式：{"dim": 维度 key, "text": 题干, "options": [{"text": 选项, "pole": 所属极}, ...]}
# 选项在运行时会被随机打乱，计分只认 pole，不认 A/B 位置。
QUESTIONS = [
    # 一、进取 Ambitious / 自保 Preserving —— 向上管理
    {"dim": "manage", "text": "领导盯着你的方案：“这事儿，还能不能有更多想象空间？”", "options": [
        {"text": "能！我明天交个升级版。", "pole": "进取"},
        {"text": "能是能，我先把这版落地。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "一个没人认领的新项目，突然砸到你头上", "options": [
        {"text": "逐步梳理任务流程。", "pole": "进取"},
        {"text": "确认任务的职责和边界", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "同事小声提醒：“这事儿以前没人这么干过。”", "options": [
        {"text": "我觉得值得试一试，反正有兜底方案。", "pole": "进取"},
        {"text": "那我再先翻翻有没有先例。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "领导看完方案：“可以，就是风险有点大。”", "options": [
        {"text": "风险大，说明天花板高。", "pole": "进取"},
        {"text": "我把风险点逐条补上。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "有个跨部门项目，干好了大老板能记住你", "options": [
        {"text": "这不就是我的机会？冲。", "pole": "进取"},
        {"text": "先算算投入产出再说。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "组里有个谁都不肯接的硬骨头", "options": [
        {"text": "放着别动，我来啃。", "pole": "进取"},
        {"text": "先打听下为啥没人接。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "你手下的员工提了个大胆又有点冒险的想法", "options": [
        {"text": "先小范围试一版看看。", "pole": "进取"},
        {"text": "先把风险评估做扎实。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "你发现个机会：成了部门露脸，砸了自己扛", "options": [
        {"text": "赌一把，赢了算我们的。", "pole": "进取"},
        {"text": "再观望观望，不急。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "这项目干好干砸，大老板都会看见", "options": [
        {"text": "怕啥，爱拼才会赢。", "pole": "进取"},
        {"text": "那我得再掂量掂量。", "pole": "自保"},
    ]},

    # 二、硬刚 Clapback / 斡旋 Smooth-talk —— 对线能力
    {"dim": "clash", "text": "合作部门第 N 次把锅甩到你面前", "options": [
        {"text": "当场说清责任边界", "pole": "硬刚"},
        {"text": "先接住，回头慢慢协调。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "平级同事当面说：“这本来就该你做。”", "options": [
        {"text": "依据呢？说出来听听。", "pole": "硬刚"},
        {"text": "那咱看看怎么配合更顺。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "下属当面怼你，语气还有点冲", "options": [
        {"text": "来，咱直接比方案。", "pole": "硬刚"},
        {"text": "有分歧是好事，慢慢拉齐。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "对齐会上，有人说了个你完全不认同的观点", "options": [
        {"text": "我不同意，问题在这儿。", "pole": "硬刚"},
        {"text": "你主要是怎么考虑的？", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "收到一封阴阳怪气的工作邮件", "options": [
        {"text": "直接打电话，说清楚。", "pole": "硬刚"},
        {"text": "客气回一封，先稳住。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "你是领导，两个组同时来抢资源", "options": [
        {"text": "两边摆事实，谁急谁先用。", "pole": "硬刚"},
        {"text": "各让一步，我来凑方案。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "新同事连续两次踩着截止线交活", "options": [
        {"text": "阴阳他，顺便PUA他一把。", "pole": "硬刚"},
        {"text": "先问问是不是有难处。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "领导提了个你觉得离谱的要求", "options": [
        {"text": "这不合理，我得提一嘴。", "pole": "硬刚"},
        {"text": "先表示理解，再给替代。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "会议室里俩人吵起来了，你是第三人", "options": [
        {"text": "先别吵，把分歧点摆出来。", "pole": "硬刚"},
        {"text": "都别急，咱目标是一样的。", "pole": "斡旋"},
    ]},

    # 三、画饼 Vision-bait / 搬砖 Grind-work —— 背锅风险
    {"dim": "blame", "text": "领导甩来一句：“这个方向你研究一下。”", "options": [
        {"text": "行，我先想清楚它的意义。", "pole": "画饼"},
        {"text": "行，我先去扒资料和数据。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "汇报前一晚，发现材料还是有点单薄", "options": [
        {"text": "先重梳一遍故事线。", "pole": "画饼"},
        {"text": "先把数据和图表补齐。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "新项目启动，大家问作为项目组长的你接下来怎么干", "options": [
        {"text": "先把愿景和蓝图讲明白。", "pole": "画饼"},
        {"text": "先把任务拆到每个人头上。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "要向领导汇报一项日常工作", "options": [
        {"text": "从战略意义讲起，格局拉满。", "pole": "画饼"},
        {"text": "直接说进展、数据和结果。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "明天开会，领导甩给你 80 页材料", "options": [
        {"text": "看目录和结论，抓主线。", "pole": "画饼"},
        {"text": "从头过一遍，边看边记。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "方向还没定，交付时间已经到了", "options": [
        {"text": "先编个故事，边做边改。", "pole": "画饼"},
        {"text": "能确定的先一件件干掉。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "领导：“这页 PPT 差点意思。”", "options": [
        {"text": "那我重捋一遍表达逻辑。", "pole": "画饼"},
        {"text": "那我去补点数据和案例。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "领导让你带领团队，同事拉住你：“这项目到底要干啥？”", "options": [
        {"text": "我给你讲讲最终蓝图。", "pole": "画饼"},
        {"text": "先说你今天要干哪几件。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "项目收尾，你觉得最该留下的是", "options": [
        {"text": "复盘成方法论，沉淀下来。", "pole": "画饼"},
        {"text": "成果、数据、问题都理清楚。", "pole": "搬砖"},
    ]},

    # 四、卷王 Deadline-chaser / 躺平 Last-miner —— 摸鱼指数
    {"dim": "slack", "text": "任务一周后才截止，你的第一反应", "options": [
        {"text": "今天先干掉五分之一。", "pole": "卷王"},
        {"text": "不急，先忙手头别的。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "领导说“明天要”，现在是今天下午", "options": [
        {"text": "今晚先把初稿肝出来。", "pole": "卷王"},
        {"text": "明早状态好，明早再说。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "还有三天截止，但需求没完全定", "options": [
        {"text": "先交一版，留出改的时间。", "pole": "卷王"},
        {"text": "先放着，等需求再明确点。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "距离正式汇报还有整整两周", "options": [
        {"text": "以终为始，现在就开始盘。", "pole": "卷王"},
        {"text": "先忙完手头，到时候说不定出现新情况。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "你带的下属总爱踩着截止线交活", "options": [
        {"text": "提前卡几个节点盯进度。", "pole": "卷王"},
        {"text": "只要最后交上来就行。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "周五下班，领导来电话：“周一给我。”", "options": [
        {"text": "行吧，周末加个班。", "pole": "卷王"},
        {"text": "喂？喂？信号不太好啊。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "晚上八点，明天开会，材料下属已经发你了", "options": [
        {"text": "先翻一遍，心里有个底。", "pole": "卷王"},
        {"text": "万事俱备，稳等明天。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "今天难得没活儿，但随时可能来新需求", "options": [
        {"text": "看会儿资料提升一下自己。", "pole": "卷王"},
        {"text": "难得清闲，先放松下颈椎。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "年度总结，还有一个月才交", "options": [
        {"text": "我早就开始攒素材了。", "pole": "卷王"},
        {"text": "等年底项目结束一起写。", "pole": "躺平"},
    ]},
]

# 第 37 题（固定最后一题，不计入四维评分，用于解锁隐藏人格）
BONUS_QUESTION = {
    "text": "如果明天就是世界末日，今天下午17:29，领导突然发来一句——"
            "“这个事情辛苦今晚推进一下。”\n你会：",
    "options": [
        {"key": "A", "text": "今日事今日毕，今晚搞定。"},
        {"key": "B", "text": "反正都世界末日了，再说吧。"},
        {"key": "C", "text": "先拉个群，大家一起看看。"},
        {"key": "D", "text": "告诉领导没问题，后天一定完美完成。"},
    ],
}

# ---------------------------------------------------------------- 16 型人格

# code -> 档案（内容取自 ICBCTI.md）
PERSONALITIES = {
    "ACVD": {"name": "未来行长", "group": "红人组", "image": "未来行长.png",
             "keyword": "降维打击", "skill": "宏大叙事构建",
             "ultimate": "“这个事情，我们不妨再往前想一步。”",
             "scene": "在茶水间给实习生规划十年蓝图。",
             "line": "“格局打开。”"},
    "ACVL": {"name": "PPT战略刺客", "group": "红人组", "image": "PPT战略刺客.png",
             "keyword": "视觉欺诈", "skill": "黑话连篇输出",
             "ultimate": "“我重新排了一版。”",
             "scene": "用炫酷的飞入动画掩盖没数据的尴尬。",
             "line": "“底层逻辑没通，我先搭个框架。”"},
    "ACGD": {"name": "WPS特种兵", "group": "红人组", "image": "WPS特种兵.png",
             "keyword": "文档爆破", "skill": "多线程写材料",
             "ultimate": "“把原文件发我。”",
             "scene": "Ctrl+C/V残影连击。",
             "line": "“这都不用手点。”"},
    "ACGL": {"name": "漏洞感知者", "group": "红人组", "image": "漏洞感知者.png",
             "keyword": "整顿职场", "skill": "硬刚不合理KPI",
             "ultimate": "“这个这么做有很大风险。”",
             "scene": "全员开始卷，他默默合上电脑。",
             "line": "“天塌了有行长顶着。”"},
    "ASVD": {"name": "资源召唤师", "group": "黄人组", "image": "资源召唤师.png",
             "keyword": "借力打力", "skill": "跨部门无缝摇人",
             "ultimate": "“我帮你问问。”",
             "scene": "一个电话，召唤出三个部门为他加班。",
             "line": "“我打过招呼了，你直接OA拉群。”"},
    "ASVL": {"name": "人形态工晓伴", "group": "黄人组", "image": "人形态工晓伴.png",
             "keyword": "绝对捧场", "skill": "自动补充情绪价值",
             "ultimate": "“消消气，来先喝杯瑞幸。”",
             "scene": "处长发火时精准递茶降温。",
             "line": "“太牛啦太牛啦。”"},
    "ASGD": {"name": "部门粘合剂", "group": "黄人组", "image": "部门粘合剂.png",
             "keyword": "和稀泥大师", "skill": "薛定谔的推进",
             "ultimate": "“大家一起对一下，我来做会议纪要。”",
             "scene": "用废话文学让吵架双方都觉得自己赢了。",
             "line": "“这个都可以协调。”"},
    "ASGL": {"name": "人形态智涌", "group": "黄人组", "image": "人形态智涌.png",
             "keyword": "人形活字典", "skill": "秒回OA消息",
             "ultimate": "“我会用最直白的方式回复你。”",
             "scene": "用3000字长文回复新人小白问题。",
             "line": "“根据XXX号文，你应该这么做。”"},
    "PCVD": {"name": "工位防御塔", "group": "蓝人组", "image": "工位防御塔.png",
             "keyword": "物理隔离", "skill": "上班戴耳机听音乐装聋",
             "ultimate": "“这个是不是要再确认一下？”",
             "scene": "办公桌文件筑起视线高墙",
             "line": "“我有个急活儿，你走OA提流程吧。”"},
    "PCVL": {"name": "退堂鼓艺术家", "group": "绿人组", "image": "退堂鼓艺术家.png",
             "keyword": "战术撤退", "skill": "列举100个风险",
             "ultimate": "“要不我们再研究研究？”",
             "scene": "需求刚念完标题已经准备申请延期。",
             "line": "“风险太大了，建议暂缓处理”"},
    "PCGD": {"name": "e企邮轰炸机", "group": "蓝人组", "image": "e企邮轰炸机.png",
             "keyword": "抄送狂魔", "skill": "工作要留痕",
             "ultimate": "“再次提醒。”",
             "scene": "项目没推进，邮件已经往返37封。",
             "line": "“烦请于今日下班前反馈。”"},
    "PCGL": {"name": "17:30下班守门员", "group": "绿人组", "image": "1730下班守门员.png",
             "keyword": "绝不逗留", "skill": "千手观音收拾背包",
             "ultimate": "“今天先到这儿。”",
             "scene": "在周会上拿《劳动法》给领导普法。",
             "line": "“明天再说。”"},
    "PSVD": {"name": "会议室DJ", "group": "蓝人组", "image": "会议室DJ.png",
             "keyword": "气氛掌控", "skill": "掌控会议进程",
             "ultimate": "“我简单补充两句。”",
             "scene": "主持人说“最后还有一个问题”，结果一发言打开了第二轮话题。",
             "line": "“我再展开一下。”"},
    "PSVL": {"name": "会议太极宗师", "group": "绿人组", "image": "会议太极宗师.png",
             "keyword": "滴水不漏", "skill": "推脱需求于无形",
             "ultimate": "“原则上没有问题，后续再沟通。”",
             "scene": "会议开了一下午，锅甩到了隔壁处室。",
             "line": "“我们保持沟通。”"},
    "PSGD": {"name": "兜底老黄牛", "group": "蓝人组", "image": "兜底老黄牛.png",
             "keyword": "填坑之王", "skill": "默默扫清遗留",
             "ultimate": "“没事，我来弄。”",
             "scene": "默默修好了三年前离职同事留下的bug。",
             "line": "“问题不大。”"},
    "PSGL": {"name": "工位炒股战神", "group": "绿人组", "image": "工位炒股战神.png",
             "keyword": "心跳玩家", "skill": "Alt+Tab极速切屏",
             "ultimate": "“去厕所找个坑操作一下。”",
             "scene": "对着K线抱头痛哭，同事以为是工作出了问题。",
             "line": "“大盘又绿了，这班得倒贴钱。”"},
}

# ---------------------------------------------------------------- 隐藏人格

# 解锁条件：第 37 题选项 + 指定人格类型 + 指定星级组合（星级即对应分数的区间）
HIDDEN_PERSONALITIES = {
    "A": {"name": "兜底老黄牛觉醒", "code": "PSGD", "image": "兜底老黄牛_觉醒.png",
          "stars": {"manage": 1, "clash": 1, "blame": 5, "slack": 1},
          "desc": "世界末日都无法阻止你拉磨。"},
    "B": {"name": "17:30守门员觉醒", "code": "PCGL", "image": "1730下班守门员_觉醒.png",
          "stars": {"manage": 1, "clash": 5, "blame": 5, "slack": 5},
          "desc": "末日可以延期，下班不能。"},
    "C": {"name": "资源召唤师觉醒", "code": "ASVD", "image": "资源召唤师_觉醒.png",
          "stars": {"manage": 5, "clash": 1, "blame": 1, "slack": 1},
          "desc": "世界都要毁灭了，你还在拉群。"},
    "D": {"name": "PPT战略刺客觉醒", "code": "ACVL", "image": "PPT战略刺客_觉醒.png",
          "stars": {"manage": 5, "clash": 5, "blame": 1, "slack": 5},
          "desc": "末日之前，不妨再画个大饼。"},
}


def star_level(score):
    """0-9 分转换为 1-5 星：8/9→5 星，6/7→4 星，4/5→3 星，2/3→2 星，0/1→1 星。"""
    if score >= 8:
        return 5
    if score >= 6:
        return 4
    if score >= 4:
        return 3
    if score >= 2:
        return 2
    return 1


def find_hidden(bonus_key, code, stars):
    """判断隐藏人格是否解锁，返回隐藏人格字典或 None。"""
    hidden = HIDDEN_PERSONALITIES.get(bonus_key)
    if not hidden:
        return None
    if hidden["code"] != code:
        return None
    for key, level in hidden["stars"].items():
        if stars.get(key) != level:
            return None
    return hidden
