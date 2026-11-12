# Stürzt absichtlich ab. Zeigt, was bei einem Fehler in einer App passiert: Bluescreen statt Stillstand.
def run(ctx):
    ctx.update()
    return 1 / 0
