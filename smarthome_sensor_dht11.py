# Smart Home sensor program
# MicroPython and ESP32 https://docs.micropython.org/en/latest/esp32/quickref.html
# https://docs.micropython.org/en/latest/library/espnow.html
# https://randomnerdtutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
 
import network
import espnow

from machine import Pin
import time

import dht                             # The DHT11 module

########################################
# OWN MODULES
from adc_sub import ADC_substitute

########################################
# CONFIGURATION
dashboard_mac_address = b'INSERT MAC HERE IN CORRECT FORMAT EG: \xA1\xB2\xC3\xD4\xE5\xF6' # MAC address of dashboard (Educaboard). Byte string format!

# Sensor
sensor_id = "DHT11"                    # The sensor ID
pin_dht11 = 32                         # The ultra sound digital trigger GPIO output pin

# Battery
pin_battery = 34                       # The battery measurement input pin, ADC1_6

########################################
# OBJECTS
# ESP-NOW
sta = network.WLAN(network.STA_IF)     # Or network.AP_IF
sta.active(True)                       # WLAN interface must be active to send()/recv()

en = espnow.ESPNow()                   # ESP-NOW object
en.active(True)                        # Make ESP-NOW active

# Sensor
sensor = dht.DHT11(Pin(pin_dht11))

# Battery
battery = ADC_substitute(pin_battery)  # The battery object

########################################
# VARIABLES
# Previous values
prev_sensor_value_temp = -999          # The previous value from the sensor
prev_sensor_value_hum = -999           # The previous value from the sensor
prev_bat_pct = -1                      # The previous battery percentage value

########################################
# FUNCTIONS
def get_battery_percentage():          # The battery voltage percentage
    return 24                          # Replace with own math. Use function in adc_sub.py
                                       # Make the result an integer value, and avoid neg. and above 100% values

# value = battery.read_adc()
# value = battery.read_voltage()
# bat_pct = int(alpha * value + beta)
# if bat_pct < 0:
#     bat_pct = 0
# elif bat_pct > 100:
#     bat_pct = 100
# 
# return bat_pct

########################################
# PROGRAM

# INITIALIZATION
# ESP-NOW
en.add_peer(dashboard_mac_address)     # Must add_peer() before send()
en.send(dashboard_mac_address, sensor_id + " ready", False)

print(sensor_id + " ready")

# MAIN (super loop)
while True:
    # Measure the battery percentage
    bat_pct = get_battery_percentage()
    
    # Check the sensor
    sensor.measure()
    sensor_value_temp = sensor.temperature()
    sensor_value_hum = sensor.humidity()

    # Send data if there is a change (this principle saves power)
    if bat_pct != prev_bat_pct or sensor_value_temp != prev_sensor_value_temp or sensor_value_hum != prev_sensor_value_hum:
        data_string = str(time.ticks_ms()) + '|' + str(bat_pct) + '|' + str(sensor_value_temp) + '|' + str(sensor_value_hum) # The data to send. CHANGE IT!
        
        print("Sending: " + data_string)
        try:
            en.send(dashboard_mac_address, data_string, False)
        except ValueError as e:
            print("Error sending the message: " + str(e))  
        
        # Update the previous values for use next time
        prev_bat_pct = bat_pct
        prev_sensor_value_temp = sensor_value_temp
        prev_sensor_value_hum = sensor_value_hum
    
