// Fotos für die Diashow verkleinern: im Browser, die Fotos verlassen den Rechner nicht.
// Jedes Foto wird so verkleinert, dass es ganz in 320 x 218 passt, und als normales (nicht progressives) JPEG
// gespeichert: direkt in einen Ordner auf der Karte (Chrome, Edge) oder als ZIP-Datei. Videos bleiben weg.
"use strict";
var W = 320, H = 218, QUALITY = 0.85, FOLDER = "Clippy-Bilder";

function cleanName(name, taken) {
  // Dateiname ohne Endung, nur einfache Zeichen, dazu .jpg; doppelte bekommen _2, _3, ...
  var base = name.replace(/\.[^.]*$/, "").replace(/[^A-Za-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "") || "bild";
  var out = base + ".jpg", n = 2;
  while (taken[out.toLowerCase()]) out = base + "_" + n++ + ".jpg";
  taken[out.toLowerCase()] = true;
  return out;
}

var CRC = [];
for (var c, i = 0; i < 256; i++) {
  c = i;
  for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
  CRC[i] = c >>> 0;
}

function crc32(bytes) {
  var c = 0xFFFFFFFF;
  for (var i = 0; i < bytes.length; i++) c = CRC[(c ^ bytes[i]) & 255] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

function makeZip(files) {
  // files: [{name, bytes: Uint8Array}] -> Uint8Array einer ZIP-Datei ohne Kompression (JPEGs sind schon klein)
  var parts = [], central = [], offset = 0;
  function head(sig, extra) {
    var h = new DataView(new ArrayBuffer(extra));
    h.setUint32(0, sig, true);
    return h;
  }
  files.forEach(function (f) {
    var name = new TextEncoder().encode(f.name), crc = crc32(f.bytes), n = f.bytes.length;
    var local = head(0x04034b50, 30);
    [[4, 20], [6, 0x0800], [8, 0], [10, 0], [12, 0x21]].forEach(function (p) { local.setUint16(p[0], p[1], true); });
    local.setUint32(14, crc, true); local.setUint32(18, n, true); local.setUint32(22, n, true);
    local.setUint16(26, name.length, true); local.setUint16(28, 0, true);
    var dir = head(0x02014b50, 46);
    [[4, 20], [6, 20], [8, 0x0800], [10, 0], [12, 0], [14, 0x21]].forEach(function (p) { dir.setUint16(p[0], p[1], true); });
    dir.setUint32(16, crc, true); dir.setUint32(20, n, true); dir.setUint32(24, n, true);
    dir.setUint16(28, name.length, true); dir.setUint32(42, offset, true);
    parts.push(new Uint8Array(local.buffer), name, f.bytes);
    central.push(new Uint8Array(dir.buffer), name);
    offset += 30 + name.length + n;
  });
  var size = central.reduce(function (s, p) { return s + p.length; }, 0);
  var end = head(0x06054b50, 22);
  end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, size, true); end.setUint32(16, offset, true);
  var all = parts.concat(central, [new Uint8Array(end.buffer)]);
  var out = new Uint8Array(all.reduce(function (s, p) { return s + p.length; }, 0)), at = 0;
  all.forEach(function (p) { out.set(p, at); at += p.length; });
  return out;
}

function load(file) {
  // Foto öffnen; ältere Safari kennen createImageBitmap (mit Drehung) nicht, dann über ein <img>
  function viaImg() {
    return new Promise(function (ok, no) {
      var img = new Image();
      img.onload = function () { ok(img); };
      img.onerror = no;
      img.src = URL.createObjectURL(file);
    });
  }
  if (!window.createImageBitmap) return viaImg();
  return createImageBitmap(file, { imageOrientation: "from-image" }).catch(viaImg);
}

function shrink(file) {
  // Foto -> Blob mit einem JPEG, das ganz in W x H passt; die Drehung aus der Kamera wird beachtet
  return load(file).then(function (pic) {
    var k = Math.min(W / pic.width, H / pic.height, 1);
    var canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(pic.width * k));
    canvas.height = Math.max(1, Math.round(pic.height * k));
    var g = canvas.getContext("2d");
    g.imageSmoothingQuality = "high";
    g.drawImage(pic, 0, 0, canvas.width, canvas.height);
    return new Promise(function (done) { canvas.toBlob(done, "image/jpeg", QUALITY); });
  });
}

function start() {
  var input = document.getElementById("photos"), list = document.getElementById("list");
  var toCard = document.getElementById("tocard"), toZip = document.getElementById("tozip");
  var ready = [];
  if (!window.showDirectoryPicker) toCard.style.display = "none";  // nur Chrome und Edge können direkt speichern
  function line(text, bad) {
    var li = document.createElement("li");
    li.textContent = text;
    if (bad) li.className = "bad";
    list.appendChild(li);
  }
  input.onchange = function () {
    var files = Array.prototype.slice.call(input.files), taken = {};
    ready = []; list.innerHTML = ""; toCard.disabled = toZip.disabled = true;
    files.reduce(function (chain, f) {
      return chain.then(function () {
        if (!/^image\//.test(f.type)) return line(f.name + ": kein Foto, bleibt weg", true);
        return shrink(f).then(function (blob) { return blob.arrayBuffer(); }).then(function (buf) {
          var name = cleanName(f.name, taken);
          ready.push({ name: name, bytes: new Uint8Array(buf) });
          line(f.name + " → " + name + " (" + Math.round(buf.byteLength / 1024) + " KB)");
        }, function () { line(f.name + ": kann dieser Browser nicht öffnen", true); });
      });
    }, Promise.resolve()).then(function () {
      line(ready.length + " von " + files.length + " fertig.");
      toCard.disabled = toZip.disabled = ready.length === 0;
    });
  };
  toZip.onclick = function () {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([makeZip(ready)], { type: "application/zip" }));
    a.download = "clippy-bilder.zip";
    a.click();
  };
  toCard.onclick = async function () {
    // nur Chrome und Edge; die kennen auch async. Was schon auf der Karte liegt, wird nie überschrieben.
    try {
      var card = await window.showDirectoryPicker({ mode: "readwrite" });
      var dir = await card.getDirectoryHandle(FOLDER, { create: true }), there = {};
      for await (var name of dir.keys()) there[name.toLowerCase()] = true;
      for (var i = 0; i < ready.length; i++) {
        var free = cleanName(ready[i].name, there);  // gleicher Name schon da: _2, _3, ...
        var w = await (await dir.getFileHandle(free, { create: true })).createWritable();
        await w.write(ready[i].bytes);
        await w.close();
      }
      line(ready.length + " Bilder im Ordner " + FOLDER + " gespeichert.");
    } catch (e) {
      if (e.name !== "AbortError") line("Speichern ging nicht: " + e.message, true);
    }
  };
}

if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", start);
if (typeof module !== "undefined") module.exports = { makeZip: makeZip, cleanName: cleanName, crc32: crc32 };
