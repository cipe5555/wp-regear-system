from collections import Counter

# 提取裝備名稱列表
equipment_list = [
    "謎團法杖T7", "刺客兜帽T8", "審判者護甲T5.3", "傭兵鞋子T8", "Martlock披風T4.3", "迅爪T5.1",
    "謎團法杖T6.1", "刺客兜帽T6.2", "審判者護甲T4.4", "學者便鞋T7.1", "Martlock披風T4.2", "迅爪T5.1",
    "擁王者T6.2", "牧師風帽T7.1", "惡棍外套T6.2", "傭兵鞋子T7.1", "Fort Sterling披風T4.3", "迅爪T5.1",
    "永凍稜鏡T5.3", "刺客兜帽T8", "學者長袍T8", "潛行者鞋子T7.1", "Lymhurst披風T4.3", "騎乘馬T3",
    "祕術長杖T6.1", "刺客兜帽T6.2", "騎士護甲T7.1", "傭兵鞋子T6.2", "Martlock披風T4.2", "鐵甲馬T5",
    "大地符文法杖T5.3", "牧師風帽T6.2", "騎士護甲T8.1", "皇家鞋子T5.3", "摩根娜披風T4.3", "駝鹿T6",
    "戰鬥腕甲T8.1", "士兵頭盔T8", "惡棍外套T5.3", "潛行者鞋子T7.1", "Lymhurst披風T4.3", "迅爪T5.1",
    "瘟疫法杖T6.2", "刺客兜帽T8", "牧師長袍T6.2", "傭兵鞋子T6.2", "Lymhurst披風T4.3", "配鞍灰狼T5",
    "斷水劍T6.2", "騎士頭盔T8", "守衛者護甲T6.2", "守墓者長靴T5.3", "Brecilien披風T4.2", "騎乘馬T3",
    "血月法杖T4.3", "潛行者兜帽T6.1", "傭兵外套T6.1", "純潔便鞋T4.3", "Caerleon披風T4.3", "鐵甲馬T5",
    "墮落法杖T6.2", "士兵頭盔T8", "迷霧行者外套T4.4", "牧師便鞋T7.1", "Lymhurst披風T4.3", "迅爪T5.1",
    "永凍稜鏡T6.2", "刺客兜帽T6.2", "學者長袍T8", "守墓者長靴T7.1", "Lymhurst披風T4.2", "迅爪T5.1"
]

# 統計各裝備出現次數
equipment_count = Counter(equipment_list)

# 排序並顯示結果
sorted_equipment = sorted(equipment_count.items(), key=lambda x: x[1], reverse=True)
sorted_equipment
