import os
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, PHONE_NUMBER, API_KEY_WAPI
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import requests
from tqdm import tqdm  # Barra de progreso visual
from datetime import datetime
from utils import request_wapi, get_forecast, create_df, send_message, get_date  # Importación de funciones personalizadas

# Ciudad y clave de la API del clima
query = 'cuajimalpa'  # Reemplaza 'cuajimalpa' con la ciudad de tu elección
api_key = API_KEY_WAPI  # Clave de la API del clima

# Obtiene la fecha actual en el formato deseado
input_date = get_date()

# Realiza una solicitud a la API del clima
response = request_wapi(api_key, query)

datos = []

# Recopila los datos del pronóstico para las próximas 24 horas
for i in tqdm(range(24), colour='green'):  # Barra de progreso visual
    datos.append(get_forecast(response, i))

# Crea un DataFrame con los datos de pronóstico de lluvia
df_rain = create_df(datos)

# Envía un mensaje de Twilio con el pronóstico de lluvia o "Hoy no lloverá"
message_id = send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df_rain, query)

# Imprime un mensaje de éxito
print('Mensaje Enviado con éxito ' + message_id)