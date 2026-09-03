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
    {"dim": "manage", "text": "领导问：“这个项目你觉得还有没有更大的想象空间？”", "options": [
        {"text": "有，我们可以直接往更大方向做。", "pole": "进取"},
        {"text": "先把现有方案稳稳落地，后续稳步推进。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "一个新项目突然找上你，但没人明确说谁负责。", "options": [
        {"text": "先接下来，边做边理。", "pole": "进取"},
        {"text": "先确认一下职责和边界。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "同事说：“这个事情以前没这么干过。”", "options": [
        {"text": "“所以才值得试试。”", "pole": "进取"},
        {"text": "“那最好先看看有没有先例。”", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "你的方案被领导说：“可以，但风险也不小。”", "options": [
        {"text": "解释怎么把风险变成机会。", "pole": "进取"},
        {"text": "先把风险点逐项补齐。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "突然有一个跨部门机会，可以让你被更多领导看到。", "options": [
        {"text": "必须拿下，让领导看看我的实力。", "pole": "进取"},
        {"text": "先看看投入产出。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "一个大项目出现一个没人愿意接的“硬骨头”。", "options": [
        {"text": "舍我其谁，必须拿下。", "pole": "进取"},
        {"text": "先搞清楚为什么没人接。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "你手下的新员工提出一个大胆但有风险的想法。", "options": [
        {"text": "先做个小范围试点。", "pole": "进取"},
        {"text": "先把风险评估做好。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "你发现一个机会，可能让部门出彩，但也可能失败。", "options": [
        {"text": "押上部门绩效，赌把大的。", "pole": "进取"},
        {"text": "再观察一下。", "pole": "自保"},
    ]},
    {"dim": "manage", "text": "如果一个项目成功和失败会被大老板看见。", "options": [
        {"text": "冲一把，爱拼才会赢。", "pole": "进取"},
        {"text": "没必要冒那个险。", "pole": "自保"},
    ]},

    # 二、硬刚 Clapback / 斡旋 Smooth-talk —— 对线能力
    {"dim": "clash", "text": "和你合作的部门总是把问题甩给你。", "options": [
        {"text": "当场把责任边界说清楚。", "pole": "硬刚"},
        {"text": "先把事情接住，再慢慢协调。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "平级的同事当面说：“这个工作本来就应该你做。”", "options": [
        {"text": "“你的依据是什么？”", "pole": "硬刚"},
        {"text": "“我们先看看怎么配合比较合适。”", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "你的下属提出不同意见，而且语气比较直接。", "options": [
        {"text": "直接讨论谁的方案更合理。", "pole": "硬刚"},
        {"text": "先认可分歧，再慢慢拉共识。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "对齐颗粒度的会上有人提出一个你明显不同意的观点。", "options": [
        {"text": "马上指出问题。", "pole": "硬刚"},
        {"text": "先问一句：“你的考虑主要是什么？”", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "收到一封语气不太友好的工作邮件。", "options": [
        {"text": "打个电话，把事情说清楚。", "pole": "硬刚"},
        {"text": "邮件里保持客气并回复。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "你是领导，手下两个部门都想要同一个资源。", "options": [
        {"text": "摆事实、讲需求，让他们直接争。", "pole": "硬刚"},
        {"text": "协调双方都能接受的方案。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "你手下的新员工连续两次拖延任务。", "options": [
        {"text": "找他谈话，怼他，PUA他。", "pole": "硬刚"},
        {"text": "先了解原因，再想办法推动。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "领导的要求你觉得明显不合理。", "options": [
        {"text": "会后单独找领导提出异议。", "pole": "硬刚"},
        {"text": "私下跟领导说理解与替代方案。", "pole": "斡旋"},
    ]},
    {"dim": "clash", "text": "两个人在会议室吵起来了，你是第三个人。", "options": [
        {"text": "“先把分歧点说清楚。”", "pole": "硬刚"},
        {"text": "“大家其实目标是一致的。”", "pole": "斡旋"},
    ]},

    # 三、画饼 Vision-bait / 搬砖 Grind-work —— 背锅风险
    {"dim": "blame", "text": "领导给你一个模糊任务：“你去研究一下这个方向。”", "options": [
        {"text": "先想清楚项目意义和整体框架。", "pole": "画饼"},
        {"text": "先找资料、数据、案例。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "汇报前一天，你发现材料内容还不够丰富。", "options": [
        {"text": "先重新梳理故事线。", "pole": "画饼"},
        {"text": "先把数据和材料补齐。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "大家讨论一个新项目怎么做。", "options": [
        {"text": "“我们先把愿景想清楚。”", "pole": "画饼"},
        {"text": "“先拆一下具体任务。”", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "你要向领导介绍一个普通的日常工作。", "options": [
        {"text": "强调它对整体战略的意义。", "pole": "画饼"},
        {"text": "讲当前进展、数据和结果。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "明天沟通会，领导给你一份80页材料。", "options": [
        {"text": "主要看目录和核心逻辑。", "pole": "画饼"},
        {"text": "高效率看完并且记笔记。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "一个项目方向还没完全确定，但时间已经到了。", "options": [
        {"text": "先定一个故事，再边做边调整。", "pole": "画饼"},
        {"text": "先把确定的事情一件件做掉。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "领导说：“这页PPT感觉还差点意思。”", "options": [
        {"text": "重新想表达逻辑。", "pole": "画饼"},
        {"text": "先补图表、数据和案例。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "领导让你带领团队，同事问你：“这个项目到底想干嘛？”", "options": [
        {"text": "讲清楚最终蓝图。", "pole": "画饼"},
        {"text": "先告诉他今天具体干什么。", "pole": "搬砖"},
    ]},
    {"dim": "blame", "text": "项目结束，你觉得最重要的是：", "options": [
        {"text": "总结经验，形成方法论。", "pole": "画饼"},
        {"text": "把成果、数据和问题整理清楚。", "pole": "搬砖"},
    ]},

    # 四、卷王 Deadline-chaser / 躺平 Last-miner —— 摸鱼指数
    {"dim": "slack", "text": "任务截止安排在一周以后，你第一反应：", "options": [
        {"text": "今天先做掉1/5。", "pole": "卷王"},
        {"text": "不急，手头还有其它任务。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "领导说明天要材料，现在是今天下午。", "options": [
        {"text": "今天晚上先把初稿搞出来。", "pole": "卷王"},
        {"text": "明天早上状态最好，明早再做。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "一个任务还有三天截止，但需求没完全明确。", "options": [
        {"text": "先交一版，后续留时间修改。", "pole": "卷王"},
        {"text": "先放着，等需求明确一点。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "项目距离正式汇报还有两周。", "options": [
        {"text": "以终为始，开始规划最终材料。", "pole": "卷王"},
        {"text": "先把手头工作做完，到时候可能会有新情况。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "你发现某个下属总喜欢临近截止才交东西。", "options": [
        {"text": "提前设几个节点盯进度。", "pole": "卷王"},
        {"text": "只要最后交出来就行。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "周五下午下班，领导打电话跟你说：“下周一给我。”", "options": [
        {"text": "周末加个班。", "pole": "卷王"},
        {"text": "唉，喂？喂？信号不好。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "现在晚上8点，明天上午开会，会议材料你的下属已经发给你了。", "options": [
        {"text": "先把材料翻一翻。", "pole": "卷王"},
        {"text": "万事俱备等明天。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "今天没什么事，但可能随时有突发新任务。", "options": [
        {"text": "看看资料提升一下自我。", "pole": "卷王"},
        {"text": "难得清闲，放松下颈椎。", "pole": "躺平"},
    ]},
    {"dim": "slack", "text": "年度总结，距离提交还有一个月。", "options": [
        {"text": "早就开始积累素材了。", "pole": "卷王"},
        {"text": "等年底项目完事一起弄。", "pole": "躺平"},
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
