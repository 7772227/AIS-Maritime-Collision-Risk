import pandas as pd
import numpy as np
import time
import json

# 1. 引入雷达标绘计算函数
def calc_tcpa_dcpa(lat1, lon1, sog1, cog1, lat2, lon2, sog2, cog2):
    lat_avg = np.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 60 * np.cos(lat_avg)
    y = (lat2 - lat1) * 60
    vx1 = sog1 * np.sin(np.radians(cog1)); vy1 = sog1 * np.cos(np.radians(cog1))
    vx2 = sog2 * np.sin(np.radians(cog2)); vy2 = sog2 * np.cos(np.radians(cog2))
    v_rx = vx2 - vx1; v_ry = vy2 - vy1
    v_sq = v_rx**2 + v_ry**2
    if v_sq < 1e-6: return np.sqrt(x**2 + y**2), 0.0
    tcpa_hours = - (x * v_rx + y * v_ry) / v_sq
    if tcpa_hours < 0: return np.sqrt(x**2 + y**2), 0.0
    dcpa = np.sqrt((x + v_rx * tcpa_hours)**2 + (y + v_ry * tcpa_hours)**2)
    return dcpa, tcpa_hours * 60

# 2. 准备数据 (读取前1000行做快速实验)
print("正在加载数据...")
df = pd.read_csv('../data7.csv', nrows=1000)
df = df.dropna(subset=['LAT', 'LON', 'SOG', 'COG'])
# 模拟两艘船，船A固定，船B取数据里的点
lat_a, lon_a, sog_a, cog_a = 25.75, -80.11, 12.0, 270.0 

# 设定网络模拟参数
NETWORK_LATENCY = 0.1 # 模拟 100ms 的海上网络延迟
DCPA_THRESHOLD = 8.0
TCPA_THRESHOLD = 20.0

# ==========================================
# 实验 A：Cloud Baseline (全量数据上云)
# ==========================================
print("\n[实验 A] 开始模拟 Cloud Baseline (所有数据传回云端计算)...")
cloud_bytes_sent = 0
cloud_latencies = []

start_time_cloud = time.perf_counter()

for _, row in df.iterrows():
    step_start = time.perf_counter()
    
    # 模拟船端打包数据上传
    payload = {
        "mmsi": int(row['MMSI']), "lat": float(row['LAT']), "lon": float(row['LON']), 
        "sog": float(row['SOG']), "cog": float(row['COG'])
    }
    json_str = json.dumps(payload)
    cloud_bytes_sent += len(json_str.encode('utf-8')) # 记录上传字节数
    
    # 模拟网络传输延迟
    time.sleep(NETWORK_LATENCY) 
    
    # 云端计算
    calc_tcpa_dcpa(lat_a, lon_a, sog_a, cog_a, row['LAT'], row['LON'], row['SOG'], row['COG'])
    
    step_end = time.perf_counter()
    cloud_latencies.append((step_end - step_start) * 1000) # 毫秒

end_time_cloud = time.perf_counter()
total_time_cloud = end_time_cloud - start_time_cloud

# ==========================================
# 实验 B：Edge Baseline (边缘端本地计算，只传警报)
# ==========================================
print("[实验 B] 开始模拟 Edge Baseline (边缘端计算，仅上传警报)...")
edge_bytes_sent = 0
edge_latencies = []
alerts_generated = 0

start_time_edge = time.perf_counter()

for _, row in df.iterrows():
    step_start = time.perf_counter()
    
    # 边缘端本地计算 (无网络延迟)
    dcpa, tcpa = calc_tcpa_dcpa(lat_a, lon_a, sog_a, cog_a, row['LAT'], row['LON'], row['SOG'], row['COG'])
    
    # 如果触发警报，才发数据给云端
    if dcpa < DCPA_THRESHOLD and tcpa < TCPA_THRESHOLD:
        alerts_generated += 1
        alert_payload = {"alert": "collision_risk", "dcpa": round(dcpa, 2), "tcpa": round(tcpa, 2)}
        alert_str = json.dumps(alert_payload)
        edge_bytes_sent += len(alert_str.encode('utf-8'))
        
        # 只有警报过网络，才会有延迟
        time.sleep(NETWORK_LATENCY) 
        
    step_end = time.perf_counter()
    edge_latencies.append((step_end - step_start) * 1000)

end_time_edge = time.perf_counter()
total_time_edge = end_time_edge - start_time_edge

# ==========================================
# 3. 打印对比结果
# ==========================================
print("\n" + "="*40)
print("  Edge vs Cloud Baseline Results")
print("="*40)
print(f" 处理数据量: {len(df)} 条 AIS 记录")
print(f" 模拟网络延迟: {NETWORK_LATENCY*1000} ms")
print("-" * 40)
print(f"  Cloud Baseline:")
print(f"    - 发送总字节: {cloud_bytes_sent} Bytes")
print(f"    - 总耗时: {total_time_cloud:.2f} s")
print(f"    - 平均单次延迟: {np.mean(cloud_latencies):.2f} ms")
print("-" * 40)
print(f"  Edge Baseline:")
print(f"    - 发送总字节: {edge_bytes_sent} Bytes")
print(f"    - 总耗时: {total_time_edge:.2f} s")
print(f"    - 平均单次延迟: {np.mean(edge_latencies):.2f} ms")
print(f"    - 触发警报次数: {alerts_generated} 次")
print("="*40)