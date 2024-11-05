import pygame
import sys
import random
import math

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

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
dot_size = 5
normal_speed = cell_size
pacman_speed = normal_speed
ghost_speed = 2

# スピードブースト設定
speed_boost_amount = normal_speed * 1.5  # スピードアップの倍率
speed_boost_cost = 5  # スピードブースト使用時のスコア消費量

# 体力設定
max_health = 100
current_health = max_health
healing_amount = 20  # 回復量

# 敵の数の設定
initial_ghost_count = 5  # 初期の敵の数

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

# プレイヤーの移動
def move_pacman(keys):
    global pacman_x, pacman_y, score, pacman_speed

    direction = None
    new_x, new_y = pacman_x, pacman_y

    # スピードブーストの発動 (Shiftキー)
    if keys[pygame.K_LSHIFT] and score >= speed_boost_cost:
        pacman_speed = speed_boost_amount
        score -= speed_boost_cost
    else:
        pacman_speed = normal_speed

    # 移動方向の決定
    if keys[pygame.K_LEFT]:
        direction = (-pacman_speed, 0)
    elif keys[pygame.K_RIGHT]:
        direction = (pacman_speed, 0)
    elif keys[pygame.K_UP]:
        direction = (0, -pacman_speed)
    elif keys[pygame.K_DOWN]:
        direction = (0, pacman_speed)
    
    if direction:
        new_x += direction[0]
        new_y += direction[1]
        pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
        if not any(pacman_rect.colliderect(wall) for wall in walls):
            pacman_x, pacman_y = new_x, new_y

    # ドットとの衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for dot in dots[:]:
        if pacman_rect.colliderect(dot):
            dots.remove(dot)
            score += 10

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
                ghost["x"], ghost["y"] = new_x, new_y

# 回復スキル
def heal():
    global current_health
    if current_health < max_health:
        current_health = min(current_health + healing_amount, max_health)

# 敵をランダムに消去する関数
def eliminate_random_enemy():
    if ghosts:
        ghosts.pop(random.randint(0, len(ghosts) - 1))

# 描画処理
def draw_game():
    screen.fill(BLACK)
    
    # 壁の描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
    
    # ドットの描画
    for dot in dots:
        pygame.draw.rect(screen, GREEN, dot)
    
    # プレイヤーの描画
    pygame.draw.rect(screen, YELLOW, pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size))
    
    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))
    
    # スコアの描画
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # 体力の描画
    health_text = font.render(f"Health: {current_health}", True, WHITE)
    screen.blit(health_text, (10, 50))

# ゲームループ
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            score -= 10
            wallhack.toggle()
    
    # キー入力の取得
    keys = pygame.key.get_pressed()

    # 敵のランダム消去
    if keys[pygame.K_e]:
        eliminate_random_enemy()
    
    # 回復スキル発動
    if keys[pygame.K_f]:
        heal()
    
    # 各種関数の実行
    move_pacman(keys)
    move_ghosts()
    
    # ゴーストとの衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for ghost in ghosts:
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if pacman_rect.colliderect(ghost_rect):
            print("Game Over!")
            pygame.quit()
            sys.exit()
    
    # ゲーム描画
    draw_game()
    pygame.display.flip()
    clock.tick(30)
