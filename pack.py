import pygame
import sys
import random
import math

# 初期設定
pygame.init()
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man Like Game")

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# キャラクター設定
pacman_size = 20
ghost_size = 20
dot_size = 5
pacman_speed = 5
ghost_speed = 2

# ゲームデータの初期化
def init_game():
    global pacman_x, pacman_y, ghosts, dots, score
    pacman_x, pacman_y = screen_width // 2, screen_height // 2  # プレイヤーの初期位置を中央に設定
    ghosts = [{"x": random.randint(50, screen_width - 50), "y": random.randint(50, screen_height - 50)} for _ in range(3)]
    dots = [pygame.Rect(random.randint(50, screen_width - 50), random.randint(50, screen_height - 50), dot_size, dot_size) for _ in range(20)]
    score = 0

# プレイヤーの移動（画面外に出ないように制限）
def move_pacman(keys):
    global pacman_x, pacman_y
    if keys[pygame.K_LEFT]:
        pacman_x = max(0, pacman_x - pacman_speed)  # 左端に到達したらそれ以上左に行かない
    if keys[pygame.K_RIGHT]:
        pacman_x = min(screen_width - pacman_size, pacman_x + pacman_speed)  # 右端に到達したらそれ以上右に行かない
    if keys[pygame.K_UP]:
        pacman_y = max(0, pacman_y - pacman_speed)  # 上端に到達したらそれ以上上に行かない
    if keys[pygame.K_DOWN]:
        pacman_y = min(screen_height - pacman_size, pacman_y + pacman_speed)  # 下端に到達したらそれ以上下に行かない

# ゴーストの追尾移動
def move_ghosts():
    for ghost in ghosts:
        dx, dy = pacman_x - ghost["x"], pacman_y - ghost["y"]
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            ghost["x"] += dx * ghost_speed
            ghost["y"] += dy * ghost_speed

# 衝突判定
def check_collisions():
    global running, score
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    
    # ゴーストとの衝突
    for ghost in ghosts:
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if pacman_rect.colliderect(ghost_rect):
            print("Game Over!")
            running = False
    
    # ドットとの衝突
    for dot in dots[:]:
        if pacman_rect.colliderect(dot):
            dots.remove(dot)
            score += 10  # ドットを取るごとに10点加算

# 描画処理
def draw_game():
    screen.fill(BLACK)
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    
    # プレイヤーの描画
    pygame.draw.rect(screen, YELLOW, pacman_rect)
    
    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))

    # ドットの描画
    for dot in dots:
        pygame.draw.rect(screen, WHITE, dot)
    
    # スコア表示
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# ゲームループ
clock = pygame.time.Clock()
running = True
init_game()
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
    check_collisions()
    draw_game()
    
    pygame.display.flip()
    clock.tick(30)
