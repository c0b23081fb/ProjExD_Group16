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
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)  # ビームの色

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
normal_speed = 5
boosted_speed = 8
pacman_speed = normal_speed
ghost_speed = 2

# 体力設定
max_health = 100
current_health = max_health
healing_amount = 20

# 無敵状態の設定
is_invincible = False
invincible_duration = 5  # 5秒間無敵
invincible_start_time = None

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

# 初期位置
pacman_x, pacman_y = 1 * cell_size, 1 * cell_size

# 壁のリスト作成
walls = []
for row_index, row in enumerate(maze):
    for col_index, cell in enumerate(row):
        if cell == 1:
            walls.append(pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size))

# ゴーストの位置をランダムに初期化
ghosts = [{"x": 5 * cell_size, "y": 5 * cell_size} for _ in range(3)]

class WallHack:
    def __init__(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

wallhack = WallHack()

# ビームリスト
beams = []
beam_speed = 10

# 無敵状態を開始する関数
def activate_invincibility():
    global is_invincible, invincible_start_time
    is_invincible = True
    invincible_start_time = time.time()

# 無敵状態の終了を確認する関数
def check_invincibility():
    global is_invincible
    if is_invincible and (time.time() - invincible_start_time) >= invincible_duration:
        is_invincible = False

# 進行方向の初期設定（x方向, y方向）
pacman_direction = (0, 0)

# プレイヤーの移動
def move_pacman(keys):
    global pacman_x, pacman_y, pacman_speed, pacman_direction

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

# ビームの発射（8方向）
def fire_beam():
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),    # 左、右、上、下
        (-1, -1), (1, -1), (-1, 1), (1, 1)   # 左上、右上、左下、右下
    ]
    for direction in directions:
        beam = {
            "x": pacman_x + pacman_size // 2,
            "y": pacman_y + pacman_size // 2,
            "direction": direction
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
        beam_rect = pygame.Rect(beam["x"], beam["y"], 5, 5)
        for ghost in ghosts:
            ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
            if beam_rect.colliderect(ghost_rect):
                ghosts.remove(ghost)
                beams.remove(beam)
                break

# ゴーストの移動
def move_ghosts():
    for ghost in ghosts:
        # ゴーストがランダムに上下左右に移動する例
        direction = random.choice([(0, 2), (0, -2), (2, 0), (-2, 0)])  # (dx, dy)
        ghost["x"] += direction[0] * ghost_speed
        ghost["y"] += direction[1] * ghost_speed

        # 壁に衝突しないように位置を調整
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if any(ghost_rect.colliderect(wall) for wall in walls):
            ghost["x"] -= direction[0] * ghost_speed
            ghost["y"] -= direction[1] * ghost_speed

# ゲームのメインループ
def game_loop():
    global current_health
    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)
        keys = pygame.key.get_pressed()
        move_pacman(keys)
        move_ghosts()
        move_beams()
        check_beam_collisions()
        check_invincibility()

        for wall in walls:
            pygame.draw.rect(screen, BLUE, wall)

        for ghost in ghosts:
            pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))

        pygame.draw.rect(screen, YELLOW, (pacman_x, pacman_y, pacman_size, pacman_size))

        for beam in beams:
            pygame.draw.circle(screen, PURPLE, (int(beam["x"]), int(beam["y"])), 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fire_beam()
                elif event.key == pygame.K_h:
                    wallhack.toggle()
                elif event.key == pygame.K_i:
                    activate_invincibility()

        pygame.display.flip()
        clock.tick(30)

game_loop()