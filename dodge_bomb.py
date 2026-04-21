import os
import sys
import random
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), #上
    pg.K_DOWN: (0, +5), #下
    pg.K_LEFT: (-5, 0), #左 
    pg.K_RIGHT: (+5, 0), #右
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数:こうかとんrctまたは爆弾rct
    戻り値:横方向、縦方向のはみ出し判定結果（Ture:はみ出ていない、False:はみ出している）
    """
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko, tate 


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20))  #半径10の赤い円を書く
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  #爆弾円を描く
    bb_img.set_colorkey((0, 0, 0)) #黒を透過させる
    bb_rct = bb_img.get_rect() #爆弾RECTを取得する
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  # 爆弾の初期座標を設定する
    vx, vy = +5, +5 #爆弾の速度

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

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy) #爆弾を移動させる
        yoko, tate = check_bound(bb_rct) 
        if not yoko: #横方向の判定
            vx *= -1 
        if not tate: #縦方向の判定
            vy *= -1 
        screen.blit(bb_img, bb_rct) #爆弾を画面に書く
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
