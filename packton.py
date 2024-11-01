import pygame
import sys
import pygame as pg
from math import atan2, degrees
import os
import random


# 初期化
pygame.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# 画面サイズ、色、FPS設定
WIDTH, HEIGHT = 1000,640
TILE_SIZE = 40  # タイルの1マスのサイズ
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255,0,0)
# speed = 10

# 画面生成
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("パクトン")

# ステージマップ (1が壁、0が通路)
stage = [
    [1] * 25,
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1] * 25,
]

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：パクトンのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def find_random_position():
    """黒い道から初期位置を取得する関数"""
    while True:
        row = random.randint(0,len(stage) - 1)
        col = random.randint(0,len(stage[0]) - 1)
        if stage[row][col] == 0:
            return col * TILE_SIZE, row * TILE_SIZE
        
def is_valid_move(rect):
    """指定された位置が青い壁や迷路の外でないことを確認する"""
    if rect.left < 0 or rect.right > WIDTH or rect.top < 0 or rect.bottom > HEIGHT:
        return False  # 画面外にはみ出した場合
    col, row = rect.centerx // TILE_SIZE, rect.centery // TILE_SIZE
    return stage[row][col] == 0  # 青い壁（1）の上にはいけない

class Packton(pg.sprite.Sprite):
    """
    ゲームキャラクターに関するクラス
    """
    # speed = TILE_SIZE
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        パクトン画像Surfaceを生成する
        引数1 num：パクトン画像ファイル名の番号
        引数2 xy：パクトン画像の位置座標タプル
        """
        super().__init__()
        # img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        # img = pg.transform.flip(img0, True, False)  # デフォルトのパクトン
        self.images = {
            "default": pg.transform.rotozoom(pg.image.load(f"fig/0.png"), 0, 1.0),
            "moving": pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 1.0),
            "defeat": pg.transform.rotozoom(pg.image.load(f"fig/6.png"), 0, 1.0),
            "dead": pg.transform.rotozoom(pg.image.load(f"fig/8.png"), 0, 1.0),
        }
        self.image = self.images["default"]
        # self.dire = (+1, 0)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.move_mode = False
        self.memo = 0
        self.lock = False
        self.alive = True

    

    def update(self, key_lst: list[bool],tmr):
        """
        押下キーに応じてパクトンを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        if self.move_mode and not self.lock and self.alive:
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    next_rect = self.rect.move(mv[0] * TILE_SIZE, mv[1] * TILE_SIZE)
                    if is_valid_move(next_rect):
                        self.rect = next_rect
                        self.image = self.images["moving"]
                        # self.dire = mv
                        self.move_mode = False
                        self.lock =True
                        self.memo = tmr
                        print("move")
                        print(self.memo,tmr)
                    else:
                        self.image = self.images["default"]
        if self.lock and tmr - self.memo >= 3:
            print("unlock")
            self.lock = False
            self.image = self.images["defalt"]

        screen.blit(self.image, self.rect)
    def change_state(self,state: str):
        """
        キャラクターに応じて画像を切り替える
        引数state: 'defalt'、'dead'などの状態
        """
        if state in self.images:
            self.image = self.images[state]
            if state == "dead":
                self.alive = False  # 死亡状態に設定
    
class Enemy(pg.sprite.Sprite):
    """敵のクラス"""
    delta = [(+1,0),(0,+1),(-1,0),(0,-1)]

    def __init__(self,num: int, xy: tuple[int,int]):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f'fig/{num}.png'),0,1.0)
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
        self.dire = random.choice(__class__.delta)

    def update(self):
        """敵を移動させる"""
        next_rect = self.rect.move(self.dire[0] * TILE_SIZE,self.dire[1] * TILE_SIZE)
        if not is_valid_move(next_rect):
            self.rect = random.choice(__class__.delta)
        # self.rect.move(self.dire[0] * TILE_SIZE,self.dire[1] * TILE_SIZE)

    # def is_valid_move(self,rect):
    #     """指定された位置が青い壁でないことを確認する"""
    #     if rect.left < 0 or rect.right > WIDTH or rect.top < 0 or rect.bottom > HEIGHT:
    #         return False
    #     col,row = rect.centerx // TILE_SIZE,rect.centery // TILE_SIZE
    #     return stage[row][col] == 0

# メインループ
def main():
    clock = pygame.time.Clock()
    all_sprites = pg.sprite.Group()
    pack = Packton(2,(160,200))
    all_sprites.add(pack)
    enemy = Enemy(6,find_random_position())
    all_sprites.add(enemy)
    tmr = 0
    while True:
        tmr += 1
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key in Packton.delta and not pack.move_mode and not pack.lock:
                    if pack.move_mode == False and pack.lock == False:
                        pack.memo = tmr
                        pack.move_mode=True
                        print("start")
            if event.type == pg.QUIT:
                pygame.quit()
                sys.exit()
        key_lst = pg.key.get_pressed()

        # 画面の描画
        screen.fill(BLACK)
        for row in range(len(stage)):
            for col in range(len(stage[row])):
                color = BLUE if stage[row][col] == 1 else BLACK
                pg.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


        pack.update(key_lst,tmr)
        enemy.update()

        if pg.sprite.collide_rect(pack,enemy):  # パクトンと敵が摂食したらGameOver
            print("Game Over!")
            pg.quit()
            sys.exit()
    

        # 画面更新
        all_sprites.draw(screen)
        pg.display.update()
        clock.tick(FPS)
if __name__ == "__main__":
    main()