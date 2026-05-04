import math

# --- Функции принадлежности ---

def trimf(x, a, b, c):
    if b == a:
        part1 = 1.0 if x >= a else 0.0
    else:
        part1 = (x - a) / (b - a)
    
    if c == b:
        part2 = 1.0 if x <= b else 0.0
    else:
        part2 = (c - x) / (c - b)
        
    return max(min(part1, part2), 0)

def trapmf(x, a, b, c, d):
    if b == a:
        part1 = 1.0 if x >= a else 0.0
    else:
        part1 = (x - a) / (b - a)
    
    if d == c:
        part2 = 1.0 if x <= d else 0.0
    else:
        part2 = (d - x) / (d - c)
        
    return max(min(part1, 1.0, part2), 0)

# --- Фазификация ---

def fuzzify(grammar, vocab, listen):
    g_low = trapmf(grammar, 0, 0, 2, 4)
    g_med = trimf(grammar, 2, 5, 8)
    g_high = trapmf(grammar, 6, 8, 10, 10)

    v_low = trapmf(vocab, 0, 0, 2, 4)
    v_med = trimf(vocab, 2, 5, 8)
    v_high = trapmf(vocab, 6, 8, 10, 10)

    l_low = trapmf(listen, 0, 0, 2, 4)
    l_med = trimf(listen, 2, 5, 8)
    l_high = trapmf(listen, 6, 8, 10, 10)

    return {
        'g': {'low': g_low, 'med': g_med, 'high': g_high},
        'v': {'low': v_low, 'med': v_med, 'high': v_high},
        'l': {'low': l_low, 'med': l_med, 'high': l_high}
    }

# --- База правил и Вывод ---

def calculate_level(grammar, vocab, listen):
    mf = fuzzify(grammar, vocab, listen)
    
    rules = []
    
    # Правила вывода уровня
    r1 = min(mf['g']['low'], mf['v']['low'], mf['l']['low'])
    rules.append({'name': 'Все навыки низкие -> A1', 'weight': r1, 'center': 0.5})

    r2 = min(mf['g']['med'], mf['v']['low'])
    rules.append({'name': 'Грамматика средняя, Словарь базовый -> A2', 'weight': r2, 'center': 1.5})

    r3 = min(mf['l']['high'], mf['g']['low'])
    rules.append({'name': 'Слух отличный, Грамматика слабая (Геймер) -> B1', 'weight': r3, 'center': 2.5})

    r4 = min(mf['g']['med'], mf['v']['med'], mf['l']['med'])
    rules.append({'name': 'Все навыки средние -> B1', 'weight': r4, 'center': 2.5})

    r5 = min(mf['g']['high'], mf['v']['high'])
    rules.append({'name': 'Грамматика и Словарь отличные -> C1', 'weight': r5, 'center': 4.5})

    r6 = min(mf['g']['high'], mf['v']['high'], mf['l']['high'])
    rules.append({'name': 'Все навыки на максимуме -> C2', 'weight': r6, 'center': 5.5})

    r7 = min(mf['v']['high'], mf['l']['med'])
    rules.append({'name': 'Словарь продвинутый, Слух средний -> B2', 'weight': r7, 'center': 3.5})

    r9 = min(mf['g']['high'], mf['l']['low'])
    rules.append({'name': 'Грамматика отличная, Слух слабый (Теоретик) -> B1', 'weight': r9, 'center': 2.5})

    # Дефаззификация
    numerator = sum(r['weight'] * r['center'] for r in rules)
    denominator = sum(r['weight'] for r in rules)
    
    score = numerator / denominator if denominator != 0 else 0

    # ЛОГИЧЕСКИЕ ОГРАНИЧЕНИЯ НА ОСНОВЕ ЗАВИСИМОСТЕЙ НАВЫКОВ
    
    # Если словарный запас почти нулевой (<=2), то уровень не может быть выше A2 (индекс 1.5)
    if vocab <= 2:
        if score > 1.5:
            score = 1.5
    
    # Если грамматика почти нулевая (<=2), то уровень не может быть выше A2
    if grammar <= 2:
        if score > 1.5:
            score = 1.5
    
    # Если аудирование очень низкое (<=2), но другие навыки высокие — всё равно ограничиваем до B1
    if listen <= 2 and (grammar > 5 or vocab > 5):
        if score > 2.5:
            score = 2.5
    
    # --- ГЕНЕРАЦИЯ КОНКРЕТНЫХ РЕКОМЕНДАЦИЙ ---
    
    level = ""
    rec_parts = []
    color = ""

    # 1. Определяем общий уровень и цвет
    if score <= 1.5:   # Важно: здесь должно быть <=, чтобы 1.5 попало в A1-A2
        level = "A1-A2"
        color = "#e74c3c"
    elif score < 2.5:
        level = "B1"
        color = "#f1c40f"
    elif score <= 3.5:
        level = "B2"
        color = "#3498db"
    else:
        level = "C1-C2"
        color = "#2ecc71"

    # 2. Конкретные советы по Грамматике
    if grammar <= 3:
        rec_parts.append("ГРАММАТИКА: Начни с основ. Выучи глагол to be, местоимения и Present Simple. Твоя цель — построить простое предложение без ошибок.")
    elif 4 <= grammar <= 6:
        rec_parts.append("ГРАММАТИКА: Разберись с временами группы Past (Simple/Continuous) и Future Simple. Научись задавать вопросы в разных временах.")
    elif 7 <= grammar <= 8:
        rec_parts.append("ГРАММАТИКА: Подтяни Perfect-времена (Present/Past Perfect) и условные предложения (Conditionals).")
    elif grammar >= 9:
        rec_parts.append("ГРАММАТИКА: Твой уровень отличный. Для совершенства изучи Mixed Conditionals, инверсию и сложные пассивные конструкции.")

    # 3. Конкретные советы по Словарю
    if vocab <= 3:
        rec_parts.append("СЛОВАРЬ: Твоя задача — выучить топ-500 самых частотных слов английского языка (список Oxford 3000). Учи их сразу в контексте простых фраз.")
    elif 4 <= vocab <= 6:
        rec_parts.append("СЛОВАРЬ: Расширяй запас до 1500-2000 слов. Учи тематические блоки: 'Путешествия', 'Работа', 'Хобби'. Начни использовать синонимы вместо слова 'good'.")
    elif 7 <= vocab <= 8:
        rec_parts.append("СЛОВАРЬ: Цель — 3000-4000 слов. Учи фразовые глаголы (get up, look for) и устойчивые выражения (collocations). Читай статьи на Medium.")
    elif vocab >= 9:
        rec_parts.append("СЛОВАРЬ: Твой запас богат. Работай над нюансами: различай оттенки значений синонимов, учи академическую лексику (AWL) и профессиональный сленг IT-сферы.")

    # 4. Конкретные советы по Аудированию
    if listen <= 3:
        rec_parts.append("АУДИРОВАНИЕ: Слушай адаптированные подкасты для новичков (например, 'English Class 101' или 'BBC Learning English'). Включай английские субтитры к простым мультфильмам.")
    elif 4 <= listen <= 6:
        rec_parts.append("АУДИРОВАНИЕ: Переходи на сериалы уровня 'Friends' или 'Extra English'. Сначала смотри с английскими субтитрами, потом пробуй без них по 5 минут.")
    elif 7 <= listen <= 8:
        rec_parts.append("АУДИРОВАНИЕ: Смотри YouTube-блогеров на английском (технологии, игры, лайфстайл) без субтитров. Попробуй подкасты для носителей языка.")
    elif listen >= 9:
        rec_parts.append("АУДИРОВАНИЕ: Ты понимаешь почти всё. Для тренировки слушай стендап-комики и новости BBC/CNN в быстром темпе.")

    # 5. Сборка финального текста
    rec = "\n\n".join(rec_parts)

    active_rules = [r for r in rules if r['weight'] > 0.01]

    return {
        'score': round(score, 2),
        'level': level,
        'recommendation': rec,
        'color': color,
        'rules': active_rules
    }