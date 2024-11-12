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
pacman_size = cell_size / 2
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
# invincibility_active = False
# invincibility_start_time = 0
# invincibility_duration = 5  # 無敵状態の継続時間（秒）
is_invincible = False
invincible_start_time = None
invincible_duration = 5

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
        # self.speed = 1000000
    
    def toggle(self):
        self.enabled = not self.enabled
wallhack = WallHack()

# ビームリスト
beams = []
beam_speed = 10

# 無敵状態のアクティベート関数
def activate_invincibility():
    global invincibility_active, invincible_start_time
    is_invincible = True
    invincible_start_time = time.time()

# 無敵状態のチェック関数
def check_invincibility():
    global is_invincible
    if is_invincible and (time.time() - invincible_start_time) >= invincible_duration:
        is_invincible = False


# 進行方向の初期設定（x方向, y方向）
pacman_direction = (0, 0)

# プレイヤーの移動
def move_pacman(keys):
    global pacman_x, pacman_y, pacman_speed, pacman_direction,score
    direction = None

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

    # Shiftキーが押されている間は加速
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        pacman_speed = boosted_speed
    else:
        pacman_speed = normal_speed
    
    if direction:
        new_x += direction[0]
        new_y += direction[1]
        pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
        if not any(pacman_rect.colliderect(wall) for wall in walls):
            pacman_x, pacman_y = new_x, new_y


    pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
    if wallhack.enabled or not any(pacman_rect.colliderect(wall) for wall in walls):
        pacman_x, pacman_y = new_x, new_y

    # ドットとの衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for dot in dots[:]:
        if pacman_rect.colliderect(dot):
            dots.remove(dot)
            score += 10


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
    if current_health < max_health:
        current_health = min(current_health + healing_amount, max_health)


        # ゴーストがランダムに上下左右に移動する例
        direction = random.choice([(0, 2), (0, -2), (2, 0), (-2, 0)])  # (dx, dy)
        ghost["x"] += direction[0] * ghost_speed
        ghost["y"] += direction[1] * ghost_speed

        # 壁に衝突しないように位置を調整
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if any(ghost_rect.colliderect(wall) for wall in walls):
            ghost["x"] -= direction[0] * ghost_speed
            ghost["y"] -= direction[1] * ghost_speed


# ランダムに敵を排除する関数
def eliminate_random_enemy():

    if ghosts:
        ghosts.pop(random.randint(0, len(ghosts) - 1))
    if ghosts:  # ゴーストがいる場合のみ
        ghost_to_remove = random.choice(ghosts)  # ランダムにゴーストを選択
        ghosts.remove(ghost_to_remove)  # ゴーストを削除

# # ヒールの処理
# def heal():
# ゲームのメインループ
# def game_loop():
    # global current_health
    # clock = pygame.time.Clock()

# ゴースト停止スキル
def freeze_ghosts():
    global ghost_freeze_timer
    ghost_freeze_timer = pygame.time.get_ticks() + ghost_freeze_duration


# ゲームの描画
def draw_game():
    screen.fill(BLACK)
    # while True:
    # screen.fill(BLACK)
    keys = pygame.key.get_pressed()
    move_pacman(keys)
    move_ghosts()
    move_beams()
    check_beam_collisions()
    check_invincibility()

    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)

        pygame.draw.rect(screen, BLUE, wall)




    # ドットの描画
    for dot in dots:
        pygame.draw.rect(screen, GREEN, dot)


    # プレイヤーの描画
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    pygame.draw.rect(screen, YELLOW, pacman_rect)

    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))

    pygame.draw.rect(screen, YELLOW, (pacman_x, pacman_y, pacman_size, pacman_size))

    # ビームの描画
    for beam in beams:
            pygame.draw.circle(screen, PURPLE, (int(beam["x"]), int(beam["y"])), 5)

    # ヒール表示
    health_text = f"Health: {current_health}/{max_health}"
    font = pygame.font.Font(None, 36)
    text_surface = font.render(health_text, True, WHITE)
    # screen.blit(text_surface, (10, 10))



    # スコアの描画
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # 体力の描画
    health_text = font.render(f"Health: {current_health}", True, WHITE)
    screen.blit(health_text, (10, 50))


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
            if not any(dot_rect.colliderect(wall) for wall in walls) and dist >= 30:
                dot.x, dot.y = new_x, new_y  # 壁に衝突しない場合のみ位置を更新
            elif dist < 30:
                dot.x, dot.y = pacman_x, pacman_y #自機との距離が非常に近い場合自機の位置に移動させる(オーバーラン対策)

# ゲームループ
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get(): 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # スペースキーでビームを発射
                fire_beam()
      
            


        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            
            score -= 100
            wallhack.toggle()
            print(wallhack.enabled)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
            score -= 10
            vacuum.toggle()
            print(vacuum.enabled)

    # キー入力の取得
    keys = pygame.key.get_pressed()

    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False
    #     elif event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_f:  # 'f'キーで回復
    #             heal()
    #         if event.key == pygame.K_g:  # 'g'キーでゴースト停止
    #             freeze_ghosts()
    #         if event.key == pygame.K_v:  # 'v'キーで無敵発動
    #             activate_invincibility()
    #         if event.key == pygame.K_b:  # 'b'キーでビーム発射
    #             fire_beam()
    #         if event.key == pygame.K_h:  # 'h'キーで壁貫通をトグル
    #             wallhack.toggle()

    # 敵のランダム消去

    if keys[pygame.K_e]:
        eliminate_random_enemy()

    if keys[pygame.K_f]:
        heal()


    # 敵を2秒停止するスキル発動
    if keys[pygame.K_s]:
        freeze_ghosts()

    if keys[pygame.K_i]:  # Iキーで無敵を発動
        activate_invincibility()

    # 毎フレームの処理
    check_invincibility()         # 無敵状態の終了確認
    move_pacman(keys)             # プレイヤーの移動
    move_ghosts()                 # ゴーストの移動

    move_beams()                  # ビームの移動
    check_beam_collisions()       # ビームとゴーストの衝突判定
    draw_game()                   # 画面の描画
    

    # 各種関数の実行
    if vacuum.enabled:
        dot_vacuum()   

    # 敵との衝突判定
    pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
    for ghost in ghosts:
        ghost_rect = pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size)
        if pacman_rect.colliderect(ghost_rect):
            print("Game Over!")
            pygame.quit()
            sys.exit()


    # ゴーストの停止タイマーを更新
    if ghost_freeze_timer > 0:
       ghost_freeze_timer -= clock.get_time()  # タイマーを減少
    else:
        move_ghosts()

    draw_game()
    pygame.display.flip()
    clock.tick(30)

# pygame.quit()
# sys.exit()
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         sys.exit()
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_SPACE:
        #             fire_beam()
        #         elif event.key == pygame.K_h:
        #             wallhack.toggle()
        #         elif event.key == pygame.K_i:
        #             activate_invincibility()

        # pygame.display.flip()
        # clock.tick(30)

# game_loop()
