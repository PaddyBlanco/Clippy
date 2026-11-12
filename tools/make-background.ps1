# Makes a 320x240 desktop background for the device from any picture.
# Crops to 4:3 around the centre, then tones the colours down.
#   .\tools\make-background.ps1 -Source Assets\desktop-background.jpg -Out local\bg\bg.jpg
# Saturation: 1 = original colours, 0 = grey.  Contrast: 1 = original, lower = flatter.
# Lift: 0 = unchanged, higher = brighter and more washed out.
param(
    [Parameter(Mandatory)] [string] $Source,
    [Parameter(Mandatory)] [string] $Out,
    [double] $Saturation = 0.75,
    [double] $Contrast = 1.0,
    [double] $Lift = 0.0
)
Add-Type -AssemblyName System.Drawing

$src = [System.Drawing.Image]::FromFile((Resolve-Path $Source))
$cropW = [Math]::Min($src.Width, [int]($src.Height * 4 / 3))
$cropH = [Math]::Min($src.Height, [int]($src.Width * 3 / 4))
$crop = New-Object System.Drawing.Rectangle (($src.Width - $cropW) / 2), (($src.Height - $cropH) / 2), $cropW, $cropH

# Saturation matrix (luminance weights), scaled by contrast, shifted by lift
$s = $Saturation; $c = $Contrast
$r = 0.3086 * (1 - $s); $g = 0.6094 * (1 - $s); $b = 0.0820 * (1 - $s)
$m = New-Object System.Drawing.Imaging.ColorMatrix
$m.Matrix00 = ($r + $s) * $c; $m.Matrix01 = $r * $c;        $m.Matrix02 = $r * $c
$m.Matrix10 = $g * $c;        $m.Matrix11 = ($g + $s) * $c; $m.Matrix12 = $g * $c
$m.Matrix20 = $b * $c;        $m.Matrix21 = $b * $c;        $m.Matrix22 = ($b + $s) * $c
$m.Matrix40 = $Lift;          $m.Matrix41 = $Lift;          $m.Matrix42 = $Lift
$attr = New-Object System.Drawing.Imaging.ImageAttributes
$attr.SetColorMatrix($m)

$dst = New-Object System.Drawing.Bitmap 320, 240
$gfx = [System.Drawing.Graphics]::FromImage($dst)
$gfx.InterpolationMode = 'HighQualityBicubic'
$gfx.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, 320, 240),
    $crop.X, $crop.Y, $crop.Width, $crop.Height, 'Pixel', $attr)

$outPath = Join-Path (Get-Location) $Out
New-Item -ItemType Directory -Force (Split-Path $outPath) | Out-Null
$jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
$quality = New-Object System.Drawing.Imaging.EncoderParameters 1
$quality.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 90L
$dst.Save($outPath, $jpeg, $quality)
$gfx.Dispose(); $dst.Dispose(); $src.Dispose()
"{0}: {1} bytes" -f $Out, (Get-Item $outPath).Length
