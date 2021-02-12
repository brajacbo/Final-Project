import pandas as pd       ## Pandas

hora_fecha_d = []
vel_viento_d = []
UV_d = []
temperatura_d = []
humedad_d = []
LDR_d = []
lluvia_d = []

cabeceras = {'Fecha y hora':hora_fecha_d,
        'Velocidad de viento':vel_viento_d,
        'Intensidad luz UV':UV_d,
        'Temperatura':temperatura_d,
        'Humedad relativa':humedad_d,
        'Luz/oscuridad':LDR_d,
        'Lluvia':lluvia_d}
df = pd.DataFrame(cabeceras, columns = ['Fecha y hora','Velocidad de viento','Intensidad luz UV','Temperatura','Humedad relativa','Luz/oscuridad','Lluvia'])
df.to_csv('DATA_all.csv')
print(df)