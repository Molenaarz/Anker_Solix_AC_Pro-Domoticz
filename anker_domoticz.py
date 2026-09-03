import time
import requests
import struct
from pymodbus.client import ModbusTcpClient

# Laad de configuratie uit het losse config.py bestand
try:
    import config
except ImportError:
    print("Fout: config.py niet gevonden! Maak deze aan op basis van het voorbeeld.")
    exit(1)

def read_modbus_register(client, address, count=1):
    try:
        res = client.read_input_registers(address=address, count=count, device_id=1)
    except TypeError:
        res = client.read_input_registers(address=address, count=count, slave=1)
        
    if res.isError() or not hasattr(res, 'registers') or not res.registers:
        return None
        
    if count == 1:
        return res.registers[0] if isinstance(res.registers, list) else res.registers
    return res.registers

def read_anker_data(client):
    try:
        # Registers uitlezen via Input Registers (Functie 04)
        soc_val = read_modbus_register(client, address=10256, count=1)
        soh_val = read_modbus_register(client, address=10257, count=1)
        pv_val = read_modbus_register(client, address=10012, count=1)
        volt_val = read_modbus_register(client, address=10101, count=1)
        temp_val = read_modbus_register(client, address=10053, count=1)
        pwr_reg = read_modbus_register(client, address=10254, count=2)

        if soc_val is None or pwr_reg is None:
            return

        # Data formatteren
        soc = soc_val if soc_val <= 100 else 100
        soh = soh_val if (soh_val is not None and soh_val <= 100) else 100
        pv_power = pv_val if pv_val is not None else 0
        
        # 32-bit Signed Integer voor het batterijvermogen
        if isinstance(pwr_reg, list) and len(pwr_reg) >= 2:
            raw_pwr_bytes = struct.pack('>HH', pwr_reg[0], pwr_reg[1])
            bruto_power = struct.unpack('>i', raw_pwr_bytes)[0]
        else:
            bruto_power = 0
        
        # Netto AC vermogen naar huis (gladgestreken voor inverter overhead)
        netto_ac = int(bruto_power * 0.82) if bruto_power < 0 else bruto_power

        # Netspanning formatteren
        if volt_val is not None and volt_val > 1000 and volt_val < 3000:
            grid_volt = round(volt_val / 10.0, 1)
        else:
            grid_volt = 230.0

        # Temperatuur formatteren
        if temp_val is not None and temp_val > 0:
            device_temp = round(temp_val / 10.0, 1) if temp_val > 100 else float(temp_val)
        else:
            device_temp = 20.0

        # Laad- en ontlaadwatts splitsen voor de Domoticz-tellers
        charge_w = bruto_power if bruto_power > 0 else 0
        discharge_w = abs(bruto_power) if bruto_power < 0 else 0

        print(f"[{time.strftime('%X')}] SoC: {soc}% | SOH: {soh}% | Temp: {device_temp}°C | Netto: {netto_ac}W | Netspanning: {grid_volt}V")
        
        # Gegevens verzenden naar Domoticz op basis van config
        send_to_domoticz(config.IDX_BATTERY_SOC, soc)
        send_to_domoticz(config.IDX_PV_POWER, pv_power)
        send_to_domoticz(config.IDX_BATTERY_POWER, netto_ac)
        send_to_domoticz(config.IDX_BATTERY_VOLTAGE, grid_volt)
        
        if config.IDX_BATTERY_SOH: send_to_domoticz(config.IDX_BATTERY_SOH, soh)
        if config.IDX_TEMPERATURE: send_to_domoticz(config.IDX_TEMPERATURE, device_temp)
        if config.IDX_TOTAL_CHARGE: send_to_domoticz(config.IDX_TOTAL_CHARGE, charge_w)
        if config.IDX_TOTAL_DISCHARGE: send_to_domoticz(config.IDX_TOTAL_DISCHARGE, discharge_w)
            
    except Exception as e:
        print(f"Fout tijdens verwerken van de Modbus-data: {e}")

def send_to_domoticz(idx, value):
    if idx is None:
        return
    svalue = str(value)
    if idx == config.IDX_BATTERY_POWER:
        svalue = f"{value};0"

    url = f"{config.DOMOTICZ_IP}/json.htm?type=command&param=udevice&idx={idx}&nvalue=0&svalue={svalue}"
    try:
        requests.get(url, timeout=2)
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Anker Solix Service gestart. Interval: {config.INTERVAL} seconden.")
    client = ModbusTcpClient(config.ANKER_IP, port=config.PORT)
    
    try:
        while True:
            if not client.is_socket_open():
                client.connect()
                
            read_anker_data(client)
            time.sleep(config.INTERVAL)
            
    except KeyboardInterrupt:
        print("\nService handmatig gestopt.")
    finally:
        client.close()
