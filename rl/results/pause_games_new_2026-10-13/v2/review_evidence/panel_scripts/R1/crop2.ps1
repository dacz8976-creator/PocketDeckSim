param([string]$File, [int]$X, [int]$Y, [int]$W, [int]$H, [string]$Out, [double]$Scale = 1.5)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($File)
$rect = New-Object System.Drawing.Rectangle $X, $Y, $W, $H
$ow = [int]($W * $Scale); $oh = [int]($H * $Scale)
$bmp = New-Object System.Drawing.Bitmap $ow, $oh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$dest = New-Object System.Drawing.Rectangle 0, 0, $ow, $oh
$g.DrawImage($img, $dest, $rect, [System.Drawing.GraphicsUnit]::Pixel)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $img.Dispose()
"saved $Out ($($img.Width)x$($img.Height))"
