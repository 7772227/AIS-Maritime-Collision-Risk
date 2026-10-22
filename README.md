# AIS-Based Maritime Edge Computing for Real-Time Vessel Collision Risk Assessment

## Research Question
Can lightweight AIS-based vessel collision-risk assessment be performed at maritime edge nodes to reduce communication overhead and warning latency under bandwidth-constrained maritime networks?

## Project Showcase

<p align="center">
  <img src="docs/iot_terminal.png" width="32%" alt="Edge Terminal" />
  <img src="CBF_Demo/cbf_result.png" width="32%" alt="CBF Safety Filter" />
  <img src="docs/radar_calculation_test.png" width="32%" alt="TCPA Calculation" />
</p>

## Architecture & Workflow
Maritime IoT Scenario
      ↓
AIS Data Stream (Replay)
      ↓
Shipboard / Near-shore Edge Node
      ↓
Real-time Risk Assessment (Vector-based DCPA / TCPA)
      ↓
Local Decision (Risk Alerts)
      ↓
[Optional] Control Interface (CBF Safety Filter)
(Note: This project is a prototype for Smart Ocean Networks, focusing on processing real AIS data to evaluate vessel collision risks and simulate edge-side processing.)

## Features & Modules

### Part 1: Historical Encounter Detection & Visualization (src/test_ais.py)
Uses Python (Pandas) to clean 300,000+ AIS records (filtering stationary vessels).
Generates interactive maps using Folium.
Scientific Note: This module calculates the Observed Minimum Separation from historical AIS trajectories, not the predictive DCPA. It synchronizes historical timestamps to identify past close encounters.

### Part 2: Predictive DCPA/TCPA & Radar Plotting (src/tcpa_calculator.py)
Implements the standard Maritime Radar Plotting algorithm.
Uses relative-motion vectors derived from SOG and COG to predict the true DCPA (Distance at Closest Point of Approach) and TCPA (Time to Closest Point of Approach).

### Part 3: Edge-oriented AIS Stream Simulation (src/iot_stream_sim.py)
Simulates an Edge Node receiving AIS data sequentially via replay.
Triggers local warnings dynamically based on predicted DCPA/TCPA.
Scientific Note: The current implementation replays historical records to emulate online processing. It does not yet model a real physical network (e.g., MQTT, network delay).
Threshold Note: The safety thresholds (e.g., 8nm, 1nm, 20min) used in the simulation are configurable experimental thresholds for the prototype stage, not regulatory maritime standards.

### Part 4: CBF Safety Control Proof-of-Concept (CBF_Demo/)
Demonstrates a Control Barrier Function (CBF-QP) safety filter for a 2D point-mass model.
Shows how a vessel automatically corrects its path to avoid a static obstacle. (See CBF_Demo/README.md for mathematical details).

## How to Run

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
2. Download the AIS dataset (e.g., data7.csv) and place it in the root directory of the project.
3. Run the modules:
python src/test_ais.py
python src/tcpa_calculator.py
python src/iot_stream_sim.py
python CBF_Demo/cbf_demo.py

## Future Work
1. Edge vs. Cloud Baseline: Conduct experiments comparing communication overhead and end-to-end warning latency between local edge processing and cloud-based processing under simulated maritime network constraints .
2. Vessel Dynamics & HOCBF: Upgrade the CBF model to account for vessel inertia (double integrator) and implement High-Order CBF (HOCBF).
3. COLREGs Integration: Encode maritime right-of-way rules as safety constraints within the CBF-QP framework.
4. IoT Messaging: Transition the stream simulation to a real MQTT-based publisher/subscriber architecture.
