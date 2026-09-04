# Anker SOLIX Solarbank 2 / Max AC Pro to Domoticz

A lightweight, local, Python integration to bridge the **Anker SOLIX Solarbank 2 / Max AC Pro** series directly into **Domoticz** using local Modbus TCP. No cloud login required, completely local, and fully compatible with the official Domoticz Energy Dashboard.

This script runs as a continuous background daemon (systemd service) and polls your solar battery every 10 seconds for real-time visualization.

## Features
- 🔋 **Real-time SoC & SOH** (State of Charge and State of Health percentages).
- ☀️ **Solar PV Generation** monitoring.
- 🏡 **Net AC Output Tracking** beautifully mapped to a single bi-directional sensor (positive for charging, negative for discharging into your home).
- ⚡ **Grid AC Voltage monitoring** (uncovers 230V/240V mains grid fluctuations).
- 🌡️ **Internal Hardware Temperature** logging.
- 📊 **Calculated Cumulative Counters** for total lifetime charge and discharge.

---

## Prerequisites

1. **Enable Modbus TCP:** Open your official Anker SOLIX app, navigate to your Solarbank settings, find the **Modbus TCP** section, and turn it on. Note the IP address assigned to the battery.
2. **Python 3 Environment:** Ensure you have Python 3 and `pip` installed on your Domoticz server (Mini-PC/Raspberry Pi).

---

## Domoticz Virtual Sensors Setup

Go to **Setup > Hardware** in Domoticz, add a **Dummy (Does nothing)** hardware device named `Anker SOLIX`, and create the following virtual sensors using the **Create Virtual Sensors** button:

| Sensor Name | Sensor Type | Description |
| :--- | :--- | :--- |
| `Anker Battery SoC` | **Percentage** | Tracks battery level (0-100%) |
| `Anker PV Power` | **Usage (Electric)** | Tracks real-time Solar input in Watts |
| `Anker Battery Power` | **Electric (Instant+Counter)** | **Crucial:** Handles bi-directional energy flow into the Energy Dashboard |
| `Anker Grid Voltage` | **Voltage** | Monitors grid wisselspanning (~230V) |
| `Anker Battery SOH` | **Percentage** | Tracks battery cell health degradation over time |
| `Anker System Temp` | **Temperature** | Internal device temperature |
| `Anker Total Charged` | **Incremental Counter** | **Crucial:** Tracks cumulative charging in Wh without chart errors |
| `Anker Total Discharged`| **Incremental Counter** | **Crucial:** Tracks cumulative discharging in Wh without chart errors |

*Note all the **IDX** numbers of these new sensors from the **Setup > Devices** list.*

---

## Installation & Configuration

1. Clone this repository into your preferred folder and navigate into it:
   ```bash
   git clone https://github.com
   cd Anker_Solix_AC_Pro-Domoticz
   ```

2. Create a clean isolated virtual environment and install dependencies:
   ```bash
   python3 -m venv Anker
   ./Anker/bin/pip install pymodbus requests
   ```

3. Configure your specific parameters. Open `config.py` and fill in your battery IP address and your Domoticz IDX numbers:
   ```bash
   nano config.py
   ```

---

## Running as a Persistent Background Service (Systemd Daemon)

To make sure Linux continuously runs this script in the background and restarts it automatically after a system reboot or power failure, set it up as a systemd service:

1. Create the service definition file:
   ```bash
   sudo nano /etc/systemd/system/ankersolix.service
   ```

2. Paste the following configuration (verify your paths if you didn't install it in `/anker_script`):
   ```ini
   [Unit]
   Description=Anker Solix Modbus to Domoticz Service
   After=network.target

   [Service]
   User=root
   Group=root
   WorkingDirectory=/anker_script
   ExecStart=/anker_script/Anker/bin/python3 -u /anker_script/anker_domoticz.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. Reload systemd, enable the service to auto-start on boot, and start it right now:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ankersolix.service
   sudo systemctl start ankersolix.service
   ```

4. Check if your logs are successfully streaming live without buffering:
   ```bash
   journalctl -u ankersolix.service -f -n 10
   ```

---

## Energy Dashboard Configuration

1. Open Domoticz, go to **Setup > Settings > Energy Dashboard Setup**.
2. Assign **`Anker Battery Power`** to the **Battery** field.
3. Assign **`Anker Battery SoC`** to the **Battery SOC** field.
4. Assign **`Anker Grid Voltage`** to the **Battery Voltage** field.
5. Set `Battery Energy In` and `Battery Energy Out` to **Disabled** (our script already feeds all unified calculations directly through the main Battery sensor).
6. Click **Save**. Your battery visual tracking is now fully active!

## License
This project is open-source and available under the [MIT License](LICENSE).
