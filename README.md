# AIS Maritime Collision Risk Analysis

## Overview
This project is a prototype for **Smart Ocean Networks**, focusing on processing real Automatic Identification System (AIS) data to evaluate vessel collision risks.

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
