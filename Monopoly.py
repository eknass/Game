from typing_extensions import Text
from ursina import *
from random import randint
from math import sin, cos, radians

app = Ursina()

mouse_sensitivity = Vec2(40, 40)
speed = 5
zoom_speed = 50


# --- Названия 36 клеток ---
cell_names = [
    "Старт", "Прочитать книгу с названием из одного слова", "Мой список", "Прочитать книгу моего года рождения", "Школьная программа",
    "Прочитать детектив", "Прочитать книгу из топа", "Прочитать книгу в названии которой есть число", "Бросай еще раз", "Прочитать книгу с вопросом в названии",
    "Помощь зала", "Прочитать книгу, основанную на реальных событиях", "Мой список", "Выбрать по обложке", "Прочитать книгу которую экранизировали",
    "Прочитать книгу с именем главного героя в названии", "Бросай еще раз", "Прочитать книгу, которую посоветовал друг", "Мой список", "Школьная программа",
    "Прочитать книгу любимого автора", "Мой список", "Прочитать книгу вышедшую в этом году", "Прочитать книгу в которой более 500 страниц", "Бросай еще раз",
    "Помощь зала", "Прочитать классический роман", "Прочитать автобиографию", "Мой список", "Прочитать книгу в названии которой есть цвет",
    "Выбрать по обложке", "Прочитать книгу в которой менее 200 страниц"
]

cells = []
cell_count = len(cell_names)  # 36
side_cells = cell_count // 4  # 9
size = 40                    # длина стороны поля


# --- Генерация клеток по периметру ---
for i in range(cell_count):
    if i < side_cells:  # нижняя сторона (слева -> направо)
        x = -size/2 + i * (size/(side_cells-1))
        z = size/2
    elif i < side_cells*2:  # правая сторона (снизу -> вверх)
        x = (size/2)+5.6
        z = size/2 - (i - side_cells) * (size/(side_cells-1))
    elif i < side_cells*3:  # верхняя сторона (справа -> налево)
        x = size/2 - (i - side_cells*2) * (size/(side_cells-1))+5.6
        z = (-size/2)-5.6
    else:  # левая сторона (сверху -> вниз)
        x = -size/2
        z = -size/2 + (i - side_cells*3) * (size/(side_cells-1))-5.6

    # Клетка
    box = Entity(
        model='cube',
        position=(x, 0, z),
        scale=(5, 0.5, 5),
        color=color.azure if i % 2 == 0 else color.white
    )
    box.name = cell_names[i]
    cells.append(box)
    # Функция переноса текста внутри клеток
    def wrap_text(text, max_chars=30):
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                lines.append(current)
                current = word
            else:
                current += (' ' if current else '') + word
        if current:
            lines.append(current)
        return '\n'.join(lines)

    # Подпись внутри клетки
    Text(
        text=wrap_text(cell_names[i],max_chars=10),
        parent=box,
        y=2,
        rotation=(95, 0, 0),
        scale=5,
        color=color.black,
        origin=(0, 0)
    )

# Текст с координатами камеры
camera_text = Text(
    text='',
    origin=( -0.5, 0.5),   # выравнивание относительно угла
    scale=1,
    x=-0.85,               # положение по X (левый край)
    y=0.5,                # положение по Y (верхний край)
    color=color.yellow)

# --- Игрок ---
player = Entity(model='sphere', color=color.red, scale=0.8, position=cells[0].position + Vec3(0, 0.6, 0))

#Background
background = Entity(
    model = 'quad',
    texture = 'textures/background.png',
    scale = (43,43),
    x = 3,
    z = -3,

    rotation_x = 90
)

# --- Переменные игры ---
current_index = 0
target_index = 0
moving = False
steps = 0

# --- UI ---
info_text = Text(text="Нажми [SPACE], чтобы бросить кубик", position=(-0.7, 0.45), scale=1.5)

#Окно при остановке на клетке
popup = WindowPanel(title='Всплывающее окно', content=[Text('                           ', position =(0,0))], enabled=False)

# --- Бросок кубика ---
def input(key):
    global steps, target_index, moving
    if key == 'space' and not moving:
        steps = randint(2, 12)  # два кубика
        target_index = (current_index + steps) % cell_count
        moving = True
        print(f"Выпало: {steps}, цель: {cells[target_index].name}")
    if key == 'scroll up':
            # приближение
        forward = camera.forward
        camera.position += forward * time.dt * zoom_speed * 10
    if key == 'scroll down':
            # отдаление
        forward = camera.forward
        camera.position -= forward * time.dt * zoom_speed * 10 
    if key == 'left mouse down':
        mouse.locked = True
        mouse.visible = False   
    if key == 'left mouse up':
        mouse.locked = False
        mouse.visible = True
    if key == 'escape':
        popup.enabled = False

# --- Логика движения ---
def update():
    global current_index, steps, moving
    coord = camera.position
    camera_text.text = f'Camera position: {coord.x:.2f},{coord.y:.2f},{coord.z:.2f}'
    # Движение камеры при зажатой кнопке мыши
    if held_keys['left mouse']:
        camera.rotation_y += mouse.velocity[0] * mouse_sensitivity.x
        camera.rotation_x -= mouse.velocity[1] * mouse_sensitivity.y
        camera.rotation_x = clamp(camera.rotation_x, 0, 100)
    if moving:        
        target_pos = cells[target_index].position + Vec3(0, 0.6, 0)
        player.position = lerp(player.position, target_pos, time.dt * 3)
        camera.position = (player.position.x, 50, player.position.z)
        camera.rotation = (90,0,0)
        if distance(player.position, target_pos) < 0.1:
            player.position = target_pos
            current_index = target_index
            moving = False
            print(f"Игрок встал на: {cells[current_index].name}")
            popup.content[0].text = cells[current_index].name
            popup.enabled = True
            
    # Движение камеры на WASD
    speed = 15 * time.dt        
    direction = Vec3(
        cos(radians(camera.rotation_y)) * (held_keys['d'] - held_keys['a']) +
        sin(radians(camera.rotation_y)) * (held_keys['s'] - held_keys['w']),
        0,
        -sin(radians(camera.rotation_y)) * (held_keys['a'] - held_keys['d']) + -(
        cos(radians(camera.rotation_y)) * (held_keys['s'] - held_keys['w']))
    ).normalized()
    camera.position += direction * time.dt * speed
    camera.position += camera.up * direction.z * speed
    camera.position += camera.right * direction.x * speed
    camera.x = clamp(camera.x,-50,50)
    camera.y = clamp(camera.y,1,500)
    camera.z = clamp(camera.z,-30,30)

# --- Камера сверху ---
camera.position = (0,220,0)

""" camera.position = (player.position.x, 50, player.position.z) """
camera.rotation_x = 90
""" camera.orthographic = False """
""" camera.fov = 20 """

app.run()