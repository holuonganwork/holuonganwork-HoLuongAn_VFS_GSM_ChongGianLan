param(
    [Parameter(Mandatory = $true)][string]$PlantUmlJar,
    [string]$JavaExecutable = 'java',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$jarPath = (Resolve-Path -LiteralPath $PlantUmlJar).Path
$diagramRoot = $PSScriptRoot
$catalog = Get-Content -LiteralPath (Join-Path $diagramRoot 'catalog.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$sourceFiles = @()
foreach ($entry in $catalog) {
    if ($entry.file -notmatch '^[a-z0-9-]+$') { throw "Invalid diagram file name: $($entry.file)" }
    $sourceFiles += (Resolve-Path -LiteralPath (Join-Path $diagramRoot "src/$($entry.file).puml")).Path
}
$javaArgs = @('-Djava.awt.headless=true', '-DPLANTUML_LIMIT_SIZE=16000', '-jar', $jarPath, '-charset', 'UTF-8')
& $JavaExecutable @javaArgs '-checkonly' @sourceFiles
if ($LASTEXITCODE -ne 0) { throw 'PlantUML syntax validation failed.' }
if ($CheckOnly) { Write-Output "Syntax valid: $($catalog.Count) diagrams."; return }
& $JavaExecutable @javaArgs '-tsvg' '-nometadata' '-o' '../svg' @sourceFiles
if ($LASTEXITCODE -ne 0) { throw 'PlantUML SVG rendering failed.' }
$navigation = [System.Collections.Generic.List[string]]::new()
$cards = [System.Collections.Generic.List[string]]::new()
foreach ($entry in $catalog) {
    $svgPath = Join-Path $diagramRoot "svg/$($entry.file).svg"
    if (-not (Test-Path -LiteralPath $svgPath)) { throw "Missing output: $svgPath" }
    $svg = Get-Content -LiteralPath $svgPath -Raw -Encoding UTF8
    if ($svg -match 'Syntax Error|An error has occurred|Cannot find Graphviz') { throw "Renderer error in $svgPath" }
    $id = [System.Net.WebUtility]::HtmlEncode($entry.id)
    $title = [System.Net.WebUtility]::HtmlEncode($entry.title)
    $group = [System.Net.WebUtility]::HtmlEncode($entry.group)
    $file = $entry.file
    $navigation.Add("<a href='#$id'>$id · $title</a>")
    $cards.Add(@"
<article id='$id' data-search='$id $title $group'>
  <div class='heading'><div><p class='group'>$group</p><h2>$id — $title</h2></div>
  <div class='actions'><a href='svg/$file.svg' target='_blank' rel='noopener'>Mở SVG</a><a href='src/$file.puml' download>Nguồn PlantUML</a></div></div>
  <div class='image-wrap'><a href='svg/$file.svg' target='_blank' rel='noopener'><img src='svg/$file.svg' alt='$id — $title' loading='lazy'></a></div>
</article>
"@)
}
$navHtml = $navigation -join "`n"
$cardHtml = $cards -join "`n"
$html = @"
<!doctype html>
<html lang='vi'>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Sơ đồ BA — Điều tra gian lận tài xế</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#172033;font:16px/1.6 Arial,sans-serif}a{color:#1d4ed8}header{padding:30px 40px;background:#fff;border-bottom:1px solid #dbe2ea}h1{font-size:28px;line-height:1.3;margin:0 0 12px}header p{max-width:1000px;margin:8px 0}.layout{display:grid;grid-template-columns:285px minmax(0,1fr);gap:24px;margin:24px}nav{position:sticky;top:16px;align-self:start;max-height:95vh;overflow:auto;background:#fff;border:1px solid #dbe2ea;padding:16px}nav a{display:block;padding:7px 0;font-size:14px;text-decoration:none}input{display:block;width:100%;padding:10px;border:1px solid #64748b;font:inherit;margin:6px 0 14px}article{background:#fff;border:1px solid #cbd5e1;margin-bottom:24px;padding:24px;scroll-margin-top:16px}.heading{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:22px}h2{font-size:21px;line-height:1.4;margin:0}.group{margin:0 0 4px;color:#475569;font-size:13px}.actions{display:flex;gap:16px;font-size:14px;white-space:nowrap}.image-wrap{overflow:auto;border-top:1px solid #e2e8f0;padding-top:18px}.image-wrap img{display:block;max-width:100%;height:auto;margin:auto}#empty{display:none;padding:20px}a:focus-visible,input:focus-visible{outline:3px solid #2563eb;outline-offset:3px}@media(max-width:950px){.layout{grid-template-columns:1fr;margin:12px}nav{position:static;max-height:280px}header{padding:24px}.heading{display:block}.actions{margin-top:12px}article{padding:14px}}@media print{nav,.actions,header input{display:none}.layout{display:block;margin:0}article{break-before:page;border:0}.image-wrap img{max-height:90vh}body{background:#fff}}
</style></head>
<body><header><h1>Sơ đồ BA — Hệ thống điều tra gian lận tài xế</h1>
<p>14 sơ đồ mô tả hệ thống đích phối hợp tài xế–kiểm soát. Mở SVG để phóng to; mỗi hình có nguồn PlantUML đi kèm.</p>
<p><a href='../18-diagram-catalog.md'>Danh mục và truy vết</a> · <a href='../README.md'>Bộ tài liệu BA</a></p></header>
<div class='layout'><nav aria-label='Danh mục sơ đồ'><label for='search'>Tìm sơ đồ</label><input id='search' type='search' placeholder='Mã, tên hoặc nhóm sơ đồ'>
$navHtml
</nav><main><p id='empty' role='status'>Không tìm thấy sơ đồ phù hợp.</p>
$cardHtml
</main></div>
<script>
const field=document.getElementById('search');const cards=[...document.querySelectorAll('article')];const clean=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'d');field.addEventListener('input',()=>{const q=clean(field.value);let count=0;cards.forEach(card=>{const visible=clean(card.dataset.search).includes(q);card.hidden=!visible;if(visible)count++;});document.getElementById('empty').style.display=count?'none':'block';});
</script></body></html>
"@
[System.IO.File]::WriteAllText((Join-Path $diagramRoot 'index.html'), $html, [System.Text.UTF8Encoding]::new($false))
Write-Output "Rendered: $($catalog.Count) SVG diagrams and index.html."
