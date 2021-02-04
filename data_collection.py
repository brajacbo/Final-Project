## Librerias:
import RPi.GPIO as GPIO   ## GPIO
import time               ## Tiempo
import busio              ## Conexión i2c
import board              ##
import adafruit_veml6070  ## Sensor VELM6070
import Adafruit_DHT       ## Sensor AM2301
import requests           ## Envio de datos por Thingspeak
import pandas as pd       ## Pandas

sensor = Adafruit_DHT.DHT22  ## Sensor de termperatura y humedad relativa AM2301

## Pines GPIO:
TH = 15     ## GPIO 15 sensor de temperatura y humedad relativa
LDR = 18    ## GPIO 18 sensor LDR
RAIN = 17   ## GPIO 17 sensor de lluvia
WIND = 27   ## Sensor de velocidad de viento

GPIO.setmode(GPIO.BCM)

GPIO.setup(LDR, GPIO.IN)
GPIO.setup(RAIN, GPIO.IN)
GPIO.setup(WIND,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

## Listas vacias de los datos de las variables:

hora_fecha_d = []
vel_viento_d = []
UV_d = []
temperatura_d = []
humedad_d = []
LDR_d = []
lluvia_d = []

## Inicializacion de variables:

humedad, temperatura = Adafruit_DHT.read_retry(sensor, TH)
temperatura_old = temperatura
humedad_old = humedad

## Toma ciclica de datos:

while True:
    print('*')
    
    ## Lectura velocidad de viento:
    
    count = 0    ## Inicialización de variables
    rps_sum = 0
    rpm_sum = 0
    rps_prom = 0
    rpm_prom = 0
    anterior_input = False
    timeWind = 50
    timeOld = time.monotonic()
    timeStart = timeOld
    pulsos_vuelta = 1    ## Depende de la cantidad de imanes

    while True:
        
        inputValue = GPIO.input(WIND)
        
        if(inputValue == True and anterior_input == False): ## condición con antirebote
            
            count += 1
            ##print(count)
            timeNew = time.monotonic()# time.monotic()
            Dtime = timeNew - timeOld
            ##print("Diferencia entre tiempos de pulso: ",Dtime)
            
            rps = 1/(pulsos_vuelta*Dtime)
            rpm = rps*60
            ##print('RPS: ', rps)
            ##print('RPM: ', rpm)
            
            rps_sum += rps
            rpm_sum += rpm
            
            timeOld = timeNew + 0.04

            time.sleep(0.04)  ## tiempo para antirrebote
        
        anterior_input = inputValue   ## Guardar valor de entrada anterior anterior
        
        timeBucle = time.monotonic() - timeStart
        
        if timeBucle >= timeWind:
            if count > 2:
                rps_prom = rps_sum/count
                rpm_prom = rpm_sum/count
                if rpm_prom > 10000:
                    rpm_prom = 0
            else:
                rps_prom = 0
                rpm_prom = 0
            
            vel_viento_d.append('{: 0.2f}'. format (rpm_prom))  ## Agrega dato a lista de la variable
            
            ##print(timeBucle)
            ##print('RPS promedio: ', rps_prom)
            ##print('RPM promedio: ', rpm_prom)
            
            break
        
    
    ## Lectura rayos UV:
    with busio.I2C(board.SCL, board.SDA) as i2c:
        uv = adafruit_veml6070.VEML6070(i2c)
        
        uv_raw = uv.uv_raw
        risk_level = uv.get_index(uv_raw)
        
        UV_d.append(uv_raw)  ## Agrega dato a lista de la variable
    
    ## Lectura temperatura y humedad relativa:

    humedad, temperatura = Adafruit_DHT.read_retry(sensor, TH)
    
    if humedad is not None and temperatura is not None and abs(temperatura_old - temperatura) < 2: ## Ajuste de error de datos aleatorios
        print('bien T')
        temperatura_old = temperatura
        humedad_old = humedad
    
    else:
        print('mal T')
        ##print('Fallo la lectura del sensor AM2301 - Intentar de nuevo')
        humedad, temperatura = Adafruit_DHT.read_retry(sensor, TH)
        temperatura_old = temperatura
        humedad_old = humedad
    
    temperatura_d.append('{: 0.2f}'. format (temperatura))  ## Agrega dato a lista de la variable
    humedad_d.append('{: 0.2f}'. format (humedad))          ## Agrega dato a lista de la variable
    
    ## Lectura LDR:
    lectura = GPIO.input(LDR)
    if lectura == 1:
        info_ldr = 'Oscuro'
        ldr = 0
    else:
        info_ldr = 'iluminado'
        ldr = 1
    
    LDR_d.append(info_ldr)  ## Agrega dato a lista de la variable
    
    ## Lectura Lluvia:
    lectura = GPIO.input(RAIN)
    if lectura == 1:
        info_rain = 'Seco'
        rain = 0
    else:
        info_rain = 'Precipitación'
        rain = 1
    
    lluvia_d.append(info_rain)  ## Agrega dato a lista de la variable
    
    ## Hora y fecha actual:
    localtime = time.asctime( time.localtime(time.time()) )
    
    hora_fecha_d.append(localtime) ## Agrega dato a lista de la variable
    
    ##DataFrame:
    data = {'Fecha y hora':hora_fecha_d,
            'Velocidad de viento':vel_viento_d,
            'Rayos UV':UV_d,
            'Temperatura':temperatura_d,
            'Humedad relativa':humedad_d,
            'Luz/oscuridad':LDR_d,
            'Lluvia':lluvia_d}
    df = pd.DataFrame(data, columns = ['Fecha y hora',
                                       'Velocidad de viento',
                                       'Rayos UV',
                                       'Temperatura',
                                       'Humedad relativa',
                                       'Luz/oscuridad',
                                       'Lluvia'])
    df.to_csv('DATA.csv')
    
    print(f'Indice UV={uv_raw}, Nivel UV ={risk_level} | Velocidad de viento= {rpm_prom:.2f} | Temperatura={temperatura:.2f}°C | Humedad={humedad:.2f}% | {info_ldr} | {info_rain}')
    enviar = requests.get(f'https://api.thingspeak.com/update?api_key=VEX7N395HLX3Z5RE&field1={temperatura:.2f}&field2={humedad:.2f}&field3={uv_raw}&field4={rpm_prom:.2f}&field5={ldr}&field6={rain}')
    ##print(df)
    time.sleep(10)