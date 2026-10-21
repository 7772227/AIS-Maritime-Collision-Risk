import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import minimize

# 1. 定义环境参数
target = np.array([10.0, 10.0])   # 目标位置
obstacle = np.array([5.0, 5.0])   # 障碍物中心
obstacle_r = 2.0                  # 障碍物半径 (安全红线)
alpha = 2.0                       # CBF 的安全衰减系数

# 2. 定义 CBF 屏障函数 h(x) 和它的导数
# h(x) > 0 表示安全，h(x) < 0 表示碰撞。h(x) = 距离^2 - 半径^2
def h(x):
    return np.linalg.norm(x - obstacle)**2 - obstacle_r**2

def grad_h(x):
    return 2 * (x - obstacle)

# 3. 核心：CBF 二次规划 (QP) 安全滤波器
# 目标：找到控制输入 u，使得它尽量接近名义控制 (去往目标)，同时满足安全约束
def cbf_qp(x):
    # 名义控制：直接指向目标
    u_nom = target - x
    
    # 如果已经安全，就不需要修改
    if h(x) >= 0.1:
        return u_nom
        
    # 构造 QP 约束： h_dot + alpha * h >= 0
    # 因为 x_dot = u，所以 h_dot = grad_h * u
    # 即 grad_h * u + alpha * h >= 0
    A = -grad_h(x)  # scipy 的 minimize 默认求最小值，所以不等式约束写成 A*u <= b
    b = alpha * h(x)
    
    # 求解最小化 ||u - u_nom||^2，约束为 A*u <= b
    res = minimize(
        lambda u: np.linalg.norm(u - u_nom)**2,
        x0=u_nom,
        constraints={'type': 'ineq', 'fun': lambda u: b - np.dot(A, u)},
        bounds=[(-5, 5), (-5, 5)]
    )
    return res.x

# 4. 动画设置
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, 12); ax.set_ylim(0, 12)
ax.set_title("Control Barrier Function (CBF) Safety Filter")

# 画障碍物
circle = plt.Circle(obstacle, obstacle_r, color='red', alpha=0.3, label='Danger Zone (h(x) < 0)')
ax.add_patch(circle)
ax.plot(target[0], target[1], 'g*', markersize=15, label='Target')
line, = ax.plot([], [], 'b-', label='Trajectory')
point, = ax.plot([], [], 'bo')
ax.legend(loc='upper left')

# 初始状态（在障碍物左下方）
x = np.array([1.0, 1.0])
history = [x.copy()]

def update(frame):
    global x
    for _ in range(3): # 每次动画多算几步，速度快一点
        u = cbf_qp(x)
        x = x + 0.1 * u # 积分更新位置
        history.append(x.copy())
        
    line.set_data([p[0] for p in history], [p[1] for p in history])
    point.set_data([x[0]], [x[1]])
    return line, point

ani = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=True)
plt.show()