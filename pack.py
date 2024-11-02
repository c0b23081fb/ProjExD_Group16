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
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# キャラクター設定
pacman_size = 20
ghost_size = 20
dot_size = 5
pacman_speed = 5
ghost_speed = 2

# 壁の設定
walls = [
    pygame.Rect(100, 100, 400, 10),
    pygame.Rect(100, 200, 400, 10),
    pygame.Rect(100, 300, 400, 10),
    pygame.Rect(100, 100, 10, 200),
    pygame.Rect(490, 100, 10, 200),
]

# ゲームデータの初期化
def init_game():
    global pacman_x, pacman_y, ghosts, dots, score

    # プレイヤーが壁と重ならない位置に生成されるまでループ
    while True:
        pacman_x, pacman_y = random.randint(0, screen_width - pacman_size), random.randint(0, screen_height - pacman_size)
        pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
        
        # 壁と重なっていないか確認
        if not any(pacman_rect.colliderect(wall) for wall in walls):
            break  # 壁と重ならない位置が見つかったらループを抜ける

    # ゴーストとドットの初期位置
    ghosts = [{"x": random.randint(50, screen_width - 50), "y": random.randint(50, screen_height - 50)} for _ in range(3)]
    dots = [pygame.Rect(random.randint(50, screen_width - 50), random.randint(50, screen_height - 50), dot_size, dot_size) for _ in range(20)]
    score = 0


# プレイヤーの移動
def move_pacman(keys):
    global pacman_x, pacman_y
    if keys[pygame.K_LEFT]:
        pacman_x -= pacman_speed
    if keys[pygame.K_RIGHT]:
        pacman_x += pacman_speed
    if keys[pygame.K_UP]:
        pacman_y -= pacman_speed
    if keys[pygame.K_DOWN]:
        pacman_y += pacman_speed

    # 壁との衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for wall in walls:
        if pacman_rect.colliderect(wall):
            # 衝突時の移動修正
            if keys[pygame.K_LEFT]:
                pacman_x += pacman_speed
            if keys[pygame.K_RIGHT]:
                pacman_x -= pacman_speed
            if keys[pygame.K_UP]:
                pacman_y += pacman_speed
            if keys[pygame.K_DOWN]:
                pacman_y -= pacman_speed

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
    
    # 壁の描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)

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
