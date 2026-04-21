import math
import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    Rectが画面内にあるかどうかを判定し、横方向・縦方向の結果を返す
    引数：こうかとんRect または 爆弾Rect
    戻り値：(横方向判定結果, 縦方向判定結果) ※True：画面内
    """
    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する
    引数：画面Surface
    """
    # 画面全体を暗くする半透明のSurface
    black_out = pg.Surface((WIDTH, HEIGHT))
    black_out.fill((0, 0, 0))
    black_out.set_alpha(128)
    
    # フォントの設定と「Game Over」文字の描画
    fnt = pg.font.SysFont(None, 80)
    txt = fnt.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # 泣いているこうかとん画像
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct1 = kk_img.get_rect(center=(WIDTH // 2 - 250, HEIGHT // 2))
    kk_rct2 = kk_img.get_rect(center=(WIDTH // 2 + 250, HEIGHT // 2))
    
    # 描画
    screen.blit(black_out, [0, 0])
    screen.blit(txt, txt_rect)
    screen.blit(kk_img, kk_rct1)
    screen.blit(kk_img, kk_rct2)
    
    pg.display.update()
    time.sleep(5)


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー、rotozoomした画像Surfaceを値とした辞書を返す
    """
    kk_base = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    return {
        (0, 0):   pg.transform.rotozoom(kk_base, 0, 1.0),
        (5, 0):   pg.transform.rotozoom(kk_base, 0, 1.0),
        (5, -5):  pg.transform.rotozoom(kk_base, 45, 1.0),
        (0, -5):  pg.transform.rotozoom(kk_base, 90, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_base, 135, 1.0),
        (-5, 0):  pg.transform.rotozoom(kk_base, 180, 1.0),
        (-5, 5):  pg.transform.rotozoom(kk_base, 225, 1.0),
        (0, 5):   pg.transform.rotozoom(kk_base, 270, 1.0),
        (5, 5):   pg.transform.rotozoom(kk_base, 315, 1.0),
    }


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の爆弾Surfaceリストと加速度リストのタプルを返す
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    # こうかとんの初期設定
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    
    # 爆弾の初期設定
    bb_imgs, bb_accs = init_bb_imgs()
    vx, vy = 5, 5
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10)
    
    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        # 演習3：移動方向による画像の切り替え
        if any(sum_mv): 
            kk_img = kk_imgs[tuple(sum_mv)]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        # 演習2：爆弾の拡大・加速処理
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        
        # サイズ変更時に中心がズレないように調整
        old_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = old_center

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        screen.blit(bg_img, [0, 0])
        screen.blit(bb_img, bb_rct)
        screen.blit(kk_img, kk_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
