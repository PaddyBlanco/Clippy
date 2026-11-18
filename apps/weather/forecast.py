# Wetter von Open-Meteo (kostenlos, ohne Anmeldung): die Orte, die Abfrage und was aus der Antwort gebraucht wird.
# GPS hat das Gerät nicht, darum stehen die Orte fest hier.

PLACES = (("Eferding", 48.31, 14.02), ("Linz", 48.31, 14.29))  # Name, Breite, Länge
DAYS = ("Heit", "Morgn", "Übermorgn")
URL = ("http://api.open-meteo.com/v1/forecast?latitude=%.2f&longitude=%.2f"
       "&current=temperature_2m,weather_code,is_day"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
       "&timezone=Europe%%2FVienna&forecast_days=3")

# Arten von Wetter und wie man sie sagt; die Zeichen dazu malt icons.py
WORDS = {"sun": "Sunnig", "partly": "A bissl Wolkn", "cloud": "Bewölkt", "fog": "Nebl", "drizzle": "Niesln",
         "rain": "Regn", "snow": "Schnee", "storm": "Gwitter"}
WET = ("drizzle", "rain", "snow", "storm")  # dafür braucht man einen Schirm


def url(place):
    _, lat, lon = place
    return URL % (lat, lon)


def kind(code):
    """WMO-Wettercode (0 bis 99) -> Art aus WORDS. Unbekannt oder None -> "cloud"."""
    if code is None:
        return "cloud"
    if code == 0:
        return "sun"
    if code in (1, 2):
        return "partly"
    if code in (45, 48):
        return "fog"
    if 51 <= code <= 57:
        return "drizzle"
    if 61 <= code <= 67 or 80 <= code <= 82:
        return "rain"
    if 71 <= code <= 77 or code in (85, 86):
        return "snow"
    if code >= 95:
        return "storm"
    return "cloud"


def _at(values, i):
    try:
        return values[i]
    except (TypeError, IndexError, KeyError):
        return None


def parse(data):
    """Antwort von Open-Meteo -> {"now": (Grad, Art, Tag?), "days": [(Name, Art, min, max, Regen %), ...]}.
    Fehlt etwas, steht dort None; ohne brauchbare Antwort ganz None."""
    if not isinstance(data, dict) or "current" not in data:
        return None
    now, daily = data["current"], data.get("daily")
    now, daily = now if isinstance(now, dict) else {}, daily if isinstance(daily, dict) else {}
    days = []
    for i, name in enumerate(DAYS):
        if _at(daily.get("time"), i) is None:
            break
        days.append((name, kind(_at(daily.get("weather_code"), i)), _at(daily.get("temperature_2m_min"), i),
                     _at(daily.get("temperature_2m_max"), i), _at(daily.get("precipitation_probability_max"), i)))
    return {"now": (now.get("temperature_2m"), kind(now.get("weather_code")), now.get("is_day", 1) != 0),
            "days": days, "time": now.get("time")}


def degrees(t):
    """14.9 -> "15°", None -> "?°"."""
    return "?°" if t is None else "%d°" % round(t)
