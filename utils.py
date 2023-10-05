
import pandas as pd
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, PHONE_NUMBER, API_KEY_WAPI
from datetime import datetime
import requests

# Función para obtener la fecha actual en el formato deseado
def get_date():
    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")
    return input_date

# Función para hacer una solicitud a la API de WeatherAPI
def request_wapi(api_key, query):
    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key=' + api_key + '&q=' + query + '&days=1&aqi=no&alerts=no'
    
    try:
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)
    
    return response

# Función para obtener los datos de pronóstico de lluvia
def get_forecast(response, i):
    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    tempe = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    
    return fecha, hora, condicion, tempe, rain, prob_rain

# Función para crear un DataFrame con los datos relevantes del pronóstico
def create_df(data):
    col = ['Fecha', 'Hora', 'Condicion', 'Temperatura', 'Lluvia', 'prob_lluvia']
    df = pd.DataFrame(data, columns=col)
    df = df.sort_values(by='Hora', ascending=True)
    
    df_rain = df[(df['Lluvia'] == 1) & (df['Hora'] > 6) & (df['Hora'] < 22)]
    df_rain = df_rain[['Hora', 'Condicion']]
    df_rain.set_index('Hora', inplace=True)
    
    return df_rain

# Función para enviar un mensaje de Twilio con el pronóstico de lluvia o "Hoy no lloverá"
def send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df, query):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    
    client = Client(account_sid, auth_token)
    
    if df.empty:  # Verificamos si el DataFrame está vacío (no hay pronóstico de lluvia)
        message_body = "Hoy no lloverá, no te preocupes hermosa"
    else:
        message_body = f'\nHola!\n\nEl pronóstico de lluvia hoy {input_date} en {query} es:\n\n{df.to_string(index=False)}'
    
    message = client.messages.create(
        body=message_body,
        from_=PHONE_NUMBER,
        to='+525586686270'
    )
    
    return message.sid

# Obtener la fecha actual en el formato deseado
input_date = get_date()

# Realizar una solicitud a la API de WeatherAPI
response = request_wapi(API_KEY_WAPI, 'Ciudad')  # Reemplaza 'Ciudad' con la ciudad deseada

# Crear una lista de pronóstico de lluvia
forecast_data = []
for i in range(24):
    fecha, hora, condicion, tempe, rain, prob_rain = get_forecast(response, i)
    forecast_data.append([fecha, hora, condicion, tempe, rain, prob_rain])

# Crear un DataFrame con los datos del pronóstico
df_forecast = create_df(forecast_data)

# Enviar un mensaje con el pronóstico de lluvia o "Hoy no lloverá"
send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df_forecast, 'Ciudad')