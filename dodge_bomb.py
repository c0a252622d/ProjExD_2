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
    引数：こうかとんRect または 爆弾Rect
    戻り値：(横方向判定結果, 縦方向判定結果) ※True：画面内
    """
    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    演習1：背景をかなり濃い黒にしてゲームオーバーを表示する
    """
    bb = pg.Surface((WIDTH, HEIGHT))
    bb.fill((0, 0, 0))
    bb.set_alpha(220)  # さらに濃く設定
    
    fnt = pg.font.SysFont(None, 80)
    txt = fnt.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct1 = kk_img.get_rect(center=(WIDTH // 2 - 250, HEIGHT // 2))
    kk_rct2 = kk_img.get_rect(center=(WIDTH // 2 + 250, HEIGHT // 2))
    
    screen.blit(bb, [0, 0])
    screen.blit(txt, txt_rect)
    screen.blit(kk_img, kk_rct1)
    screen.blit(kk_img, kk_rct2)
    pg.display.update()
    time.sleep(5)


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    演習3：指示書の表に基づき、反転・回転を正しく適用した辞書を返す
    """
    # 元のこうかとんは「左」向き
    kk_base = pg.image.load("fig/3.png")
    kk_left = pg.transform.rotozoom(kk_base, 0, 0.9)    # 左向き基準
    kk_right = pg.transform.flip(kk_left, True, False)  # 右向き基準（反転）

    return {
        (0, 0):   kk_right,                                # 停止（右向き）
        (5, 0):   kk_right,                                # 右
        (5, -5):  pg.transform.rotozoom(kk_right, 45, 1.0),  # 右上
        (0, -5):  pg.transform.rotozoom(kk_right, 90, 1.0),  # 上
        (-5, -5): pg.transform.rotozoom(kk_left, -45, 1.0),  # 左上
        (-5, 0):  kk_left,                                 # 左
        (-5, 5):  pg.transform.rotozoom(kk_left, 45, 1.0),   # 左下
        (0, 5):   pg.transform.rotozoom(kk_right, -90, 1.0), # 下
        (5, 5):   pg.transform.rotozoom(kk_right, -45, 1.0), # 右下
    }


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    演習4：追従アルゴリズム
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery
    dist = math.sqrt(dx**2 + dy**2)
    if dist < 300:
        return current_xy
    scale = math.sqrt(50) / dist
    return dx * scale, dy * scale


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    演習2：爆弾のリスト作成
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
    kk_rct = kk_img.get_rect(center=(300, 200))
    
    bb_imgs, bb_accs = init_bb_imgs()
    vx, vy = 5.0, 5.0
    bb_rct = bb_imgs[0].get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    
    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        # 1. 背景描画
        screen.blit(bg_img, [0, 0])

        # 2. こうかとんの移動と向き
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        if any(sum_mv): # 移動している間だけ向きを更新
            kk_img = kk_imgs[tuple(sum_mv)]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        # 3. 爆弾の更新
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        
        # 中心位置を維持してRectを更新
        old_center = bb_rct.center
        bb_rct = bb_img.get_rect(center=old_center)
        
        # 移動
        bb_rct.move_ip(vx * bb_accs[idx], vy * bb_accs[idx])
        yoko, tate = check_bound(bb_rct)
        if not yoko: vx *= -1
        if not tate: vy *= -1
            
        # 4. 衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # 5. 描画
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