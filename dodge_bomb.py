import math
import os
import sys
import random
import time
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

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数:画面surface
    戻り値:なし
    """
    gameover_surf = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(gameover_surf, (0, 0, 0), (0, 0, WIDTH, HEIGHT))  # 黒い背景を描く
    gameover_surf.set_alpha(200)  # 透明度を設定

    font_surf = pg.Surface((WIDTH, HEIGHT))
    font = pg.font.Font(None, 100)  # フォントとサイズを指定
    text_surf = font.render("GAME OVER", True, (255, 255, 255))  # 白い文字で描画
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 文字を画面中央に配置
    gameover_surf.blit(text_surf, text_rect)  # ゲームオーバーの文字を描画

    gmkk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    gmkk_rect1 = gmkk_img.get_rect(center=(WIDTH // 2 - 250, HEIGHT // 2))  # こうかとんの画像を文字の左に配置
    gmkk_rect2 = gmkk_img.get_rect(center=(WIDTH // 2 + 250, HEIGHT // 2))  # こうかとんの画像を文字の右に配置
    gameover_surf.blit(gmkk_img, gmkk_rect1)  # こうかとんの画像を描画
    gameover_surf.blit(gmkk_img, gmkk_rect2)  # こうかとんの画像を描画

    screen.blit(gameover_surf, (0, 0))  # ゲームオーバー画面を表示
    pg.display.update()  # 画面を更新
    pg.time.wait(5000)  # タイマー

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
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200



    bb_imgs, bb_accs = init_bb_imgs() # 追加：リストを生成
    bb_img = bb_imgs[0]               # 追加：最初の爆弾をセット
    bb_rct = bb_img.get_rect()        # 修正：最初のRectを取得
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  # 爆弾の初期座標を設定する
    vx, vy = +5, +5 #爆弾の速度

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct): #こうかとんと爆弾が重なったら
            print("ゲームオーバー")
            gameover(screen)  #ゲームオーバー画面を表示する関数を呼び出す
            return  #ゲームオーバーとしてmain関数を終了
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
        idx = min(tmr // 500, 9)  # 500フレームごとに段階を上げる
        bb_img = bb_imgs[idx]
        acc = bb_accs[idx]
        avx, avy = vx * acc, vy * acc
        
        old_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = old_center
        

        bb_rct.move_ip(avx, avy)  # 修正：加速後の速度(avx, avy)で移動
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
