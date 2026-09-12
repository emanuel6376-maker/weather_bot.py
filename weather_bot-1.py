import os
import requests
from datetime import datetime

# CAPE bot for Discord + Open-Meteo
# Configure the DISCORD_WEBHOOK_URL environment variable with your Discord webhook.
LAT = -23.9828       # Itapeva-SP
LON = -48.8756

URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LAT,
    "longitude": LON,
    "current": "temperature_2m,dew_point_2m,wind_speed_10m",
    "hourly": "cape,cin,temperature_2m,dew_point_2m,wind_speed_10m",
    "forecast_days": 1,
    "timezone": "America/Sao_Paulo"
}

def main():
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("DISCORD_WEBHOOK_URL não foi configurado.")

    data = requests.get(URL, params=params, timeout=20).json()

    times = data["hourly"]["time"]
    current_time = data["current"]["time"]

    # Escolhe a hora mais próxima do horário atual.
    idx = min(range(len(times)), key=lambda i: abs(
        datetime.fromisoformat(times[i]) - datetime.fromisoformat(current_time)
    ))

    cape = data["hourly"]["cape"][idx]
    cin = data["hourly"]["cin"][idx]
    temp = data["current"]["temperature_2m"]
    dew = data["current"]["dew_point_2m"]
    wind = data["current"]["wind_speed_10m"]

    if cape is None:
        cape_text = "indisponível"
        level = "⚪ Sem dados"
    else:
        cape_text = f"{cape:.0f} J/kg"
        if cape < 500:
            level = "🟢 Baixo"
        elif cape < 1000:
            level = "🟡 Moderado"
        elif cape < 2000:
            level = "🟠 Alto"
        elif cape < 3000:
            level = "🔴 Muito alto"
        else:
            level = "🟣 Extremamente alto"

    message = (
        "🌩️ **CONDIÇÕES CONVECTIVAS — ITAPEVA/SP**\n"
        f"⚡ **CAPE:** {cape_text}\n"
        f"🧊 **CIN:** {cin:.0f} J/kg\n"
        f"🌡️ **Temperatura:** {temp:.1f} °C\n"
        f"💧 **Ponto de orvalho:** {dew:.1f} °C\n"
        f"🌬️ **Vento:** {wind:.1f} km/h\n"
        f"📊 **Potencial convectivo:** {level}\n\n"
        "Fonte: Open-Meteo"
    )

    response = requests.post(webhook, json={"content": message}, timeout=20)
    response.raise_for_status()

if __name__ == "__main__":
    main()
