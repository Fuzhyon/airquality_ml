#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bme680
import datetime
import time
import pandas as pan
import databaseconfig as cfg
from sqlalchemy import create_engine



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
df_airquality = pan.DataFrame(columns=["temperature", "pressure", "humidity", "record_datetime", "airquality"])
sensor_temperature = []
sensor_pressure = []
sensor_humidity = []
sensor_airquality = []
sensor_time = []

counter_fivemin_db_storing = 0
day_counter = 0

try:
    while True:
        if sensor.get_sensor_data():
            output = datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S,')+'{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH'.format(
                sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)
            if sensor.data.heat_stable:
                print('{0},{1} Ohms'.format(
                    output,
                    sensor.data.gas_resistance))
                if (counter_fivemin_db_storing == 299) :
                    sensor_airquality.append(sensor.data.gas_resistance)
            else:
                print(output)
            time.sleep(1)

            print(counter_fivemin_db_storing)
            counter_fivemin_db_storing += 1
            day_counter += 1
            if (counter_fivemin_db_storing >= 300) :
                counter_fivemin_db_storing = 0
                sensor_temperature.append(sensor.data.temperature)
                sensor_pressure.append(sensor.data.pressure)
                sensor_humidity.append(sensor.data.humidity)
                sensor_time.append(time.mktime(datetime.datetime.now().timetuple()))
                engine = create_engine("mysql://"+cfg.mysql['user']+':'+cfg.mysql["password"]+'@'+cfg.mysql["host"]+':'+cfg.mysql["port"]+'/'+cfg.mysql['db'])
                df_airquality["temperature"] = pan.Series(sensor_temperature)
                df_airquality["pressure"] = pan.Series(sensor_pressure)
                df_airquality["humidity"] = pan.Series(sensor_humidity)
                df_airquality["airquality"] = pan.Series(sensor_airquality, dtype=object)
                df_airquality["record_datetime"] = pan.Series(sensor_time)
                df_airquality.to_sql("sensors_data",con=engine, if_exists='append',index=False)

            if (day_counter >= 86400):
                engine = create_engine("mysql://"+cfg.mysql['user']+':'+cfg.mysql["password"]+'@'+cfg.mysql["host"]+':'+cfg.mysql["port"]+'/'+cfg.mysql['db'])
                df_airquality["temperature"] = pan.Series(sensor_temperature)
                df_airquality["pressure"] = pan.Series(sensor_pressure)
                df_airquality["humidity"] = pan.Series(sensor_humidity)
                df_airquality["airquality"] = pan.Series(sensor_airquality, dtype=object)
                df_airquality["record_datetime"] = pan.Series(sensor_time)
                df_airquality.to_sql("sensors_data",con=engine, if_exists='append',index=False)
                df_airquality = pan.DataFrame(columns=["temperature", "pressure", "humidity", "record_datetime", "airquality"])
                day_counter = 0
            
except KeyboardInterrupt:
    print(sensor_airquality)
    df_airquality["temperature"] = pan.Series(sensor_temperature)
    df_airquality["pressure"] = pan.Series(sensor_pressure)
    df_airquality["humidity"] = pan.Series(sensor_humidity)
    df_airquality["airquality"] = pan.Series(sensor_airquality, dtype=object)
    df_airquality["record_datetime"] = pan.Series(sensor_time)
    print(df_airquality)

# from datetime import datetime

# # current date and time
# now = datetime.now()

# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)
