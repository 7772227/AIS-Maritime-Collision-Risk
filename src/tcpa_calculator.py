# Predictive DCPA/TCPA: Uses relative-motion vectors derived from SOG and COG to estimate the predicted closest point of approach.

import numpy as np

def calc_tcpa_dcpa(lat1, lon1, sog1, cog1, lat2, lon2, sog2, cog2):
    # 1. 将经纬度差转换为海里 
    lat_avg = np.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 60 * np.cos(lat_avg) # 东西向相对距离
    y = (lat2 - lat1) * 60                  # 南北向相对距离
    
    # 2. 分解两船的速度向量 (向东为X，向北为Y)
    vx1 = sog1 * np.sin(np.radians(cog1))
    vy1 = sog1 * np.cos(np.radians(cog1))
    
    vx2 = sog2 * np.sin(np.radians(cog2))
    vy2 = sog2 * np.cos(np.radians(cog2))
    
    # 3. 求相对速度向量
    v_rx = vx2 - vx1
    v_ry = vy2 - vy1
    
    # 4. 计算相对速度的大小平方
    v_sq = v_rx**2 + v_ry**2
    
    # 5. 计算 TCPA (单位：小时)
    if v_sq < 1e-6: # 相对静止
        tcpa_hours = 0
    else:
        tcpa_hours = - (x * v_rx + y * v_ry) / v_sq
        
    # 只有 TCPA > 0 才说明是在靠近
    if tcpa_hours < 0:
        tcpa_minutes = 0
        dcpa = np.sqrt(x**2 + y**2)
    else:
        tcpa_minutes = tcpa_hours * 60
        dcpa_x = x + v_rx * tcpa_hours
        dcpa_y = y + v_ry * tcpa_hours
        dcpa = np.sqrt(dcpa_x**2 + dcpa_y**2)
        
    return dcpa, tcpa_minutes

# 测试
if __name__ == "__main__":
    print("开始进行雷达标绘计算测试...")
    
     # 船1在左边(西)，向东开；船2在右边(东)，向西开 -> 相向而行！
    dcpa, tcpa = calc_tcpa_dcpa(
        lat1=25.75, lon1=-80.20, sog1=10, cog1=90,  # 船1在西边，向东
        lat2=25.75, lon2=-80.11, sog2=12, cog2=270  # 船2在东边，向西
    )
    
    print(f"预测结果：")
    print(f"  - 最小会遇距离 (DCPA): {dcpa:.2f} 海里")
    print(f"  - 到达最近点时间 (TCPA): {tcpa:.1f} 分钟")
    
    if dcpa < 0.5 and tcpa < 15:
        print("  ⚠️ 判定结果: 存在严重碰撞风险！")
    else:
        print("  ✅ 判定结果: 安全。")
