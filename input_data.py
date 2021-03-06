import RPi.GPIO as GPIO   ## GPIO
import time               ## Tiempo
import busio              ## Conexión i2c
import board              ##
import adafruit_veml6070  ## Sensor VELM6070
import Adafruit_DHT       ## Sensor AM2301
import requests           ## Envio de datos por Thingspeak

sensor = Adafruit_DHT.DHT22  ## Sensor de termperatura y humedad relativa AM2301

##Pines GPIO:
TH = 15     ## GPIO 15 sensor de temperatura y humedad relativa
LDR = 18    ## GPIO 18 sensor LDR
RAIN = 17   ## GPIO 17 sensor de lluvia
WIND = 27   ## Sensor de velocidad de viento

GPIO.setmode(GPIO.BCM)

GPIO.setup(LDR, GPIO.IN)
GPIO.setup(RAIN, GPIO.IN)
GPIO.setup(WIND,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

## Toma ciclica de datos:

while True:
    
    ## Lectura rayos UV:
    with busio.I2C(board.SCL, board.SDA) as i2c:
        uv = adafruit_veml6070.VEML6070(i2c)
        
        uv_raw = uv.uv_raw
        risk_level = uv.get_index(uv_raw)
    
    ## Lectura temperatura y humedad relativa:
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, TH)
    if humedad is not None and temperatura is not None:
        temperatura = temperatura
        tumedad = humedad
    
    else:
        print('Fallo la lectura del sensor AM2301 - Intentar de nuevo')
    
    ## Lectura LDR:
    lectura = GPIO.input(LDR)
    if lectura == 1:
        info_ldr = 'Oscuro'
        ldr = 0
    else:
        info_ldr = 'iluminado'
        ldr = 1
        
    ## Lectura Lluvia:
    lectura = GPIO.input(RAIN)
    if lectura == 1:
        info_rain = 'Seco'
        rain = 0
    else:
        info_rain = 'Precipitación'
        rain = 1
    
    print(f'Indice UV={uv_raw}, Nivel UV ={risk_level} | Velocidad de viento= NN | Temperatura={temperatura:.2f}°C | Humedad={humedad:.2f}% | {info_ldr} | {info_rain}')
    enviar = requests.get(f'https://api.thingspeak.com/update?api_key=VEX7N395HLX3Z5RE&field1={temperatura}&field2={humedad}&field3={uv_raw}&field5={ldr}&field6={rain}')
    time.sleep(60)