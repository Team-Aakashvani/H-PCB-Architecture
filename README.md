# Team Aakashvani - CanSat CDR Flight Stack 🚀

Welcome to the official aerospace hardware repository for **Team Aakashvani**. This repository contains the complete electronics design, schematic architecture, custom engineering tools, and mathematical power budgets for our CanSat flight mission.

---

## 🏗️ Hardware Architecture (H-PCB Concept)
To survive the extreme vibrational and electromagnetic challenges of a rocket launch and atmospheric descent, we have engineered a custom **H-Shape PCB Architecture**. 

Instead of a single monolithic board, the system is separated into highly isolated domains:
1. **Avionics & Telemetry (Left Wing):** Houses the main ESP32-S3 brain and high-power RF communications (XBee 3 Pro & CC1101).
2. **Power Distribution (Right Wing):** Handles the Li-Po battery, 5V BEC (Pololu), and fuel gauge (MAX17048), keeping high-current switching noise far away from delicate sensors.
3. **Sensor Bridge (Center Crossbar):** Suspended securely between the wings, this isolates our precision I2C/SPI sensors (BNO085 IMU, BMP585 Pressure, SGP41, SHT4x, NavIC GPS) from both mechanical stress and RF interference.

*Note: All RF antennas have mathematically calculated Electromagnetic Keepout Zones (Rule Areas) blocking copper traces on all 4 layers beneath them to maximize telemetry range.*

---

## 🛠️ Proprietary Engineering Tools
To guarantee millimeter-perfect mechanical fits for breakout boards that lack official manufacturer footprints, we developed a proprietary in-house CAD tool: **The Aakashwani Visual Footprint Generator**.

Built natively in Python (`Visual_Footprint_Generator.py`), this tool allows engineers to:
* Eradicate camera lens distortion using **4-Point Perspective Correction**.
* Mathematically level crooked photographs with **Auto-Leveling**.
* Click physical pads to generate standard `.kicad_mod` S-expression code.
* Snap bounding boxes perfectly using a **Photoshop-style Magnetic Lasso**.
* Export exact 2.54mm grid-snapped, strictly orthogonal PCB layouts.

---

## 📚 The Aakashwani Master Library
We do not rely on generic, unverified internet footprints that risk mission failure. 

Every single sensor, RF module, and power IC in this project is sourced from the `Aakashwani_Master_Library`. 
* All **Symbols** (`.kicad_sym`) have been programmatically cross-referenced to guarantee perfect pin-to-pad mappings.
* All **Footprints** (`.kicad_mod`) have been mathematically corrected to ensure pads snap strictly to 2.54mm pitches relative to Pin 1, and courtyard outlines are strictly 90-degree orthogonal boxes. 
* All Pads feature a **0.35mm Annular Ring** and `*.Cu` 4-layer through-hole plating to survive launch vibrations without delamination.

---

## 🚀 Getting Started (For Team Members)
1. **Clone this repository** anywhere on your PC. (Do not move individual files out of the main folder).
2. Ensure you have **KiCad 7 or KiCad 8** installed.
3. Open `Aakashwani_CAN7USAT_Flight/Aakashwani_CAN7USAT_Flight.kicad_pro`.
4. Our `fp-lib-table` and `sym-lib-table` have been configured using relative `${KIPRJMOD}` paths. KiCad will automatically detect the Master Library!
5. Open the schematic, use the **Footprint Assignment Tool** to map components, and hit `F8` to push to the PCB editor.

---
*For Jury Members and Evaluators: Please refer to the `Aakashwani_Hardware_Planning.pptx` and `Cansat_Power_Budget.xlsx` for detailed mathematical derivations of our subsystem designs.*
