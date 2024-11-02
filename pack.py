import pygame
import sys
import random
import math

# 初期設定
pygame.init()
screen_width, screen_height = 600, 400
cell_size = 20
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man Like Maze Game")

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
dot_size = 5
pacman_speed = 5
ghost_speed = 2

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

# 壁のリスト作成
walls = []
for row_index, row in enumerate(maze):
    for col_index, cell in enumerate(row):
        if cell == 1:
            walls.append(pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size))

# ゴーストの位置をランダムに初期化
ghosts = [{"x": 5 * cell_size, "y": 5 * cell_size} for _ in range(3)]

# プレイヤーの移動（壁との衝突を考慮）
def move_pacman(keys):
    global pacman_x, pacman_y
    new_x, new_y = pacman_x, pacman_y
    if keys[pygame.K_LEFT]:
        new_x -= pacman_speed
    if keys[pygame.K_RIGHT]:
        new_x += pacman_speed
    if keys[pygame.K_UP]:
        new_y -= pacman_speed
    if keys[pygame.K_DOWN]:
        new_y += pacman_speed

    # 壁との衝突判定
    pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
    if not any(pacman_rect.colliderect(wall) for wall in walls):
        pacman_x, pacman_y = new_x, new_y  # 壁に衝突しない場合のみ位置を更新

# ゴーストの移動
def move_ghosts():
    for ghost in ghosts:
        dx, dy = pacman_x - ghost["x"], pacman_y - ghost["y"]
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            new_x = ghost["x"] + dx * ghost_speed
            new_y = ghost["y"] + dy * ghost_speed
            ghost_rect = pygame.Rect(new_x, new_y, ghost_size, ghost_size)
            if not any(ghost_rect.colliderect(wall) for wall in walls):
                ghost["x"], ghost["y"] = new_x, new_y  # 壁に衝突しない場合のみ位置を更新

# 描画処理
def draw_game():
    screen.fill(BLACK)
    
    # 壁の描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
    
    # プレイヤーの描画
    pygame.draw.rect(screen, YELLOW, pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size))
    
    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))

# ゲームループ
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # キー入力の取得
    keys = pygame.key.get_pressed()
    
    # 各関数の実行
    move_pacman(keys)
    move_ghosts()
    draw_game()
    
    pygame.display.flip()
    clock.tick(30)
