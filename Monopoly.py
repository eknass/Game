from ursina import *
from random import randint

app = Ursina()

# --- Названия 40 клеток ---
cell_names = [
    "Старт", "Средиземноморский пр.", "Общественная казна", "Балтийский пр.", "Налог",
    "ЖД станция 1", "Ориентал ав.", "Шанс", "Вермонт ав.", "Коннектикут ав.",
    "Тюрьма", "Сент-Чарльз пл.", "Электростанция", "Стен пл.", "Вирджиния ав.",
    "ЖД станция 2", "Сент-Джеймс пл.", "Общественная казна", "Теннесси ав.", "Нью-Йорк ав.",
    "Бесплатная парковка", "Кентукки ав.", "Шанс", "Индиана ав.", "Иллинойс ав.",
    "ЖД станция 3", "Атлантик ав.", "Вентнор ав.", "Водоканал", "Марвин гарденс",
    "Иди в тюрьму", "Пацифик ав.", "Северная Каролина ав.", "Общ. казна", "Пенсильвания ав.",
    "ЖД станция 4"
]

cells = []
cell_count = len(cell_names)  # 36
side_cells = cell_count // 4  # 9
size = 20                    # длина стороны поля

# --- Генерация клеток по периметру ---
for i in range(cell_count):
    if i < side_cells:  # нижняя сторона (слева -> направо)
        x = -size/2 + i * (size/(side_cells-1))
        z = size/2
    elif i < side_cells*2:  # правая сторона (снизу -> вверх)
        x = (size/2)+2.5
        z = size/2 - (i - side_cells) * (size/(side_cells-1))
    elif i < side_cells*3:  # верхняя сторона (справа -> налево)
        x = size/2 - (i - side_cells*2) * (size/(side_cells-1))+2.5
        z = (-size/2)-2.5
    else:  # левая сторона (сверху -> вниз)
        x = -size/2
        z = -size/2 + (i - side_cells*3) * (size/(side_cells-1))-2.5

    # Клетка
    box = Entity(
        model='cube',
        position=(x, 0, z),
        scale=(2.4, 0.1, 2.4),
        color=color.azure if i % 2 == 0 else color.white
    )
    box.name = cell_names[i]
    cells.append(box)

    # Подпись внутри клетки
    Text(
        text=cell_names[i],
        parent=box,
        y=0.6,
        rotation=(90, 0, 0),
        scale=10,
        color=color.black,
        origin=(0, 0)
    )

# --- Игрок ---
player = Entity(model='sphere', color=color.red, scale=0.8, position=cells[0].position + Vec3(0, 0.6, 0))

# --- Переменные игры ---
current_index = 0
target_index = 0
moving = False
steps = 0

# --- UI ---
info_text = Text(text="Нажми [SPACE], чтобы бросить кубик", position=(-0.7, 0.45), scale=1.5)

# --- Бросок кубика ---
def input(key):
    global steps, target_index, moving
    if key == 'space' and not moving:
        steps = randint(2, 12)  # два кубика
        target_index = (current_index + steps) % cell_count
        moving = True
        print(f"Выпало: {steps}, цель: {cells[target_index].name}")

# --- Логика движения ---
def update():
    global current_index, steps, moving

    if moving:
        target_pos = cells[target_index].position + Vec3(0, 0.6, 0)
        player.position = lerp(player.position, target_pos, time.dt * 3)

        if distance(player.position, target_pos) < 0.1:
            player.position = target_pos
            current_index = target_index
            moving = False
            print(f"Игрок встал на: {cells[current_index].name}")

# --- Камера сверху ---
camera.position = (0, 40, 0)
camera.rotation_x = 90
camera.orthographic = True
camera.fov = 35

app.run()