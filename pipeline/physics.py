"""かんたん物理エンジン（@ko-ji「Experiment with PhysicsEngine」型の検証用、2026-11-27）
手描きで動きを決めるのではなく、運動方程式を小さな時間刻みで計算して「本当にそう動く」映像にするための部品。
2D の球（質点）だけを扱う：重力・空気抵抗（速さの2乗）・地面での跳ね返りと摩擦・球どうしの衝突。

使い方の例（同じ条件で角度だけ変えて同時に投げる）：
    from physics import World, Ball
    w = World(g=9.8, rho=1.2)
    for deg in (15, 30, 45, 60, 75):
        w.add(Ball.launch(x=0, y=0, speed=30, deg=deg, r=0.11, m=0.43, cd=0.25, tag=f'{deg}度'))
    frames = w.run(T=8.0, fps=30)          # frames[i] = [(x, y, vx, vy), ...]（各球の状態）
    w.landing()                             # 各球が最初に地面に着いた (時刻, x)
画面に描くときは、frames の x, y をピクセルに変換するだけ（軌跡は過去のコマを線でつなぐ）。
※ 単純化した計算です。動画の画面と説明欄に「物理の式で計算した目安」と書くこと。
"""
import math


class Ball:
    def __init__(self, x, y, vx, vy, r=0.1, m=1.0, cd=0.47, e=0.5, mu=0.3, tag=''):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.r, self.m, self.cd, self.e, self.mu, self.tag = r, m, cd, e, mu, tag
        self.land = None   # 最初に地面に着いた (時刻, x)

    @classmethod
    def launch(cls, x, y, speed, deg, **kw):
        a = math.radians(deg)
        return cls(x, y, speed * math.cos(a), speed * math.sin(a), **kw)

    @property
    def area(self):
        return math.pi * self.r * self.r


class World:
    def __init__(self, g=9.8, rho=1.2, ground=0.0, dt=1 / 600, collide=False):
        """collide=True で球どうしがぶつかる（条件比べのように重ねて同時に投げるときは False のまま）"""
        self.g, self.rho, self.ground, self.dt, self.collide = g, rho, ground, dt, collide
        self.balls, self.t = [], 0.0

    def add(self, b):
        self.balls.append(b)
        return b

    def _acc(self, b):
        v = math.hypot(b.vx, b.vy)
        k = 0.5 * self.rho * b.cd * b.area / b.m if self.rho > 0 else 0.0   # 空気抵抗 F = 1/2 ρ Cd A v²
        return -k * v * b.vx, -self.g - k * v * b.vy

    def step(self):
        dt = self.dt
        for b in self.balls:   # 半陰的オイラー法（小さい dt なら十分安定）
            ax, ay = self._acc(b)
            b.vx += ax * dt
            b.vy += ay * dt
            b.x += b.vx * dt
            b.y += b.vy * dt
            if b.y - b.r < self.ground and b.vy < 0:
                if b.land is None:
                    b.land = (self.t, b.x)
                b.y = self.ground + b.r
                b.vy = -b.vy * b.e
                b.vx *= (1 - b.mu)
                if abs(b.vy) < 0.05:
                    b.vy = 0.0
        n = len(self.balls) if self.collide else 0   # 球どうしの衝突（運動量保存＋はね返り係数）
        for i in range(n):
            for j in range(i + 1, n):
                p, q = self.balls[i], self.balls[j]
                dx, dy = q.x - p.x, q.y - p.y
                d = math.hypot(dx, dy)
                if 0 < d < p.r + q.r:
                    nx, ny = dx / d, dy / d
                    rv = (q.vx - p.vx) * nx + (q.vy - p.vy) * ny
                    if rv < 0:
                        e = min(p.e, q.e)
                        jimp = -(1 + e) * rv / (1 / p.m + 1 / q.m)
                        p.vx -= jimp * nx / p.m; p.vy -= jimp * ny / p.m
                        q.vx += jimp * nx / q.m; q.vy += jimp * ny / q.m
                    ov = (p.r + q.r - d) / 2
                    p.x -= nx * ov; p.y -= ny * ov; q.x += nx * ov; q.y += ny * ov
        self.t += dt

    def run(self, T, fps=30):
        """T 秒ぶん計算して、動画の1コマごとの状態を返す"""
        frames, per = [], max(1, round(1 / (fps * self.dt)))
        for i in range(int(T * fps)):
            frames.append([(b.x, b.y, b.vx, b.vy) for b in self.balls])
            for _ in range(per):
                self.step()
        return frames

    def landing(self):
        return {b.tag or i: b.land for i, b in enumerate(self.balls)}


if __name__ == '__main__':
    # 確認：空気抵抗なしなら 45度がいちばん遠い（理論値 v²/g）。ありだと最適角は45度より小さくなる
    for rho in (0.0, 1.2):
        w = World(rho=rho)
        for deg in (30, 40, 45, 50, 60):
            w.add(Ball.launch(0, 0.11, 30, deg, r=0.11, m=0.43, cd=0.25, tag=deg))
        w.run(8)
        print('空気' + ('あり' if rho else 'なし'), {k: round(v[1], 1) for k, v in w.landing().items() if v}, '理論(なし)', round(30 ** 2 / 9.8, 1))
