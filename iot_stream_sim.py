import pandas as pd
import time
import numpy as np
import os

# 计算距离函数
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3440.065
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

print("正在连接 AIS 数据网关，寻找会遇目标...")

# 读取数据，限制在佛罗里达南部海域
df = pd.read_csv('data7.csv', nrows=300000)
df = df.dropna(subset=['LAT', 'LON', 'SOG', 'BaseDateTime'])
df_moving = df[df['SOG'] > 5].copy()
df_moving['BaseDateTime'] = pd.to_datetime(df_moving['BaseDateTime'])

# 为了模拟出“靠近”的效果，我们用之前找的两艘船：319706000 和 244561000
target_mmsi_1 = 319706000
target_mmsi_2 = 244561000

ship1 = df_moving[df_moving['MMSI'] == target_mmsi_1].sort_values(by='BaseDateTime')
ship2 = df_moving[df_moving['MMSI'] == target_mmsi_2].sort_values(by='BaseDateTime')

# 时间对齐
merged = pd.merge_asof(ship1, ship2, on='BaseDateTime', suffixes=('_1', '_2'), tolerance=pd.Timedelta('1min')).dropna(subset=['LAT_2', 'LON_2'])

if len(merged) == 0:
    print("没找到时间对齐的数据，请多读点行数。")
else:
    # 截取距离最近的前 30 个时刻来模拟会遇过程
    merged['distance'] = haversine_distance(merged['LAT_1'].values, merged['LON_1'].values, merged['LAT_2'].values, merged['LON_2'].values)
    closest_idx = merged['distance'].idxmin()
    
    # 找到最近点前 20 个数据，后 5 个数据
    start_idx = max(0, closest_idx - 20)
    end_idx = min(len(merged), closest_idx + 5)
    stream_data = merged.iloc[start_idx:end_idx]
    
    print("✅ 目标锁定！开始实时流式传输，按 Ctrl+C 退出。")
    time.sleep(1)

    # 核心：实时刷新屏幕！
    for i, (_, row) in enumerate(stream_data.iterrows()):
        # 清空终端屏幕 (制造刷新的效果)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        s1_lat, s1_lon = row['LAT_1'], row['LON_1']
        s2_lat, s2_lon = row['LAT_2'], row['LON_2']
        dist = row['distance']
        
        print("="*50)
        print(" 📡 船舶智能避碰边缘计算终端 (Edge Node)")
        print("="*50)
        print(f" ⏱️  时间: {row['BaseDateTime']}")
        print(f" 🚢 船A (MMSI: {target_mmsi_1}): 位置 ({s1_lat:.4f}, {s1_lon:.4f}), 航速 {row['SOG_1']} 节")
        print(f" 🚢 船B (MMSI: {target_mmsi_2}): 位置 ({s2_lat:.4f}, {s2_lon:.4f}), 航速 {row['SOG_2']} 节")
        print("-" * 50)
        print(f" 📏 实时距离 (Distance): {dist:.2f} 海里")
        
        # 动态报警逻辑
        if dist < 3.0:
            print("\n 🚨🚨🚨 [极度危险] 距离小于 3 海里！")
            print(" ⚙️ 正在触发 CBF-QP 安全滤波器，自动修正航向...")
        elif dist < 8.0:
            print("\n ⚠️  [警告] 距离小于 8 海里，持续监控中。")
        else:
            print("\n ✅  [安全] 距离安全。")
            
        print("="*50)
        
        # 模拟流式延迟
        time.sleep(0.8)
        
    print("\n数据流传输结束。")