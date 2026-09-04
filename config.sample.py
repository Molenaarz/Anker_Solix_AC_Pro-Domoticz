# === ANKER SOLIX TO DOMOTICZ CONFIGURATION ===

# Network Settings
DOMOTICZ_IP = "http://127.0.0.1:8080"  # IP and port of your Domoticz server
ANKER_IP = "192.168.1.X"               # IP address of your Anker Solarbank (check your app)
PORT = 502                             # Default Modbus TCP port
INTERVAL = 10                          # Refresh interval in seconds

# Domoticz Virtual Sensor IDX Numbers
# Replace these with your own IDX numbers from the Domoticz devices list
IDX_BATTERY_SOC = 1001      # Type: General / Percentage (Battery SoC %)
IDX_PV_POWER = 1002         # Type: Usage / Electric (Solar Generation Watts)
IDX_BATTERY_POWER = 1003    # Type: Electric (Instant+Counter) -> For Energy Dashboard
IDX_BATTERY_VOLTAGE = 1004  # Type: General / Voltage (Grid AC Voltage)

# Optional Diagnostic & Lifetime Sensors (Set to None to disable)
IDX_BATTERY_SOH = 1005      # Type: General / Percentage (Battery Health %)
IDX_TEMPERATURE = 1006      # Type: Temp / LaCrosse TX3 (Internal Temperature °C)
IDX_TOTAL_CHARGE = 1007     # Type: RFXMeter / Counter (Lifetime Charged Wh)
IDX_TOTAL_DISCHARGE = 1008  # Type: RFXMeter / Counter (Lifetime Discharged Wh)
