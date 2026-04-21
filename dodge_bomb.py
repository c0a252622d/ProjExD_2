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
    """
    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する
    """
    bb = pg.Surface((WIDTH, HEIGHT))
    bb.fill((0, 0, 0))
    bb.set_alpha(300)
    fnt = pg.font.SysFont("notosanscjkjp", 80)
    txt = fnt.render("Game Over", True, (255, 255, 255))
    txt_x = WIDTH // 2 - txt.get_width() // 2
    txt_y = HEIGHT // 2 - txt.get_height() // 2
    bb.blit(txt, [txt_x, txt_y])
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.centery = HEIGHT // 2
    kk_rct.right = txt_x - 5
    bb.blit(kk_img, kk_rct)
    kk_rct2 = kk_img.get_rect()
    kk_rct2.centery = HEIGHT // 2
    kk_rct2.left = txt_x + txt.get_width() + 5
    bb.blit(kk_img, kk_rct2)
    screen.blit(bb, [0, 0])
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


def calc_orientation(
    org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]
) -> tuple[float, float]:
    """
    爆弾(org)からこうかとん(dst)に向かう正規化済み方向ベクトルを返す。
    距離が300未満の場合は慣性としてcurrent_xyをそのまま返す。
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    dist = math.sqrt(dx ** 2 + dy ** 2)
    if dist < 300:
        return current_xy
    scale = math.sqrt(50) / dist
    return dx * scale, dy * scale


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の爆弾SurfaceリストとaccelerationリストのタプルをVを返す
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
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10)
    vx, vy = 5.0, 5.0
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        kk_img = kk_imgs[tuple(sum_mv)]
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
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
