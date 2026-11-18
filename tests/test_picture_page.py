"""Selbsttest am PC: python tests/test_picture_page.py
Die Handbuch-Seite bilder.html: Dateinamen für die Karte und die ZIP-Datei aus manual/bilder.js.
Braucht Node.js; ohne Node wird der Test übersprungen."""
import base64
import io
import json
import os
import shutil
import subprocess
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPT = os.path.abspath(os.path.join(ROOT, "manual", "bilder.js")).replace("\\", "/")

if not shutil.which("node"):
    print("übersprungen: kein Node.js")
    raise SystemExit

JS = """
const b = require(%s);
const taken = {};
const names = ["IMG_0001.HEIC", "img_0001.jpg", "Foto vom Grillen (2).jpeg", "äöü.png", ".jpg", "a.b.c.JPG"]
  .map(n => b.cleanName(n, taken));
const files = [{name: names[0], bytes: Uint8Array.from([255, 216, 1, 2, 3, 255, 217])},
               {name: names[2], bytes: new TextEncoder().encode("Hallo Clippy")}];
const zip = b.makeZip(files);
process.stdout.write(JSON.stringify({names, crc: b.crc32(new TextEncoder().encode("123456789")),
                                     zip: Buffer.from(zip).toString("base64")}));
""" % json.dumps(SCRIPT)

out = json.loads(subprocess.run(["node", "-e", JS], capture_output=True, text=True, check=True).stdout)
assert out["names"] == ["IMG_0001.jpg", "img_0001_2.jpg", "Foto_vom_Grillen_2.jpg", "bild.jpg", "bild_2.jpg",
                        "a_b_c.jpg"], out["names"]
assert out["crc"] == 0xCBF43926  # Prüfwert von CRC-32 für "123456789"

z = zipfile.ZipFile(io.BytesIO(base64.b64decode(out["zip"])))
assert z.testzip() is None  # Prüfsummen stimmen
assert z.namelist() == ["IMG_0001.jpg", "Foto_vom_Grillen_2.jpg"]
assert z.read("IMG_0001.jpg") == bytes([255, 216, 1, 2, 3, 255, 217])
assert z.read("Foto_vom_Grillen_2.jpg") == b"Hallo Clippy"
print("ok")
