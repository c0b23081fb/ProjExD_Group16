import pygame
import sys
import random
import math
import time

# 初期設定
pygame.init()
screen_width, screen_height = 960, 360
cell_size = 40
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man Like Maze Game")

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)  # ビームの色
GREEN = (0, 255, 0)  # 回復表示用の色

# キャラクター設定
pacman_size = cell_size/2
ghost_size = cell_size - 4
normal_speed = 5
boosted_speed = 8
dot_size = 5
pacman_speed = normal_speed
ghost_speed = 2

# スピードブースト設定
speed_boost_amount = normal_speed * 1.5  # スピードアップの倍率
speed_boost_cost = 5  # スピードブースト使用時のスコア消費量

# 体力設定
max_health = 100
current_health = max_health
healing_amount = 20

# 敵停止スキルのタイマー設定
ghost_freeze_duration = 2000  # 停無敵止時間 (ミリ秒単位)
ghost_freeze_timer = 0  # タイマーの初期値

# 無敵状態の初期化
invincibility_active = False
invincibility_start_time = 0
invincibility_duration = 5  # 無敵状態の継続時間（秒）

# 迷路の定義 (1が壁, 0が道)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# プレイヤーの初期位置
pacman_x, pacman_y = 1 * cell_size, 1 * cell_size

# 壁とドットのリスト作成
walls = []
dots = []
for row_index, row in enumerate(maze):
    for col_index, cell in enumerate(row):
        if cell == 1:
            walls.append(pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size))
        elif cell == 0:
            dots.append(pygame.Rect(col_index * cell_size + cell_size // 2 - dot_size // 2, row_index * cell_size + cell_size // 2 - dot_size // 2, dot_size, dot_size))

# ゴーストの位置をランダムに初期化
ghosts = [{"x": 5 * cell_size, "y": 5 * cell_size} for _ in range(3)]
score = 0

# 壁貫通スキル
class WallHack:
    def __init__(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

wallhack = WallHack()

# ビームリスト
beams = []
beam_speed = 10

# 無敵状態のアクティベート関数
def activate_invincibility():
    global invincibility_active, invincibility_start_time
    invincibility_active = True
    invincibility_start_time = time.time()

# 無敵状態のチェック関数
def check_invincibility():
    global invincibility_active
    if invincibility_active and (time.time() - invincibility_start_time >= invincibility_duration):
        invincibility_active = False

# 進行方向の初期設定（x方向, y方向）
pacman_direction = (0, 0)

# プレイヤーの移動
def move_pacman(keys):
    global pacman_x, pacman_y, pacman_speed, pacman_direction, score

    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        pacman_speed = boosted_speed
    else:
        pacman_speed = normal_speed

    new_x, new_y = pacman_x, pacman_y
    if keys[pygame.K_LEFT]:
        new_x -= pacman_speed
        pacman_direction = (-1, 0)  # 左方向
    if keys[pygame.K_RIGHT]:
        new_x += pacman_speed
        pacman_direction = (1, 0)   # 右方向
    if keys[pygame.K_UP]:
        new_y -= pacman_speed
        pacman_direction = (0, -1)  # 上方向
    if keys[pygame.K_DOWN]:
        new_y += pacman_speed
        pacman_direction = (0, 1)   # 下方向

    pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
    if wallhack.enabled or not any(pacman_rect.colliderect(wall) for wall in walls):
        pacman_x, pacman_y = new_x, new_y

    # ドットとの衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for dot in dots[:]:
        if pacman_rect.colliderect(dot):
            dots.remove(dot)
            score += 10

# ビームの発射
def fire_beam():
    beam = {
        "x": pacman_x + pacman_size // 2,
        "y": pacman_y + pacman_size // 2,
        "direction": pacman_direction
    }
    beams.append(beam)

# ビームの移動
def move_beams():
    for beam in beams:
        dx, dy = beam["direction"]
        beam["x"] += dx * beam_speed
        beam["y"] += dy * beam_speed
    # 画面外に出たビームを削除
    beams[:] = [beam for beam in beams if 0 <= beam["x"] < screen_width and 0 <= beam["y"] < screen_height]

# ビームとゴーストの衝突判定
def check_beam_collisions():
    global ghosts
    for beam in beams:
        beam_rect = pygame.Rect(beam["x"], beam["y"], 10, 10)
        for ghost in ghosts[:]:
            ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
            if beam_rect.colliderect(ghost_rect):
                ghosts.remove(ghost)
                beams.remove(beam)
                break

# ゴーストの移動
def move_ghosts():
    for ghost in ghosts:
        if ghost_freeze_timer > pygame.time.get_ticks():
            continue
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        ghost["x"] += direction[0] * ghost_speed
        ghost["y"] += direction[1] * ghost_speed
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if any(ghost_rect.colliderect(wall) for wall in walls):
            ghost["x"] -= direction[0] * ghost_speed
            ghost["y"] -= direction[1] * ghost_speed

# 回復スキル
def heal():
    global current_health
    current_health = min(current_health + healing_amount, max_health)

# ゴースト停止スキル
def freeze_ghosts():
    global ghost_freeze_timer
    ghost_freeze_timer = pygame.time.get_ticks() + ghost_freeze_duration

# メインループ
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # 'f'キーで回復
                heal()
            if event.key == pygame.K_g:  # 'g'キーでゴースト停止
                freeze_ghosts()
            if event.key == pygame.K_v:  # 'v'キーで無敵発動
                activate_invincibility()
            if event.key == pygame.K_b:  # 'b'キーでビーム発射
                fire_beam()
            if event.key == pygame.K_h:  # 'h'キーで壁貫通をトグル
                wallhack.toggle()

    move_pacman(keys)
    move_beams()
    check_beam_collisions()
    move_ghosts()
    check_invincibility()

    # 画面描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
    for dot in dots:
        pygame.draw.rect(screen, WHITE, dot)
    pygame.draw.rect(screen, YELLOW, (pacman_x, pacman_y, pacman_size, pacman_size))
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, (ghost["x"], ghost["y"], ghost_size, ghost_size))
    for beam in beams:
        pygame.draw.circle(screen, PURPLE, (int(beam["x"]), int(beam["y"])), 5)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
