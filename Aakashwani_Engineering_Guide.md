# Team Aakashvani: Official Engineering & Routing Guide 🚀

This document is the absolute source of truth for all teammates working on the CanSat PCB. Read this entirely before opening KiCad. Our goal is a flawlessly functioning, aerospace-grade 4-layer PCB that passes the CDR (Critical Design Review) with zero DRC errors.

---

## 👥 1. Team Roles & Task Delegation
To prevent Git merge conflicts and ensure everyone is working in parallel, we have split the hierarchical schematic into three distinct domains. **Do not edit a schematic sheet that does not belong to you.**

### 📡 Avionics & RF Lead (Sheet: `Avionics_Left`)
* **Components:** ESP32-S3 (Brain), XBee 3 Pro, CC1101, Edgehax NavIC (GPS), MicroSD.
* **Responsibilities:** You are in charge of all data processing and telemetry. Ensure the SPI and UART lines are cleanly routed to the ESP32. 
* **Critical Rule:** You MUST ensure Antenna Keepout Zones (Rule Areas) are drawn under the XBee and CC1101 to prevent the ground plane from blocking our radio signals.

### ⚡ Power Systems Lead (Sheet: `Power_Right`)
* **Components:** Li-Po Battery input, 5V Pololu BEC, MAX17048 Fuel Gauge, ESC for payload release/motors.
* **Responsibilities:** You are the heart of the CanSat. You handle high current and noisy switching voltages.
* **Critical Rule:** Route your power traces **thick** (minimum 0.5mm to 1.0mm). Keep your noisy 5V BEC strictly on the Right Wing of the H-Architecture to avoid interfering with the magnetometer.

### 🔬 Sensor Bridge Lead (Sheet: `Sensor_Bridge`)
* **Components:** BNO085 (IMU), BMP585 (Pressure/Alt), SHT4x (Temp/Hum), SGP41 (Gas).
* **Responsibilities:** You handle the delicate scientific payload.
* **Critical Rule:** I2C lines (SDA/SCL) must be routed carefully. Ensure the IMU is placed precisely in the physical center of the PCB so rotational math (quaternions) calculates correctly during descent.

---

## 🔌 2. Schematic Entry (Wiring)
1. **Never use internet symbols.** Press `A` to add a component and ALWAYS search for `Aakashwani_Master`.
2. For standard sensors that don't have custom symbols (like the BMP585), place a generic connector (e.g., `Conn_01x08` for an 8-pin breakout). 
3. Wire your VCC, GND, and data lines. 
4. Once your sheet is wired, click the **"Annotate Schematic"** button at the top to give every part a unique ID (e.g., `U1`, `J3`).

---

## 👣 3. Footprint Assignment
Once the schematic is fully annotated:
1. Click the **"Run Footprint Assignment Tool"** (Op-Amp icon with a footprint).
2. On the left pane, select `Aakashwani_Master`.
3. In the middle pane, select your component.
4. On the right pane, double-click the corresponding `.kicad_mod` file.
*Note: All footprints in our Master Library have been mathematically corrected to a precise 2.54mm grid. Trust the footprints.*

---

## 🛤️ 4. PCB Layout & Routing Rules (The H-Architecture)
When you press `F8` (Update PCB from Schematic), you will drop all components into the PCB Editor. Follow these strict rules:

### A. The 4-Layer Stackup
Go to **File -> Board Setup -> Physical Stackup**. Set it to 4 Layers:
* **Layer 1 (F.Cu):** Top Signal (Short data traces)
* **Layer 2 (In1.Cu):** Solid Ground Plane (GND)
* **Layer 3 (In2.Cu):** Solid Power Plane (3.3V)
* **Layer 4 (B.Cu):** Bottom Signal (Long data routing)
*Why?* Having solid inner planes gives our signals a clean return path and protects them from electromagnetic noise.

### B. Physical Placement (H-Shape)
1. **Left Side:** Place the ESP32 and RF modules here.
2. **Right Side:** Place the Battery, BEC, and Fuel Gauge here.
3. **Center:** Place the Sensors here. 
*Do not mix these domains.*

### C. Traces & Vias
* **Data Traces (I2C, SPI, UART):** 0.25mm width.
* **Power Traces (VCC, GND to planes):** 0.5mm to 1.0mm width.
* **Vias:** Use standard `0.8mm` diameter with a `0.4mm` drill. When connecting a top-layer component to Ground, drop a Via right next to the pin to instantly connect it to Layer 2 (In1.Cu).

### D. Antenna Keepouts
In the PCB editor, select the **"Add a rule area"** tool. Draw a box underneath the overhang of the XBee and NavIC antennas. Check the boxes to prohibit **Copper Pours, Vias, and Tracks on ALL LAYERS**. If you pour copper under an antenna, we will lose signal mid-flight.

---
**Git Protocol:** Always `git pull` before you start working. Always `git push` when you finish a clean sheet. Do not push if your schematic has broken wires. 

Good luck, team. Let's win this. 🛰️
