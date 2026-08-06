import os
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def enviar_mensaje(texto):
    mensaje = urllib.parse.quote(texto)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
    urllib.request.urlopen(url)


def main():
    texto = "✅ Test message — your bot is connected and working correctly."
    enviar_mensaje(texto)
    print("Mensaje de prueba enviado.")


if __name__ == "__main__":
    main()
