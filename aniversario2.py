import os
import urllib.request
import urllib.parse
from datetime import date, timedelta

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

INICIO = date(2026, 3, 17)
hoy = date.today()
manana = hoy + timedelta(days=1)

def enviar_mensaje(texto):
    mensaje = urllib.parse.quote(texto)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
    urllib.request.urlopen(url)

if manana.day == INICIO.day:
    meses_totales = (manana.year - INICIO.year) * 12 + (manana.month - INICIO.month)

    if meses_totales > 0:
        if meses_totales % 12 == 0:
            anios = meses_totales // 12
            texto = f"🎉🩷 ¡Mañana cumplen {anios} año(s) juntos! 🩷🎉"
        else:
            texto = f"💌 Mañana cumplen {meses_totales} meses juntos 🩷"

        enviar_mensaje(texto)
    else:
        print("Aún no ha pasado ni un mes completo.")
else:
    print("Mañana no es día de aniversario, no se envía nada.")
