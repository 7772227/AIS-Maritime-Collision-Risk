# Control Barrier Function (CBF) Safety Filter Demo

This folder contains a Python demonstration of a **Control Barrier Function (CBF)** based safety filter, applied to a maritime collision avoidance scenario.

## 📐 Mathematical Formulation

### 1. Dynamics Model
For this initial prototype, we use a simplified **point-mass model** (single integrator). The system dynamics are:
\[
 \dot{x} = u 
\]
Where \(x \in \mathbb{R}^2\) is the vessel's position and \(u \in \mathbb{R}^2\) is the control input (velocity).

### 2. Safety Constraint (Barrier Function)
We define a danger zone (representing another vessel or a static obstacle). The safety set is defined by a continuously differentiable barrier function \(h(x)\):
\[
 h(x) = \|x - x_{\text{obstacle}}\|^2 - r^2 \ge 0 
\]
- \(h(x) > 0\): The vessel is safe.
- \(h(x) \le 0\): The vessel has breached the safety boundary (collision).

### 3. CBF-QP Safety Filter
To guarantee safety, the control input \(u\) must satisfy the CBF condition:
\[
 \dot{h}(x) + \alpha h(x) \ge 0 
\]
Where \(\alpha > 0\) is the **safety decay rate**. The filter solves a Quadratic Program (QP) at every time step to find the minimal modification to the nominal control \(u_{\text{nom}}\) (the direct path to the target):
\[
 \min_{u} \|u - u_{\text{nom}}\|^2 
\]
\[
 \text{s.t.} \quad \nabla h(x)^T u + \alpha h(x) \ge 0 
\]

## ⚙️ Parameter Tuning
- **`alpha` (Safety Decay Rate)**: A larger \(\alpha\) forces the vessel to react earlier and stay further from the danger zone. A smaller \(\alpha\) allows the vessel to travel closer to the boundary.
- **`obstacle_r` (Obstacle Radius)**: Defines the physical size of the danger zone.

## 🚧 Limitations & Future Work
1. **Single Integrator vs. Double Integrator**: Real vessels have massive inertia and cannot change direction instantly. The next step is to upgrade the dynamics to a **double integrator** (\(\dot{x} = v, \dot{v} = u\)) and potentially use **High-Order CBF (HOCBF)**.
2. **COLREGs Integration**: The current obstacle is static. In real maritime scenarios, moving vessels must follow the **International Regulations for Preventing Collisions at Sea (COLREGs)**. We plan to encode these rules as additional constraints in the QP formulation.
