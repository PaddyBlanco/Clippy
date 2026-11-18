# microSD-Karte: einbinden, wenn eine App sie braucht (ctx.sd), und die geteilten Leitungen umschalten.
# Karte und Display teilen sich G35, G36, G37, hängen aber an verschiedenen SPI-Einheiten. Das Einbinden verdrahtet
# die Leitungen auf die Karte um, dann bleibt das Display stehen. Darum: jeder Kartenzugriff in `with access():`,
# danach gehören die Leitungen wieder dem Display (docs/device.md). Nur FAT16/FAT32.
import os

try:
    from machine import SDCard, mem32
except ImportError:  # am PC (Vorschau)
    SDCard = None

PATH = "/sd"
PINS = (35, 36, 37)           # DC/MISO, Takt, Daten
OUT_SEL = 0x60004554          # GPIO_FUNCn_OUT_SEL_CFG_REG im ESP32-S3, je Anschluss 4 Bytes weiter
EN1, EN1_SET, EN1_CLEAR = 0x6000402C, 0x60004030, 0x60004034  # Ausgang an/aus für Anschlüsse ab 32
_card = [None]      # die eingebundene Karte, bis sie fehlt
_wiring = {}        # "display" und "card": je [(Anschluss, Signal, Ausgang an)]


def _snap():
    return [(p, mem32[OUT_SEL + 4 * p], bool(mem32[EN1] & (1 << (p - 32)))) for p in PINS]


def _wire(who):
    for p, signal, on in _wiring.get(who, ()):
        mem32[OUT_SEL + 4 * p] = signal
        mem32[EN1_SET if on else EN1_CLEAR] = 1 << (p - 32)


class _Access:
    """with access(): Leitungen gehören der Karte; danach wieder dem Display. Darin nicht zeichnen."""
    def __enter__(self):
        _wire("card")

    def __exit__(self, *exc):
        _wire("display")


_ACCESS = _Access()


def access():
    return _ACCESS


def mount():
    """Ordner der Karte, oder None ohne Karte oder mit falschem Format (z. B. exFAT). Danach gehören die Leitungen
    wieder dem Display."""
    if SDCard is None:
        return None
    if _card[0] is not None:
        try:
            with _ACCESS:
                os.listdir(PATH)
            return PATH
        except OSError:  # herausgezogen oder getauscht: lösen und neu versuchen
            _release()
    _wiring["display"] = _snap()  # so, wie das Display die Leitungen gerade braucht
    try:
        _card[0] = SDCard(slot=2, width=1, sck=36, miso=35, mosi=37, cs=4, freq=20000000)
        os.mount(_card[0], PATH)
        _wiring["card"] = _snap()
        return PATH
    except OSError:
        _release()
        return None
    finally:
        _wire("display")


def _release():
    try:
        os.umount(PATH)
    except OSError:
        pass
    if _card[0] is not None:
        _card[0].deinit()  # sonst scheitert das nächste SDCard mit EIO
        _card[0] = None
    _wire("display")
