param([string]$src, [string]$out, [int]$x0, [int]$y0, [int]$x1, [int]$y1, [double]$scale)
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($src)
$w = $x1 - $x0; $h = $y1 - $y0
$nw = [int]($w * $scale); $nh = [int]($h * $scale)
$bmp = New-Object System.Drawing.Bitmap $nw, $nh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($im, (New-Object System.Drawing.Rectangle 0, 0, $nw, $nh), (New-Object System.Drawing.Rectangle $x0, $y0, $w, $h), [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $im.Dispose()
"saved $out"
