import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ============ Markets and their local trading hours ============
MERCADOS = [
    {"nombre": "Sydney (ASX)",    "tz": "Australia/Sydney", "apertura": (10, 0), "cierre": (16, 0),  "bandera": "🇦🇺"},
    {"nombre": "Tokyo (TSE)",     "tz": "Asia/Tokyo",       "apertura": (9, 0),  "cierre": (15, 0),  "bandera": "🇯🇵"},
    {"nombre": "London (LSE)",   "tz": "Europe/London",    "apertura": (8, 0),  "cierre": (16, 30), "bandera": "🇬🇧"},
    {"nombre": "New York (NYSE)", "tz": "America/New_York", "apertura": (9, 30), "cierre": (16, 0),  "bandera": "🇺🇸"},
]

TEXTOS = {
    "abre": "▸ Opens in 5 minutes",
    "cierra": "▸ Closes now",
    "overlap_inicia": "▸ Overlap begins",
    "overlap_finaliza": "▸ Overlap ends",
    "gold": "Gold",
    "sin_precios": "(prices unavailable right now)",
}


def enviar_mensaje(texto):
    mensaje = urllib.parse.quote(texto)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
    urllib.request.urlopen(url)


def obtener_precios():
    """Returns (gold_price, btc_price). Returns (None, None) if the API call fails."""
    try:
        with urllib.request.urlopen("https://xaus.com/api/v1/spot?compact=1", timeout=10) as res:
            datos = json.loads(res.read())
            return datos.get("spot_usd_oz"), datos.get("btc_usd")
    except Exception:
        return None, None


def redondear_abajo_5(dt):
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)


def formatear_precios(oro, btc):
    partes = []
    if oro:
        partes.append(f"🥇  {TEXTOS['gold']}    ${oro:,.2f}")
    if btc:
        partes.append(f"₿   BTC     ${btc:,.0f}")
    return "\n".join(partes) if partes else TEXTOS["sin_precios"]


def mercado_esta_abierto(m, ahora_utc):
    ahora_local = ahora_utc.astimezone(ZoneInfo(m["tz"]))
    if ahora_local.weekday() >= 5:
        return False
    apertura = ahora_local.replace(hour=m["apertura"][0], minute=m["apertura"][1], second=0, microsecond=0)
    cierre = ahora_local.replace(hour=m["cierre"][0], minute=m["cierre"][1], second=0, microsecond=0)
    return apertura <= ahora_local < cierre


def main():
    ahora_utc = datetime.now(ZoneInfo("UTC"))
    oro, btc = obtener_precios()
    precios_texto = formatear_precios(oro, btc)

    londres = next(m for m in MERCADOS if m["tz"] == "Europe/London")
    nueva_york = next(m for m in MERCADOS if m["tz"] == "America/New_York")

    for m in MERCADOS:
        ahora_local = ahora_utc.astimezone(ZoneInfo(m["tz"]))

        if ahora_local.weekday() >= 5:
            continue

        apertura = ahora_local.replace(hour=m["apertura"][0], minute=m["apertura"][1], second=0, microsecond=0)
        cierre = ahora_local.replace(hour=m["cierre"][0], minute=m["cierre"][1], second=0, microsecond=0)
        aviso_apertura = apertura - timedelta(minutes=5)

        ahora_redondeado = redondear_abajo_5(ahora_local)

        if ahora_redondeado == aviso_apertura:
            texto = (
                f"{m['bandera']}  {m['nombre']}\n"
                f"{TEXTOS['abre']}\n"
                f"────────────────\n"
                f"{precios_texto}"
            )
            enviar_mensaje(texto)

        elif ahora_redondeado == cierre:
            texto = (
                f"{m['bandera']}  {m['nombre']}\n"
                f"{TEXTOS['cierra']}\n"
                f"────────────────\n"
                f"{precios_texto}"
            )
            enviar_mensaje(texto)

    # ============ London + New York overlap ============
    ny_local = ahora_utc.astimezone(ZoneInfo(nueva_york["tz"]))
    ny_apertura = ny_local.replace(hour=nueva_york["apertura"][0], minute=nueva_york["apertura"][1], second=0, microsecond=0)
    ny_redondeado = redondear_abajo_5(ny_local)

    londres_local = ahora_utc.astimezone(ZoneInfo(londres["tz"]))
    londres_cierre = londres_local.replace(hour=londres["cierre"][0], minute=londres["cierre"][1], second=0, microsecond=0)
    londres_redondeado = redondear_abajo_5(londres_local)

    etiqueta_overlap = "London + New York"

    if ny_local.weekday() < 5 and ny_redondeado == ny_apertura and mercado_esta_abierto(londres, ahora_utc):
        texto = (
            f"🇬🇧 🇺🇸  {etiqueta_overlap}\n"
            f"{TEXTOS['overlap_inicia']}\n"
            f"────────────────\n"
            f"{precios_texto}"
        )
        enviar_mensaje(texto)

    if londres_local.weekday() < 5 and londres_redondeado == londres_cierre and mercado_esta_abierto(nueva_york, ahora_utc):
        texto = (
            f"🇬🇧 🇺🇸  {etiqueta_overlap}\n"
            f"{TEXTOS['overlap_finaliza']}\n"
            f"────────────────\n"
            f"{precios_texto}"
        )
        enviar_mensaje(texto)


if __name__ == "__main__":
    main()
