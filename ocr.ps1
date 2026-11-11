Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics,ContentType=WindowsRuntime]
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'})[0]
function Await($op,$t){$m=$asTask.MakeGenericMethod($t);$tk=$m.Invoke($null,@($op));$tk.Wait()|Out-Null;$tk.Result}
$null=[Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime]; $lang=[Windows.Globalization.Language]::new('es-MX')
$eng=[Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
$out=@()
foreach($f in (Get-ChildItem C:\Users\surre\Desktop\quiz\pages\*.png|Sort-Object Name)){
 $file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
 $st=Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
 $dec=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($st)) ([Windows.Graphics.Imaging.BitmapDecoder])
 $bmp=Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
 $r=Await ($eng.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
 foreach($l in $r.Lines){$w=($l.Words|Select-Object -First 1).BoundingRect;$out+=("{0}|{1}|{2}|{3}|{4}" -f $f.BaseName,[int]$w.X,[int]$w.Y,[int]$w.Height,$l.Text)}
}
[IO.File]::WriteAllLines('C:\Users\surre\Desktop\quiz\ocrbox.txt',$out,(New-Object Text.UTF8Encoding $false))
'done'



