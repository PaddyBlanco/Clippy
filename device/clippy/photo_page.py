# Die Seite, die das Handy beim Scannen des QR-Codes in der Diashow bekommt: Fotos auswählen, im Handy auf
# 320 × 218 verkleinern (wie manual/bilder.js) und einzeln an Clippy schicken. Videos bleiben weg.

PAGE = """<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Fotos an Clippy</title>
<style>
body{margin:0;padding:10px;background:#008080;font-family:Tahoma,Verdana,sans-serif;font-size:17px}
.w{max-width:480px;margin:0 auto;background:#c0c0c0;border:3px outset #fff}
.t{background:linear-gradient(90deg,#000080,#1084d0);color:#fff;font-weight:bold;padding:4px 8px}
.c{padding:12px}
label,button{display:block;width:100%;box-sizing:border-box;min-height:52px;margin:8px 0;font-size:18px;
background:#c0c0c0;border:3px outset #fff;text-align:center;line-height:46px;font-family:inherit}
input{display:none}ul{background:#fff;border:2px inset #c0c0c0;padding:6px 6px 6px 26px;font-size:15px}
.bad{color:#a00000}
</style></head><body><div class="w"><div class="t">Fotos an Clippy</div><div class="c">
<p>Such dir Fotos aus. Dein Handy macht sie klein und schickt sie an Clippy. Videos bleiben weg.</p>
<label for="f">Fotos auswählen</label><input type="file" id="f" accept="image/*" multiple>
<ul id="l"><li>Noch nix geschickt.</li></ul></div></div>
<script>
var K = "{K}", W = 320, H = 218, list = document.getElementById("l"), sent = 0;
function line(t, bad) {
  var li = document.createElement("li"); li.textContent = t; if (bad) li.className = "bad"; list.appendChild(li);
}
function load(file) {
  function viaImg() {
    return new Promise(function (ok, no) {
      var img = new Image(); img.onload = function () { ok(img); }; img.onerror = no;
      img.src = URL.createObjectURL(file);
    });
  }
  if (!window.createImageBitmap) return viaImg();
  return createImageBitmap(file, {imageOrientation: "from-image"}).catch(viaImg);  // ältere Safari
}
function shrink(file) {
  return load(file).then(function (pic) {
    var k = Math.min(W / pic.width, H / pic.height, 1), c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(pic.width * k)); c.height = Math.max(1, Math.round(pic.height * k));
    var g = c.getContext("2d"); g.imageSmoothingQuality = "high"; g.drawImage(pic, 0, 0, c.width, c.height);
    return new Promise(function (done) { c.toBlob(done, "image/jpeg", 0.85); });
  });
}
document.getElementById("f").onchange = function (e) {
  var files = Array.prototype.slice.call(e.target.files);
  list.innerHTML = "";
  files.reduce(function (chain, f) {
    return chain.then(function () {
      if (!/^image\\//.test(f.type)) return line(f.name + ": kein Foto, bleibt weg", true);
      return shrink(f).then(function (blob) {
        return fetch("/photo?k=" + K + "&n=" + encodeURIComponent(f.name), {method: "POST", body: blob});
      }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        sent++; line("\\u2713 " + f.name);
      }).catch(function () { line(f.name + ": hat nicht geklappt", true); });
    });
  }, Promise.resolve()).then(function () { line(sent + " Fotos bei Clippy. Du kannst noch mehr schicken."); });
};
</script></body></html>"""

WRONG = """<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Clippy</title></head>
<body style="font-family:sans-serif;padding:20px">Bitte den QR-Code am Clippy scannen: Diashow, Mitte antippen.
</body></html>"""


def page(token):
    """HTML-Seite fürs Handy; token ist die Geheimzahl aus dem QR-Code."""
    return PAGE.replace("{K}", token).encode()  # nicht mit %: das CSS enthält selbst Prozentzeichen
