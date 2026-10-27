import pandas as pd
import numpy as np
import time
import json
import os

# 引入雷达标绘计算函数
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

print("加载数据...")
df = pd.read_csv('../data7.csv', nrows=100) # 取100条做测试
df = df.dropna(subset=['LAT', 'LON', 'SOG', 'COG'])
lat_a, lon_a, sog_a, cog_a = 25.75, -80.11, 12.0, 270.0 

network_delays = [0.02, 0.05, 0.1, 0.2, 0.5] # 20ms, 50ms, 100ms, 200ms, 500ms
runs = 30 
DCPA_THRESHOLD = 8.0 
TCPA_THRESHOLD = 30.0

results = []
print("开始极速仿真测试...")

for delay in network_delays:
    for run in range(runs):
        for _, row in df.iterrows():
            
            # --- 1. Cloud Baseline ---
            t_start = time.perf_counter()
            # 模拟计算时间
            calc_tcpa_dcpa(lat_a, lon_a, sog_a, cog_a, row['LAT'], row['LON'], row['SOG'], row['COG'])
            t_end = time.perf_counter()
            
            payload = {"mmsi": int(row['MMSI']), "lat": float(row['LAT']), "lon": float(row['LON']), "sog": float(row['SOG']), "cog": float(row['COG'])}
            payload_size = len(json.dumps(payload).encode('utf-8'))
            
            # 核心：直接用算式算延迟 (计算耗时 + 网络延迟)，不真正 sleep
            cloud_latency = ((t_end - t_start) + delay) * 1000 
            
            # --- 2. Edge Baseline ---
            t_start = time.perf_counter()
            dcpa, tcpa = calc_tcpa_dcpa(lat_a, lon_a, sog_a, cog_a, row['LAT'], row['LON'], row['SOG'], row['COG'])
            t_end = time.perf_counter()
            
            edge_local_latency = (t_end - t_start) * 1000
            
            alert_triggered = 0
            alert_size = 0
            edge_notify_latency = edge_local_latency
            
            if dcpa < DCPA_THRESHOLD and tcpa < TCPA_THRESHOLD:
                alert_triggered = 1
                alert_payload = {"alert": "collision_risk", "dcpa": round(dcpa,2), "tcpa": round(tcpa,2)}
                alert_size = len(json.dumps(alert_payload).encode('utf-8'))
                # 边缘端报警延迟 = 计算耗时 + 报警上传网络延迟
                edge_notify_latency = edge_local_latency + (delay * 1000)

            results.append({"network_delay_ms": int(delay * 1000), "architecture": "Cloud", "transmitted_bytes": payload_size, "warning_latency_ms": cloud_latency, "alerts": alert_triggered})
            results.append({"network_delay_ms": int(delay * 1000), "architecture": "Edge_Local", "transmitted_bytes": 0, "warning_latency_ms": edge_local_latency, "alerts": alert_triggered})
            if alert_triggered:
                results.append({"network_delay_ms": int(delay * 1000), "architecture": "Edge_Notify", "transmitted_bytes": alert_size, "warning_latency_ms": edge_notify_latency, "alerts": alert_triggered})

os.makedirs('../results', exist_ok=True)
results_df = pd.DataFrame(results)
results_df.to_csv('../results/edge_vs_cloud_results.csv', index=False)
print(" 仿真完成！数据已保存至 results/edge_vs_cloud_results.csv")

# 计算并打印统计摘要
print("\n" + "="*50)
print("  Statistical Summary (Mean Latency in ms)")
print("="*50)
summary = results_df.groupby(['network_delay_ms', 'architecture'])['warning_latency_ms'].agg(['mean', 'median', lambda x: np.percentile(x, 95)]).reset_index()
summary.columns = ['Network Delay (ms)', 'Architecture', 'Mean', 'Median', 'P95']
print(summary.to_string(index=False))