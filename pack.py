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

GREEN = (0,255,0)
GREEN = (0, 255, 0)  # 回復表示用の色

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
normal_speed = 5
boosted_speed = 8

dot_size = 5
normal_speed = cell_size
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
        pacman_x, pacman_y = new_x, new_y

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

        # 壁に衝突しないように位置を調整する
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        for wall in walls:
            if ghost_rect.colliderect(wall):
                ghost["x"] -= direction[0] * ghost_speed  # 移動を元に戻す
                ghost["y"] -= direction[1] * ghost_speed  # 移動を元に戻す
                break

# ランダムに敵を排除する関数
def eliminate_random_enemy():
    if ghosts:  # ゴーストがいる場合のみ
        ghost_to_remove = random.choice(ghosts)  # ランダムにゴーストを選択
        ghosts.remove(ghost_to_remove)  # ゴーストを削除

# ヒールの処理
def heal():
    global current_health
    current_health = min(current_health + healing_amount, max_health)

# ドットの再生成関数
def respawn_dots():
    global last_dot_spawa_time
    current_time = pygame.time.get_ticks()
    if current_time - last_dot_spawa_time > DOT_RESPAWN_TIME:
        last_dot_spawa_time = current_time
        for row_index, row in enumerate(maze):
            for col_index, cell in enumerate(row):
                if cell == 0:
                    dot_rect = pygame.Rect(col_index * cell_size + cell_size // 2 - dot_size // 2, row_index * cell_size + cell_size // 2 - dot_size // 2, dot_size, dot_size)
                    if dot_rect not in dots:
                        dots.append(dot_rect)

# ゲームの描画
def draw_game():
    screen.fill(BLACK)

    # 迷路の描画
    for wall in walls:
        pygame.draw.rect(screen, WHITE, wall)


        pygame.draw.rect(screen, BLUE, wall)
    
    # ドットの描画
    for dot in dots:
        pygame.draw.rect(screen,GREEN,dot)
    # プレイヤーの描画
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    pygame.draw.rect(screen, YELLOW, pacman_rect)

    # ゴーストの描画
    for ghost in ghosts:
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        pygame.draw.rect(screen, RED, ghost_rect)

    # ビームの描画
    for beam in beams:
        beam_rect = pygame.Rect(beam["x"], beam["y"], 5, 5)
        pygame.draw.rect(screen, PURPLE, beam_rect)

    # ヒール表示
    health_text = f"Health: {current_health}/{max_health}"
    font = pygame.font.Font(None, 36)
    text_surface = font.render(health_text, True, WHITE)
    screen.blit(text_surface, (10, 10))

    # 無敵状態の表示
    if is_invincible:
        invincible_text = "Invincible!"
        invincible_surface = font.render(invincible_text, True, GREEN)
        screen.blit(invincible_surface, (10, 40))

        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))
    
    # スコアの描画
    font = pygame.font.Font(None,36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10,10))
    # HPバーの描画
    pygame.draw.rect(screen, RED, (10, 10, max_health, 10))  # 最大体力
    pygame.draw.rect(screen, GREEN, (10, 10, current_health, 10))  # 現在の体力

# ゲームループ
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                wallhack.toggle()
            if event.key == pygame.K_SPACE:  # スペースキーでビームを発射
                fire_beam()


        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            score -= 100
            wallhack.toggle()
    
    # キー入力の取得
    keys = pygame.key.get_pressed()

    if keys[pygame.K_e]:
        eliminate_random_enemy()

    if keys[pygame.K_f]:
        heal()

    if keys[pygame.K_i]:  # Iキーで無敵を発動
        activate_invincibility()

    # 毎フレームの処理
    check_invincibility()         # 無敵状態の終了確認
    move_pacman(keys)             # プレイヤーの移動
    move_ghosts()                 # ゴーストの移動
    move_beams()                  # ビームの移動
    check_beam_collisions()       # ビームとゴーストの衝突判定
    draw_game()                   # 画面の描画
    
    pygame.display.flip()         # 画面更新

    clock.tick(30)                # フレームレートを設定

    # 各関数の実行
    move_pacman(keys)
    move_ghosts()
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
