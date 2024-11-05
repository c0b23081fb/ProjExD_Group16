import pygame
import sys
import random
import math

# 初期設定
pygame.init()
screen_width, screen_height = 960,360
cell_size = 40
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man Like Maze Game")

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0,255,0)
GREEN = (0, 255, 0)  # 回復表示用の色

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
dot_size = 5
normal_speed = cell_size
pacman_speed = normal_speed
ghost_speed = 2


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

# 壁のリスト作成
walls = []
dots = []
for row_index, row in enumerate(maze):
    for col_index, cell in enumerate(row):
        if cell == 1:
            walls.append(pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size))
        elif cell == 0:
            dots.append(pygame.Rect(col_index* cell_size + cell_size // 2 - dot_size // 2, row_index * cell_size + cell_size // 2 - dot_size // 2, dot_size, dot_size))

# ゴーストの位置をランダムに初期化
ghosts = [{"x": 5 * cell_size, "y": 5 * cell_size} for _ in range(3)]


score = 0

# タイマー設定
DOT_RESPAWN_TIME = 5000
last_dot_spawa_time = pygame.time.get_ticks()
class WallHack:
    def __init__(self):
        self.enabled = False
    
    def toggle(self):
        self.enabled = not self.enabled
wallhack = WallHack()
# プレイヤーの移動（壁との衝突を考慮）
def move_pacman(keys):
    global pacman_x, pacman_y,score

    direction = None
    new_x, new_y = pacman_x, pacman_y  # 初期値を設定
    cell_size = 10
    
    if keys[pygame.K_LEFT]:
        direction = (-cell_size, 0)
    elif keys[pygame.K_RIGHT]:
        direction = (cell_size, 0)
    elif keys[pygame.K_UP]:
        direction = (0, -cell_size)
    elif keys[pygame.K_DOWN]:
        direction = (0, cell_size)
    
    if direction:
        new_x += direction[0]
        new_y += direction[1]
        pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
        if not any(pacman_rect.colliderect(wall) for wall in walls):
            pacman_x, pacman_y = new_x, new_y


    # ドットとの衝突判定
    pacman_rect = pygame.Rect(pacman_x,pacman_y,pacman_size,pacman_size)
    for dot in dots[:]:
        if pacman_rect.colliderect(dot):
            dots.remove(dot)
            score += 10
    # 壁との衝突判定
    pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
    if wallhack.enabled or not any(pacman_rect.colliderect(wall) for wall in walls):
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


# 回復スキル
def heal():
    global current_health
    if current_health < max_health:
        current_health = min(current_health + healing_amount, max_health)  # 最大HPを超えないようにする

# 敵をランダムに消去する関数
def eliminate_random_enemy():
    if ghosts:
        ghosts.pop(random.randint(0, len(ghosts) - 1))

# ドットの再生成関数
def respawn_dots():
    global last_dot_spawa_time
    current_time = pygame.time.get_ticks()
    if current_time - last_dot_spawa_time > DOT_RESPAWN_TIME:
        last_dot_spawa_time = current_time
        dots.clear()#全てのエサを削除
        for row_index, row in enumerate(maze):
            for col_index, cell in enumerate(row):
                if cell == 0:
                    dot_rect = pygame.Rect(col_index * cell_size + cell_size // 2 - dot_size // 2, row_index * cell_size + cell_size // 2 - dot_size // 2, dot_size, dot_size)
                    #if dot_rect not in dots:
                    dots.append(dot_rect)

# 描画処理
def draw_game():
    screen.fill(BLACK)
    
    # 壁の描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
    
    # ドットの描画
    for dot in dots:
        pygame.draw.rect(screen,GREEN,dot)
    # プレイヤーの描画
    pygame.draw.rect(screen, YELLOW, pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size))
    
    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))
    
    # スコアの描画
    font = pygame.font.Font(None,36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10,10))
    # HPバーの描画
    pygame.draw.rect(screen, RED, (10, 10, max_health, 10))  # 最大体力
    pygame.draw.rect(screen, GREEN, (10, 10, current_health, 10))  # 現在の体力

#分岐機能　吸引
class Vacuum():
    def __init__(self):
        self.enabled = False
        self.speed = 1000000
    
    def toggle(self):
        self.enabled = not self.enabled
vacuum = Vacuum()

#ドットを吸い込む関数
def dot_vacuum():
   for dot in dots:
        dx, dy = pacman_x - dot.x, pacman_y - dot.y #dx,dyを自機との距離に設定
        dist = math.hypot(dx, dy) #自機との距離を計算
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            new_x = dot.x + dx * vacuum.speed/(dist**3)
            new_y = dot.y + dy * vacuum.speed/(dist**3)#自機に近いものほど強力な引力が働くように
            dot_rect = pygame.Rect(new_x, new_y, dot_size, dot_size)
            if not any(dot_rect.colliderect(wall) for wall in walls) and dist >= 20:
                dot.x, dot.y = new_x, new_y  # 壁に衝突しない場合のみ位置を更新
            elif dist < 20:
                dot.x, dot.y = pacman_x, pacman_y #自機との距離が非常に近い場合自機の位置に移動させる(オーバーラン対策)

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
            score -= 10
            vacuum.toggle()

    # キー入力の取得
    keys = pygame.key.get_pressed()

    # ランダムに敵を消去
    if keys[pygame.K_e]:
        eliminate_random_enemy()
    
    # 回復スキル発動
    if keys[pygame.K_f]:
        heal()
    
    # 各関数の実行
    move_pacman(keys)
    move_ghosts()
    if vacuum.enabled:
        dot_vacuum()
    respawn_dots()
   

    # 敵との衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for ghost in ghosts:
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if pacman_rect.colliderect(ghost_rect):
            print("Game Over!")
            pygame.quit()
            sys.exit()
    
    draw_game()
    pygame.display.flip()
    clock.tick(30)
