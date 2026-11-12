# Start am Gerät. Bewusst winzig: alles Weitere liegt im Paket clippy.
import sys

try:
    from clippy import desktop
    desktop.run()
except Exception as e:  # auch der Desktop selbst bleibt nie stumm stehen: Fehler aufs Display und in die Konsole
    sys.print_exception(e)
    import io
    import M5
    from clippy import win98
    out = io.StringIO()
    sys.print_exception(e, out)
    M5.begin()
    win98.bluescreen(M5.Display, "Clippy", out.getvalue())
