import pandas as pd
import time
import numpy as np
import os

# 1. 
def calc_tcpa_dcpa(lat1, lon1, sog1, cog1, lat2, lon2, sog2, cog2):
    lat_avg = np.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 60 * np.cos(lat_avg)
    y = (lat2 - lat1) * 60
    vx1 = sog1 * np.sin(np.radians(cog1))
    vy1 = sog1 * np.cos(np.radians(cog1))
    vx2 = sog2 * np.sin(np.radians(cog2))
    vy2 = sog2 * np.cos(np.radians(cog2))
    v_rx = vx2 - vx1
    v_ry = vy2 - vy1
    v_sq = v_rx**2 + v_ry**2
    
    if v_sq < 1e-6:
        tcpa_hours = 0
    else:
        tcpa_hours = - (x * v_rx + y * v_ry) / v_sq
        
    if tcpa_hours < 0: # 正在远离
        return np.sqrt(x**2 + y**2), 0.0
    else:
        dcpa = np.sqrt((x + v_rx * tcpa_hours)**2 + (y + v_ry * tcpa_hours)**2)
        return dcpa, tcpa_hours * 60

# 2. 
print("正在连接 AIS 数据网关...")
df = pd.read_csv('data7.csv', nrows=300000)
df = df.dropna(subset=['LAT', 'LON', 'SOG', 'COG', 'BaseDateTime'])
df_moving = df[df['SOG'] > 5].copy()
df_moving['BaseDateTime'] = pd.to_datetime(df_moving['BaseDateTime'])

# 用之前验证过有交集的船号
target_mmsi_1 = 319706000
target_mmsi_2 = 244561000

ship1 = df_moving[df_moving['MMSI'] == target_mmsi_1].sort_values(by='BaseDateTime')
ship2 = df_moving[df_moving['MMSI'] == target_mmsi_2].sort_values(by='BaseDateTime')

# 时间对齐，找前 30 个时间点
merged = pd.merge_asof(ship1, ship2, on='BaseDateTime', suffixes=('_1', '_2'), tolerance=pd.Timedelta('1min')).dropna(subset=['LAT_2', 'LON_2'])

if len(merged) == 0:
    print("没找到对齐的数据。")
else:
        # 智能寻找即将相撞的时间段
    # 计算所有时刻的 TCPA 和 DCPA，找到真正有危险的那个时间点
    merged['DCPA'] = 0.0
    merged['TCPA'] = 0.0
    for idx, row in merged.iterrows():
        d, t = calc_tcpa_dcpa(row['LAT_1'], row['LON_1'], row['SOG_1'], row['COG_1'], row['LAT_2'], row['LON_2'], row['SOG_2'], row['COG_2'])
        merged.at[idx, 'DCPA'] = d
        merged.at[idx, 'TCPA'] = t

    # 找到 TCPA > 0 且 DCPA 最小的那个时间点 
    valid_targets = merged[(merged['TCPA'] > 0) & (merged['TCPA'] < 60)]
    if len(valid_targets) > 0:
        target_idx = valid_targets['DCPA'].idxmin()
    else:
        target_idx = merged['DCPA'].idxmin() # 如果没找到，就找距离最近的

    # 截取即将相撞的前 10 个点，到相撞后的 10 个点
    start_idx = max(0, target_idx - 10)
    end_idx = min(len(merged), target_idx + 10)
    stream_data = merged.iloc[start_idx:end_idx]
    
    print(" 目标锁定！开始边缘节点实时计算...")
    time.sleep(1)

    for _, row in stream_data.iterrows():
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 计算真正的 DCPA 和 TCPA
        dcpa, tcpa = calc_tcpa_dcpa(
            row['LAT_1'], row['LON_1'], row['SOG_1'], row['COG_1'],
            row['LAT_2'], row['LON_2'], row['SOG_2'], row['COG_2']
        )
        
        # 计算当前距离
        lat_avg = np.radians((row['LAT_1'] + row['LAT_2']) / 2)
        current_dist = np.sqrt(((row['LON_2']-row['LON_1'])*60*np.cos(lat_avg))**2 + ((row['LAT_2']-row['LAT_1'])*60)**2)
        
        print("="*50)
        print("  船舶智能避碰边缘计算终端 (Edge Node)")
        print("="*50)
        print(f"  时间: {row['BaseDateTime']}")
        print(f"  船A (MMSI: {target_mmsi_1}): 航速 {row['SOG_1']} 节, 航向 {row['COG_1']}°")
        print(f"  船B (MMSI: {target_mmsi_2}): 航速 {row['SOG_2']} 节, 航向 {row['COG_2']}°")
        print("-" * 50)
        print(f"  当前距离 (Current Dist): {current_dist:.2f} 海里")
        print(f"  预测最近距离 (DCPA): {dcpa:.2f} 海里")
        print(f"  预测到达时间 (TCPA): {tcpa:.1f} 分钟")
        
        # 结合 DCPA 和 TCPA 进行预警
        if dcpa < 1.0 and tcpa < 20.0:
            print("\n 🚨 [碰撞警报] DCPA < 1海里 且 TCPA < 20分钟！")
            print(" [Control Interface] Safety-control module (e.g., CBF) would be activated.")
        elif dcpa < 3.0:
            print("\n  ⚠️ [警告] 预测会遇距离过近，持续监控。")
        else:
            print("\n  ✅️ [安全] 航行状态安全。")
            
        print("="*50)
        time.sleep(0.5) 
