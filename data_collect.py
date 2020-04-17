#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bme680
import datetime
import time
import pandas as pan
import databaseconfig as cfg
import sqlalchemy as db



print("""read-all.py - Displays temperature, pressure, humidity, and gas.

Press Ctrl+C to exit!

""")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These calibration data can safely be commented
# out, if desired.

print('Calibration data:')
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print('{}: {}'.format(name, value))

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print('\n\nInitial reading:')
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print('{}: {}'.format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

print('\n\Récupération:')
df_airquality = pan.DataFrame(columns=["Temperature", "Pressure", "Humidity", "Time", "Airquality"])
sensor_temperature = []
sensor_pressure = []
sensor_humidity = []
sensor_airquality = []
sensor_time = []

try:
    while True:
        if sensor.get_sensor_data():
            sensor_temperature.append(sensor.data.temperature)
            sensor_pressure.append(sensor.data.pressure)
            sensor_humidity.append(sensor.data.humidity)
            sensor_time.append(datetime.datetime.now())

            output = datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S,')+'{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH'.format(
                sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)
            if sensor.data.heat_stable:
                print('{0},{1} Ohms'.format(
                    output,
                    sensor.data.gas_resistance))
                sensor_airquality.append(sensor.data.gas_resistance)
            else:
                print(output)
            time.sleep(1)

except KeyboardInterrupt:
	df_airquality["Temperature"] = pan.Series(sensor_temperature)
	df_airquality["Pressure"] = pan.Series(sensor_pressure)
	df_airquality["Humidity"] = pan.Series(sensor_humidity)
	df_airquality["Airquality"] = pan.Series(sensor_airquality, dtype=object)
	df_airquality["Time"] = pan.Series(sensor_time)
	print(df_airquality)

# from datetime import datetime

# # current date and time
# now = datetime.now()

# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)


engine = db.create_engine('mysql://'+cfg.mysql['user']+':'+cfg.mysql["password"]+'@'+cfg.mysql["host"])
connection = engine.connect()
print(connection)
