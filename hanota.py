from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config_handle import config


class Hanota:
    def __call__(self, amount_in_A: int) -> list[str]:
        # A 柱放几个
        self.amount_in_A = amount_in_A
        # 左边是底部，右边是顶部
        self.A = ['A']
        self.B = ['B']
        self.C = ['C']
        self.count = 0
        # 在 A 柱添加盘子
        for i in range(self.amount_in_A, 0, -1):
            self.A.append(i)
        
        # 开始解决问题
        self.res = [f"{self.A}, {self.B}, {self.C}\n"]
        self.solve(self.A, self.B, self.C)
        self.res.append(f"\n移动次数：{self.count}")
        return self.res

    def solve(self, A: list[int], B: list[int], C: list[int]):
        """求解汉诺塔问题"""
        n = len(A) - 1
        # 将 A 顶部 n 个圆盘借助 B 移到 C
        self.dfs(n, A, B, C)

    def dfs(self, i: int, src: list[int], buf: list[int], tar: list[int]):
        """求解汉诺塔问题 f(i)"""
        if i == 1:
            self.move(src, tar)
            return
        # 子问题 f(i-1) ：将 src 顶部 i-1 个圆盘借助 tar 移到 buf
        self.dfs(i - 1, src, tar, buf)
        # 子问题 f(1) ：将 src 剩余一个圆盘移到 tar
        self.move(src, tar)
        # 子问题 f(i-1) ：将 buf 顶部 i-1 个圆盘借助 src 移到 tar
        self.dfs(i - 1, buf, src, tar)

    def move(self, src: list[int], tar: list[int]):
        """移动一个圆盘（汉诺塔的操作只有一种，从某个柱子取最上面的，放到另一个柱子上）"""
        # 从 src 顶部拿出一个圆盘
        pan = src.pop()
        # 将圆盘放入 tar 顶部
        tar.append(pan)

        # 下面都不是必须的，方便观察过程添加的
        self.count += 1
        self.res.append(f"pan {pan}, from {src[0]} to {tar[0]} -> {self.A}, {self.B}, {self.C}")


router = APIRouter(prefix="/hanota")

templates = Jinja2Templates(directory='templates')

@router.get('/{amount}/', response_class=HTMLResponse)
async def hanota(request: Request, amount: int = 3):
    if amount > config.max_hanota:
        return templates.TemplateResponse(request=request, name="hanota.html", context={"error_msg": "盘的数量太多"})
    hanota = Hanota()
    res = hanota(amount)
    return templates.TemplateResponse(request=request, name="hanota.html", context={"hanota_result": "\n".join(res)})
