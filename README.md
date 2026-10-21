# AIS Maritime Collision Risk Analysis

## Overview
This project is a prototype for **Smart Ocean Networks**, focusing on processing real Automatic Identification System (AIS) data to evaluate vessel collision risks.
## 📸 Project Showcase

<p align="center">
  <img src="docs/iot_terminal.png" width="32%" />
  <img src="CBF_Demo/cbf_result.png" width="32%" />
  <img src="docs/radar_calculation_test.png" width="32%" />
</p>

## Features
- **Data Processing:** Uses Python (Pandas) to clean and filter 300,000+ AIS records (filtering out stationary vessels with SOG < 5 knots).
- **Trajectory Visualization:** Uses Folium to generate interactive maps showing vessel paths ordered by timestamp.
- **Collision Risk Detection:** Implements the Haversine formula to calculate the **DCPA (Distance to Closest Point of Approach)** between moving vessels, identifying potential close encounters.

## Test Result
The algorithm successfully identified a specific encounter between two vessels (MMSI: 319706000 and 244561000) with a closest distance (DCPA) of 7.23 nautical miles. (See `collision_risk.html` for the map).

## Future Work
- Integrate TCPA (Time to Closest Point of Approach) calculations.
- Explore deploying this lightweight risk assessment on **Edge Computing nodes** under limited maritime bandwidth.
- Combine **Control Barrier Functions (CBF)** with DCPA constraints for autonomous ship safety control.
## Part 2: CBF-based Safety Control (CBF_Demo)

To address the collision risks identified by the AIS data analysis, I further explored safety control strategies using **Control Barrier Functions (CBF)**.

I implemented a CBF-QP (Quadratic Programming) safety filter in Python (located in the `CBF_Demo` folder). The simulation demonstrates how a vessel (the blue trajectory) automatically corrects its nominal path to avoid a danger zone (red circle) and safely reaches its target.

**Future integration:** The next step is to combine the DCPA-based risk assessment logic with the CBF safety filter and deploy this lightweight computation onto **embedded edge computing nodes** for autonomous maritime navigation.
## Part 3: IoT Real-time Stream Simulation (Edge Node)

To simulate real-time data flow in a maritime IoT environment, I developed `iot_stream_sim.py`. Instead of processing batch historical data, it simulates how an **Edge Node** (e.g., a shipboard terminal) receives AIS data sequentially from VHF receivers.

The script calculates the dynamic distance between two vessels on the fly and triggers warnings when the distance falls below the safety threshold (8 nautical miles). This demonstrates the feasibility of deploying lightweight collision risk algorithms for real-time edge computing. 
*(See `iot_terminal.png` for the terminal simulation output)*
## Part 4: TCPA Calculation & Radar Plotting Logic

Beyond just calculating the current distance or historical DCPA, I implemented the standard **Maritime Radar Plotting** algorithm (vector-based) in `tcpa_calculator.py`. 

By decomposing Speed Over Ground (SOG) and Course Over Ground (COG) into relative velocity vectors, the system can predict the **Time to Closest Point of Approach (TCPA)** in real-time. As shown in the test (`radar_calculation_test.png`), if two vessels are on a collision course, the algorithm accurately predicts a DCPA of 0.00 nm and a TCPA of 13.3 minutes, triggering a severe collision risk warning.
