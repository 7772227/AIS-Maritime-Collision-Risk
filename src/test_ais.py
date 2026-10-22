import pandas as pd
import folium
import numpy as np

# 计算两船距离的函数（海里）
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3440.065
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

df = pd.read_csv('data7.csv', nrows=300000)
df = df.dropna(subset=['LAT', 'LON', 'SOG', 'BaseDateTime'])
df_moving = df[df['SOG'] > 5].copy()

#  只保留佛罗里达南部海域的船只
# 纬度约 24~26.5，经度约 -82~-80
df_moving = df_moving[(df_moving['LAT'] > 24) & (df_moving['LAT'] < 26.5) & 
                      (df_moving['LON'] > -82) & (df_moving['LON'] < -80)]

# 找出该海域内的前10艘船
top_ships = df_moving['MMSI'].value_counts().head(10).index.tolist()

if len(top_ships) < 2:
    print("这片海域找不到两艘船，请换一个数据")
else:
    print(f"在佛罗里达南部海域找到了 {len(top_ships)} 艘船，开始两两配对计算...")
    
    found = False
    
    # 自动两两组合，直到找到真正相遇的船
    for i in range(len(top_ships)):
        for j in range(i+1, len(top_ships)):
            mmsi1 = top_ships[i]
            mmsi2 = top_ships[j]
            
            ship1 = df_moving[df_moving['MMSI'] == mmsi1].sort_values(by='BaseDateTime')
            ship2 = df_moving[df_moving['MMSI'] == mmsi2].sort_values(by='BaseDateTime')
            ship1['BaseDateTime'] = pd.to_datetime(ship1['BaseDateTime'])
            ship2['BaseDateTime'] = pd.to_datetime(ship2['BaseDateTime'])
            
            merged = pd.merge_asof(ship1, ship2, on='BaseDateTime', suffixes=('_1', '_2'), tolerance=pd.Timedelta('1min')).dropna(subset=['LAT_2', 'LON_2'])
            
            if len(merged) == 0:
                continue
                
            merged['distance_nm'] = haversine_distance(
                merged['LAT_1'].values, merged['LON_1'].values,
                merged['LAT_2'].values, merged['LON_2'].values
            )
            
            min_idx = merged['distance_nm'].idxmin()
            min_separation = merged.loc[min_idx, 'distance_nm']
            
            if min_separation < 10: 
                min_row = merged.loc[min_idx]
                print(f"\n⚠️ 找到会遇！MMSI: {mmsi1} and {mmsi2}")
                print(f"Observed Minimum Separation: {min_separation:.2f} nm")
                print(f"time: {min_row['BaseDateTime']}")
                
                center_lat = (min_row['LAT_1'] + min_row['LAT_2']) / 2
                center_lon = (min_row['LON_1'] + min_row['LON_2']) / 2
                m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
                
                folium.PolyLine(ship1[['LAT', 'LON']].values, color='blue', weight=3, tooltip=f"船1: {mmsi1}").add_to(m)
                folium.PolyLine(ship2[['LAT', 'LON']].values, color='red', weight=3, tooltip=f"船2: {mmsi2}").add_to(m)
                folium.Marker(
                    [min_row['LAT_1'], min_row['LON_1']], 
                    popup=f"min_separation: {min_separation:.2f} nm", icon=folium.Icon(color='orange', icon='warning-sign')
                ).add_to(m)
                
                m.save("collision_risk.html")
                print("成功，打开 collision_risk.html 查看两船会遇情况。")
                found = True
                break 
        if found:
            break
            
    if not found:
        print("\n：这片海域没有两艘船离得小于10海里。")
        print("建议：换数据。")
