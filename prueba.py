import os
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def enviar_mensaje(texto):
    mensaje = urllib.parse.quote(texto)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
    urllib.request.urlopen(url)

enviar_mensaje("✅ Prueba: el bot de aniversario sí está conectado correctamente")
