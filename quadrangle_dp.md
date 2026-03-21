```metadata
title: 决策单调性
date: 2026-03-16 11:00
category: 动态规划
difficulty: hard
```

考虑以下动态规划模型：

$f_i = \max_{j < i} w(j, i)$

其中 $w(i,j)$ 通常可以写作 $f(j) + cost(j, i)$ 的形式

这种动态规划常见于区间合并或区间拆分动态规划

记 $opt(i)$ 为 i 的决策点， 即 $f_i = w(opt(i)， i)$

如果说 $\forall x < y, opt(x) < opt(y)$

则称该动态规划的决策具有单调性。

## 决策单调性的解决

如果你们做过许多利用单调性降低时间复杂度的问题，你可能会觉得这个**决策单调性性质**具有很强的性质，它和我们之前一类更简单的**单调性**问题直觉上很像，都可以使用**尺取法**或者**二分法**解决，但实际上很不一样。

我们来回顾一个经典的尺取法问题：

### [P1147 连续自然数和](https://www.luogu.com.cn/problem/P1147)

**题目题意**
给定一个自然数 M，找出所有**至少两个数**的连续自然数段，使得段内数字之和等于 M。按每段第一个数升序输出这些段的起止数字。

**做法：双指针/尺取法**
维护两个指针 $L$ 和 $R$ 指向当前区间两端，并记录区间和 sum。

在外层的for循环中将 $L$ 向右移动

- 若 **sum < M**：R 右移，扩大区间
- 若 **sum == M**：记录解

**单调性体现**：两个指针均**单向移动**不回溯，利用区间和随指针移动的单调变化，高效找到所有解。

**做法：二分法**

枚举 $L$ ，二分 $R$ ，通过前缀和快速计算 $sum$。

### 决策单调性的不同

我们假设**决策单调性**也可以这样解决，很快我们就会遇到一些问题：

1) $i$ 往右移动时， $j$ 往右移动， 但在 $j$ 到达 $opt(i)$ 前可能遇到一些局部优解 $opt'(i)$ 即满足 $w( opt'(i) + 1, i) < w(opt'(i), i) <  w(opt(i), i) $不同决策点的答案不具有单调性（也就是说在$opt'(i)+1$这个决策点，有单调性情况下其取值应该更优，但结果变劣了）。
2) $w(j, i)$ 可能和 $f(j)$ 有关，如果使用二分法，在计算 $opt(mid)$ 时，$l$ 到 $mid$ 的 $f$ 值无法提前计算不能提前计算，导致一些二分方法无效。

### 解决问题（1）的分治方法

分析问题后，我们发现决策单调性可能不会提供任何别的额外的单调性质，所以我们直接对opt进行**整体二分**。

P.S. 如果之前不会**整体二分**,可以多花点时间搞懂这一部分，不太影响理解。

假如说现在需要确认 $[l,r]$ 区间的 $opt$ 值， 并且确认 $opt$ 取值这能在 $[opt_{min}, opt_{max}]$ 的范围。通过函数 $calc(l, r, opt_{min}, opt_{max})$ 递归求解这个问题，可以分为以下几步解决。

1) 暴力解决 $opt(mid)$
2) 递归解决 $calc(l, mid - 1, opt_{min}, opt(mid))$ 和 $calc(mid+1, r, opt(mid), opt_{max})$

~~时间复杂度为什么是对的？~~

可以考虑每个问题的难度为$(x,opt_{min})$到$(y,opt_{max})$的面积，每次解决分治问题会让面积减半，可以证明时间复杂度不会超过 $O(n log n)$

```c++

val_t w(int j, int i);  // 成本函数
val_t f[N];             // 最优值
int opt[N];             // 最小最优决策

// 递归求解 [l,r] 中的问题
// 已知它们的最小最优决策点一定出现在区间 [opt_min, opt_max] 中
void calc(int l, int r, int opt_min, int opt_max) {
  int mid = (l + r) / 2;
  // 求问题 mid 的最优决策点
  for (int j = opt_min; j <= std::min(opt_max, mid); ++j) {
    if (w(j, mid) < f[mid]) {
      f[mid] = w(j, mid);
      opt[mid] = j;
    }
  }
  // 根据决策单调性得出左右两部分的决策区间，递归处理
  if (l < mid) calc(l, mid - 1, opt_min, opt[mid]);
  if (r > mid) calc(mid + 1, r, opt[mid], opt_max);
}

// 求解整个区间 [1,n] 的问题
void solve(int n) {
  // 每次调用递归函数前，都需要清空数组 f
  std::fill(f + 1, f + n + 1, inf);
  // 最开始时，只知道问题 [1,n] 的所有决策点都一定在 [1,n] 中
  calc(1, n, 1, n);
}
```

### 简化 LARSCH 算法

上述算法有一个缺陷： 在求问题 mid 的最优决策点时，我们直接计算了 $w(mid, i)$， 但此时 $f(i)$ 的取值是未知的。

也就是说，如果 $w(mid, i)$ 与 $f(i)$ 有关（实际应用种大部分时候都是有关的），那么上述算法直接无法求解，我们需要对其进行改良。

改良的过程就是说考虑我们解决问题是不需要第一时间就算出 $mid$ 值真实的 $opt(mid)$ 值，我们可以考虑计算其在决策点 $[1,l)$ 范围内的最优秀决策点 $opt_l(mid)$, 在考虑利用 $opt_l(mid)$ 解决 $[l, mid)$ 范围内的问题，最后再更新计算出真正的$opt(mid)$，再接着解决右半部分 $(mid, r]$ 的问题。

首先我们知道 $opt_1(n) = 0$ ， 因为小于1的决策点只有决策点0。

对于之前的问题，我们定义求解 $[l,r]$ 范围的f值为 $calc(l, r)$ 问题，那么递归解决问题的方法如下

1) 计算 $opt_l(mid)$ ，其范围只需要在 $[opt(l-1),opt_l(r)]$ 枚举即可。（因为二分中我们总是先解决中间点的弱化问题，接着是左半边子问题，最后是中间点的完全问题和右半边子问题，此时可以保证 $opt_l(r)$ 以及范围$[1,l)$ 的 $opt$ 和 $f$ 取值已知。）
2) 递归解决左半边子问题 $calc(l, mid) $ (注意不要包含mid)
3) 此时已经计算出 $[l,mid)$ 的 $f$ 值，用其计算出 $opt_{mid}(r)$。
4) 递归解决右半边子问题 $calc(mid, r)$

在实际代码视线中 $opt_l$ 和 $opt$ 使用同一个变量存储，请读者注意区分。

```c++
val_t w(int j, int i);  // 成本函数
val_t f[N];             // 最优值
int opt[N];             // 最小最优决策

// 用决策 j 更新问题 i
void check(int j, int i) {
  if (w(j, i) < f[i]) {
    f[i] = w(j, i);
    opt[i] = j;
  }
}

// 递归求解区间 [l, r] 内的问题
void calc(int l, int r) {
  int mid = (l + r) / 2; 
  //这边注意mid要上取整数，不然会导致大小为2的区间重复计算


  for (int j = opt[l - 1]; j <= opt[r]; ++j) check(j, mid);
  //此时计算opt_l(mid)，注意opt[r]此时表示的是opt_l(r)

  if (l < mid) calc(l, mid);
  //这边mid == l 不需要计算，因为 mid == l 时，上一句话计算出的opt(l)已经是最优解了
  
  //计算opt_mid(r)
  for (int j = l; j <= mid; ++j) check(j, r);
  
  if (mid < r) calc(mid + 1, r);
}

// 求解整个区间 [1, n] 内的问题
void solve(int n) {
  // 清空 f 数组
  std::fill(f + 1, f + n + 1, inf);
  // 初始化
  check(0, 1);
  check(0, n);
  // 递归求解区间 [1, n] 内的问题
  calc(1, n);
}
```

## 决策单调性的条件

和wqs二分一样，决策单调性如果只知道做法很难解决问题。所以我们需要知道如何证明一个东西具有决策单调性。

### 四边形不等式

判断某个函数 $w(l,r)$ 是否满足四边形不等式的方法．最为直接的方法就是计算它的二阶混合差分：

$$
\begin{aligned}
\Delta_l \Delta_r w(l,r) &= \Delta_l(w(l,r+1)-w(l,r)) \\
&= w(l+1,r+1)-w(l+1,r)-w(l,r+1)+w(l,r).
\end{aligned}
$$

函数 $w(l,r)$ 满足四边形不等式，当且仅当$f_i$为$w(i,j)$的最大值（最小值），$\Delta_l \Delta_r w(l,r)$ 非正（或非负）。

### 四边形不等式快速判断方法（重要）

**直观上，满足四边形不等式的函数通常意味着，区间向两侧扩大——即左端点向左移动和右端点向右移动——具有某种抑制效应（协同效应），即同时发生会比单个发生收益更小（更大）。**

利用这个公式我们假设 $w(j, i) = f(j) + cost(j, i)$ 或者 $w(j, i) = f(j， k - 1) + cost(j, i)$

前者是不限制次数的区间拆分，后者限制次数恰好为 $k$ 次

如果 $cost(j, i)$ 满足四边形不等式， $w(j, i)$ 也满足四边形不等式。

证明非常简单，对$w(j, i)$ 进行两次$\Delta$算子运算，发现$f$项正好全部相消。

### 四边形不等式到决策单调性

满足四边形不等式即符合决策单调性。

证明:

假如 $x < y$

由于 $opt(x)$ 是最优决策点， 有 $ \forall t < opt(x)， f(t, x) < f(opt(x), x) $

记 $\Delta(\alpha) = f(opt(x), \alpha) - f(t, \alpha) $, 有 $\Delta(x) > 0$

由于二阶混合差分恒大于0，可知$\Delta$函数单调递增：

$ \Delta(y) > \Delta(x) > 0 $

即可知 $ \forall t < x, f(opt(x), y) > f(t, y)$

也就是说 $opt(y) \ge opt(x)$

## 面向二维情况：[石子合并](https://www.luogu.com.cn/problem/P1880)

环形问题考虑将所有数复制一份放到后面，破环为链，下面仅考虑链上问题。

首先先考虑给出dp方程：

$$f_{i,j} = \min_{i<k<j} pre_i - pre_{j-1} + f_{i,k} + f_{k+1,j}$$

记录 $f_{i,j}$ 的决策点为 $opt_{i,j}$

### 四边形不等式证明

我们考虑在转移时我们可以枚举 $i$ 值，则

$$f'_j = f'_k + w_{k,j}$$

其中 $w_{k,j} = pre_i - pre_{j-1} + f_{k+1,j}$

下面需要证明 $ pre_i - pre_{j-1} + f_{k+1,j} $ 符合四边形不等式

$$
\begin{aligned}
w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} = f_{k+1,j} + f_{k,j+1} - f_{k, j} - f_{k+1,j+1}
\end{aligned}
$$

我们发现这个形式可以利用数学归纳法证明，

当 $k = n - 2$ 时，$j$ 的 取值仅能为 $ n - 1 $

$$
\begin{aligned}
w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} &= f_{k+1,j} + f_{k,j+1} - f_{k, j} - f_{k+1,j+1} \\
&= f_{n-1,n-1} + f_{n-2,n} - f_{n-2, n-1} - f_{n-1, n} \\
&= 0 + 2 \cdot (a_{n-2} + a_{n-1} + a_{n}) - \min(a_{n-2} , a_{n}) - (a_{n-2} + a_{n-1}) - (a_{n-1} + a_{n}) \\
&= a_{n-2} + a_{n} - \min(a_{n-2} , a_{n}) \\
&>0
\end{aligned}
$$

则证明 $ k \ge n - 2 $ 时四边形不等式成立。

假设对于 $ k \ge m $ 都成立，

根据
$$
\begin{aligned}
w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} = f_{k+1,j} + f_{k,j+1} - f_{k, j} - f_{k+1,j+1}
\end{aligned}
$$

然后进一步可以推广到 $ k = m - 1 $ 时四边形不等式成立。

通过数学归纳法，即可证明对于所有 $ k \in [1,n] $ 都成立 $w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} > 0$。

**也就是求最小值的时候可以利用四边形不等式，而求最大值时可以用贪心。**

### 二维情况的写法

二维情况写法更加简单：

因为四边形不等式同时对两个维度成立（上文只证明对第二个维度成立，第一个维度证明同理），利用两个不同维度$opt$的单调性，可以知道：

$opt_{i,j-1} \le opt_{i,j} \le opt_{i+1,j}$

这样在枚举时先倒叙枚举$i$维度，在顺序枚举$j$维度即可计算出一个 $opt_{i,j}$ 的范围，这个范围大小均摊是 $O(1)$ 的。

### 核心代码示意

```c++
void check(int i,int k,int j){
  if (f[i][k] + f[k+1][j] + pre[j] - pre[i-1] < f[i][j]){
    opt[i][j] = k;
    f[i][j] = f[i][k] + f[k+1][j] + pre[j] - pre[i-1];
  }
} 

for(int i=(n<<1)-1;i;i--)
    for(int j=i+1;j<=(n<<1);j++){
        opt[i][j]=-1;f[i][j]=inf;      
        for(int k=opt[i][j-1];k<=opt[i+1][j];k++)
            check(i,k,j);
    }
```

### 贪心部分

这边顺便证明一下贪心部分：

我们考虑在转移时我们可以枚举 $i$ 值，则

$$f'_j = \max_{k < j} f'_k + w_{k,j}$$

其中 $w_{k,j} = pre_i - pre_{j-1} + f_{k+1,j}$

下面同样观察 $ pre_i - pre_{j-1} + f_{k+1,j} $ 性质

$$
\begin{aligned}
w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} = f_{k+1,j} + f_{k,j+1} - f_{k, j} - f_{k+1,j+1}
\end{aligned}
$$

我们发现这个形式和四边形不等式完全一样，只不过是求得是最大值，如果而求最大值会发现最后结果总是大于0,与求最大值时要求的小于0相反，所以不能使用四边形不等式。

考虑令 $W_{k,j} = f'_j + w_{k,j}$

$$
\begin{aligned}
W_{k,j} + W_{k-1, j+1} - W_{k-1,j} - W_{k,j+1} = w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1}
\end{aligned}
$$

这个形式和四边形不等式一样，所以我们可以尝试证明一个与四边形不等式相反的东西。

下面尝试证明 $ k = j - 1$ 或 $ k = i$

当 $k = n - 2$ 时，$j$ 的 取值仅能为 $ n - 1 $

$$
\begin{aligned}
w_{k,j} + w_{k-1, j+1} - w_{k-1,j} - w_{k,j+1} &= f_{k+1,j} + f_{k,j+1} - f_{k, j} - f_{k+1,j+1} \\
&= f_{n-1,n-1} + f_{n-2,n} - f_{n-2, n-1} - f_{n-1, n} \\
&= 0 + 2 \cdot (a_{n-2} + a_{n-1} + a_{n}) - \max(a_{n-2} , a_{n}) - (a_{n-2} + a_{n-1}) - (a_{n-1} + a_{n}) \\
&= a_{n-2} + a_{n} - \max(a_{n-2} , a_{n}) \\
&>0
\end{aligned}
$$

这就证明出一个和四边形不等式符号相反的东西，下面证明其最优取值只能为端点处。

证明:

记 $\Delta(\alpha) = 2 \cdot f(x, \alpha) - f(x - 1, \alpha) - f(x + 1, \alpha)  $, 下面要利用之前的不等关系证明 $\Delta(x) < 0$

先证明只含3个点时符合，然后利用归纳法证明 $\forall x > y, \Delta(x) < \Delta(y) < 0$

证明出 $\Delta(x) < 0$ 后可以证明最大值在端点处取得。

## 练习题

[一个有代码的blog](https://www.luogu.com.cn/article/vqf42hah)

|题号|
|-|
|[problem:CodeForces321E](https://codeforces.com/contest/321/problem/E)|
|[problem:洛谷P1880](https://www.luogu.com.cn/problem/P1880)|
|[problem:洛谷P4767](https://www.luogu.com.cn/problem/P4767)|
|[problem:洛谷P6918](https://www.luogu.com.cn/problem/P6918)|
