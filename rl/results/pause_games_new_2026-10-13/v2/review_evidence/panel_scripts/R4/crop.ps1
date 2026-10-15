param([string]$src, [string]$out, [int]$x0, [int]$y0, [int]$x1, [int]$y1, [double]$scale)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($src)
Write-Output ("size {0}x{1}" -f $img.Width, $img.Height)
$w = $x1 - $x0; $h = $y1 - $y0
$nw = [int]($w * $scale); $nh = [int]($h * $scale)
$bmp = New-Object System.Drawing.Bitmap $nw, $nh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$dest = New-Object System.Drawing.Rectangle 0, 0, $nw, $nh
$srcR = New-Object System.Drawing.Rectangle $x0, $y0, $w, $h
$g.DrawImage($img, $dest, $srcR, [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $img.Dispose()
Write-Output "saved $out"
