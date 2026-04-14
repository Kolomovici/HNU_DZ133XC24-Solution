# 中文字体设置工具 - PowerShell版本

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "中文字体设置工具" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 创建fonts目录
if (-not (Test-Path "fonts")) {
    New-Item -ItemType Directory -Path "fonts" | Out-Null
    Write-Host "[INFO] 创建fonts目录" -ForegroundColor Green
}

# 检查Python是否可用
$pythonAvailable = $false
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonAvailable = $true
        Write-Host "[INFO] 找到Python: $pythonVersion" -ForegroundColor Green
    }
} catch {
    $pythonAvailable = $false
}

if ($pythonAvailable) {
    Write-Host "[INFO] 使用Python脚本下载字体..." -ForegroundColor Green
    python download_fonts.py
    exit $LASTEXITCODE
}

Write-Host "[INFO] Python未找到，使用系统字体..." -ForegroundColor Yellow
Write-Host ""

# 检查Windows系统字体
$fontFound = $false
$fontPaths = @(
    "C:\Windows\Fonts\simhei.ttf",
    "C:\Windows\Fonts\msyh.ttc",
    "C:\Windows\Fonts\simsun.ttc",
    "C:\Windows\Fonts\msyhbd.ttc"
)

$fontNames = @{
    "simhei.ttf" = "SimHei字体"
    "msyh.ttc" = "微软雅黑字体"
    "simsun.ttc" = "宋体字体"
    "msyhbd.ttc" = "微软雅黑粗体"
}

foreach ($fontPath in $fontPaths) {
    $fontFile = Split-Path $fontPath -Leaf
    if (Test-Path $fontPath) {
        $fontName = $fontNames[$fontFile]
        Write-Host "[INFO] 找到$fontName" -ForegroundColor Green
        
        try {
            Copy-Item $fontPath "fonts\" -Force
            Write-Host "[SUCCESS] $fontName复制成功" -ForegroundColor Green
            $fontFound = $true
            break
        } catch {
            Write-Host "[ERROR] $fontName复制失败: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($fontFound) {
    Write-Host "✅ 字体设置完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "字体文件已复制到 fonts\ 目录" -ForegroundColor White
    Write-Host "可以正常使用词云功能" -ForegroundColor White
    
    # 显示已复制的字体文件
    $fontFiles = Get-ChildItem "fonts\*" -Include *.ttf, *.ttc, *.otf
    if ($fontFiles) {
        Write-Host ""
        Write-Host "已复制的字体文件:" -ForegroundColor Yellow
        foreach ($file in $fontFiles) {
            Write-Host "  - $($file.Name)" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ 字体设置失败！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载中文字体：" -ForegroundColor Yellow
    Write-Host "1. 下载SimHei字体（黑体）" -ForegroundColor White
    Write-Host "2. 将字体文件放入 fonts\ 目录" -ForegroundColor White
    Write-Host "3. 确保文件名为 simhei.ttf" -ForegroundColor White
    Write-Host ""
    Write-Host "字体下载地址：" -ForegroundColor Yellow
    Write-Host "- 思源黑体: https://github.com/googlefonts/noto-cjk" -ForegroundColor White
    Write-Host "- 文泉驿微米黑: http://wenq.org/wqy2/index.cgi" -ForegroundColor White
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 等待用户按键
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

exit 0