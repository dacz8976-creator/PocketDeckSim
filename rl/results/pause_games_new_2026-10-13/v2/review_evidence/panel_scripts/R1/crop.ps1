param([string]$TimeList)
$Times = $TimeList.Split(';')
Add-Type -AssemblyName System.Drawing
$src = "C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-12_NEW_LONG_VIDEOS\20261012_010706000_iOS\turn_evidence\"
$out = "C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\panel14\R1\"
foreach ($t in $Times) {
  $img = [System.Drawing.Image]::FromFile($src + "capture_" + $t + "_top.jpg")
  $rect = New-Object System.Drawing.Rectangle 280, 100, 620, 330
  $bmp = New-Object System.Drawing.Bitmap 1240, 660
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $dest = New-Object System.Drawing.Rectangle 0, 0, 1240, 660
  $g.DrawImage($img, $dest, $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $bmp.Save($out + "fan_" + $t + ".png", [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $img.Dispose()
  "saved $t"
}
