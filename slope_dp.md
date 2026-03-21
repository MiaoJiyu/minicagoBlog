```metadata
title: 斜率优化dp
date: 2026-03-16 11:00
category: 动态规划
difficulty: medium+
```

斜率优化dp问题是优化dp的**转移复杂度**的一个工具，其实现的功能是快速计算出动态规划转移的**决策点**

## 基础模型

形如

$$f_i = \max_{j \in D(i)} cost_1(i) + cost_2(j) + cost_3(i) \cdot cost_4(j)$$

其中 $D(i)$ 表示可以转移到 i 状态的状态，通常取值为 $[1, i - 1] $ 。 
$cost_1$ $cost_2$ $cost_3$ $cost_4$ 是不同的函数，取值只与参数有关。

例题：

[problem:洛谷-P3195](https://www.luogu.com.cn/problem/P3195)

有 $n$ 个玩具，第 $i$ 个玩具价值为 $c_i$．要求将这 $n$ 个玩具排成一排，分成若干段．对于一段 $[l,r]$，它的代价为 $(r-l+\sum_{i=l}^r c_i-L)^2$．其中 $L$ 是一个常量，求分段的最小代价．

$1\le n\le 5\times 10^4, 1\le L, c_i\le 10^7$．

根据大家对动态规划的学习，不难做到以下一步。

设计考虑将前$i$个玩具完成分段的最小代价为$f_i$，最后一个分段的区间为$[j+1, i]$

$$
f_i = \min_{j < i} \{ f_j + (i - (j + 1) + pre_i - pre_j - L)^2 \} 
= \min_{j < i} \{ f_j + (pre_i - pre_j + i - j - 1 - L)^2 \}
$$

用平方公式展开后半部分可得：

$$
f_i = \min_{j < i} \{(pre_i + i - 1 - L)^2 + f_j + (pre_j + j)^2 - 2 \cdot(pre_i + i - 1 - L)(pre_j + j) \}
$$

待入刚才的模型，其中

$$cost_1(x) = (pre_x+x-1-L)^2$$

$$cost_2(x) = f_x + (pre_x + x)^2$

$$cost_3(x) = 2 \cdot (pre_i+i-1-L)$$

$$cost_4(x) = pre_j + j$$

**以上部分涉及到模型的建立和转化为已知的模型，这是算法竞赛最基本的考点**

下面我们介绍两种处理这个模型的方法。

## 传统的斜率优化

### 数学基础

要理解传统的斜率优化，我们需要一些数学基础：

1) 不垂直于x轴的直线都可以写为：
$$y = kx + b$$
其中我们称 $k$ 为斜率，$b$ 为纵截距（下面简称**截距**）。

2) 考察斜率$k$的直线过三角形三点的截距的大小关系：
**以下内容请画图或使用几何画板（在线）理解**

这里提供一个在线几何画板的[例子](html/slope_model.html)。


考虑三角形由三个点 $A(x_1,y_1)$ $B(x_2,y_2),$ $C(x_3,y_3) (x_1<x_2<x_3)$ 组成
分别考察两类三角形 ：
下三角形($k_{AB} < k_{BC}$) 和 上三角形($k_{AB} > k_{BC}$)
下三角形 ：

|k|b|
|-|-|
|$k<k_{AB}$| $b_C>b_B>b_A$|
|$k_{AB}<k<k_{BC}$| $b_C>b_A>b_B$ |
|$k_{BC}<k$| $b_A>b_B>b_C$ |

上三角形：

|k|b|
|-|-|
|$k<k_{BC}$| $b_C>b_B>b_A$|
|$k_{BC}<k<k_{AB}$| $b_B>b_C>b_A$ |
|$k_{AB}<k$| $b_A>b_B>b_C$ |

不难发现如果要求截距$b$的最小值，那么上三角形中的$B$点永远不会出现在答案中；如果要求截距$b$的最大值，那么下三角形中的$B$点永远不会出现在答案中。

我们发现对于斜率$k$，其最大（最小）值总是在上（下）三角中斜率小于**其与其前一个点构成直线斜率**处取得，我们可以考虑只保留需要的三角类型，然后二分（或利用单调性，使用指针）找到最优的$b$的位置。

### 问题抽象与维护

考虑以下问题：

输入$n$个点的坐标，给出$m$个查询，每个查询给出一个斜率$k$，求经过这$n$点的$n$条直线中截距$b$的最大值。

思路：

我们要维护$n$个点直线截距的最小值，那么对于任意三个点，如果其构成一个下三角形，那么中间的点在任意$k$的取值下都不会事最优解，所以我们可以直接不维护。

具体做法：

先把所有点按$x$排序。

我们用栈（也可以是双端队列）维护，当即将插入一个新的点，如果最后三个点构成构成下三角形，删除那个中间点，重复此操作可以保证栈中任意三个点构成上三角形。

最后二分（或将k排序，利用单调性）找到$k$对应的最优点。

```c++
int main() {
    // 输入点
    scanf("%d", &n);
    for (int i = 1; i <= n; i++) scanf("%lf%lf", &p[i].x, &p[i].y);
    sort(p + 1, p + n + 1);
    
    // 单调队列维护上凸包
    hh = 1, tt = 0;
    for (int i = 1; i <= n; i++) {
        while (tt - hh >= 1 && cross(q[tt-1], q[tt], p[i]) <= 0) tt--;
        q[++tt] = p[i];
    }
    
    // 输入查询并按斜率排序
    scanf("%d", &m);
    for (int i = 1; i <= m; i++) {
        scanf("%lf", &query[i].k);
        query[i].id = i;
    }
    sort(query + 1, query + m + 1, [](Query a, Query b) { return a.k < b.k; });
    
    // 单调指针求解
    int ptr = hh;  // 指向当前最优点
    for (int i = 1; i <= m; i++) {
        double k = query[i].k;
        while (ptr < tt && calc(q[ptr], k) < calc(q[ptr + 1], k)) ptr++;
        ans[query[i].id] = calc(q[ptr], k);
    }
    
    // 按原顺序输出
    for (int i = 1; i <= m; i++) printf("%.6lf\n", ans[i]);
    return 0;
}
```

### 利用斜率进行动态规划优化

考虑之前的基础模型 

$$f_i = \max_{j \in D(i)} cost_1(i) + cost_2(j) + cost_3(i) \cdot cost_4(j)$$

先不考虑最大值符号，考虑对于确定的j，式子可以转为

$-cost_2(j) =  cost_3(i) \cdot cost_4(j) + cost_1(i) - f_i$

$y = kx + b$

其中 $ x = cost_4(j) , y = -cost_2(j), k = cost_3(i), b = cost_1(i) - f_i $

其中$(x,y)$ 仅与 $j$ 有关， 根据$k$使用上述算法求出 $b$ 的最小值后用 $cost_1(i)$减去该答案，即可在$O(1)$ (或$O(log n) ) $时间复杂度求出f_i的最大值。

## 李超树下的斜率优化

如果你觉得凸包太深奥了，无法理解，李超树维护斜率问题其实更加符合正常的思维方式（思维难度更低）。

并且李超树可以解决插入查询之间没有**强的单调性**的问题（之前的查询与修改依赖单调性，如果单调性不足需要用时间分治或平衡树解决更加麻烦）。

### 了解李超树

**问题抽象**：每次插入一个线段，每次查询求在给定$x_0$下，$y$值最大的线段（$x = x_0$与所有线段交点的最高点）

**关键思想**：在线段树框架下维护每个区间的最优直线。

**插入策略**：
- 递归位置为 $[lo, hi]$，需插入直线 $nw$。
- 比较 $nw$ 与当前最优线 $rt→f$ 在中点 $mid$ 的值。
- 将较优的线保留在节点，较劣的线递归到左（若在左端更优）或右（若在右端更优）子树。
- 这样保证最多 $O(\log^2 N)$ 次递归。

**查询策略**：
- 递归位置为 $[lo, hi]$，查询点 $x$ 的最小值。
- 先用节点存储的最优线 $rt→f$ 计算值。
- 根据 $x$ 的位置判断左/右子树，继续递归取最小值。
- 每次递归区间折半，复杂度 $O(\log N)$。

**时间复杂度**：插入 $O(\log^2 N)$，查询 $O(\log N)$，支持任意顺序操作。

### 李超树实现

```cpp
struct Line { ll m, b; };
struct Node { Line f; Node *l, *r; };
ll eval(const Line &f, ll x) { return f.m*x + f.b; }
void insert(Node *&rt, Line nw, ll lo, ll hi) {
    if (!rt) { rt = new Node{nw,nullptr,nullptr}; return; }
    ll mid=(lo+hi)>>1;
    if (eval(nw,mid)<eval(rt->f,mid)) swap(nw,rt->f);
    if (lo==hi) return;
    if (eval(nw,lo)<eval(rt->f,lo)) insert(rt->l,nw,lo,mid);
    else if (eval(nw,hi)<eval(rt->f,hi)) insert(rt->r,nw,mid+1,hi);
}
ll query(Node *rt,ll x,ll lo,ll hi){
    if(!rt) return INF;
    ll res=eval(rt->f,x);
    if(lo==hi) return res;
    ll mid=(lo+hi)>>1;
    if(x<=mid) return min(res,query(rt->l,x,lo,mid));
    else return min(res,query(rt->r,x,mid+1,hi));
}
```

### 李超树解决基础模型问题

$$f_i = \max_{j \in D(i)} cost_1(i) + cost_2(j) + cost_3(i) \cdot cost_4(j)$$

先不考虑最大值符号，考虑对于确定的j，式子可以转为

$$f_i - cost_1(i) = cost_2(j) \cdot cost_3(i) + cost_4(j)$$

$y = kx + b$

其中 $k = cost_2(j), cost_4(j) = b, x  = cost_3(i)$

即可解决。

**为什么变形为上述形式？** ：因为李超树维护的是线段的最值，每个$j$对应一个线段，查询时给定$x$（即$cost_3(i)$）求最优线段的值（即$cost_2(j) \cdot cost_4(j)$），再加上$cost_1(i)$得到$f_i$。

### 习题

[problem:洛谷-P3628](https://www.luogu.com.cn/problem/P3628)
[problem:洛谷-P2900](https://www.luogu.com.cn/problem/P2900)
[problem:洛谷-P4027](https://www.luogu.com.cn/problem/P4027)
