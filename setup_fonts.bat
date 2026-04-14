@echo off
chcp 65001 >nul
echo ============================================================
echo 中文字体设置工具
echo ============================================================
echo.

REM 检查Python是否可用
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] 找到Python，使用脚本下载字体...
    python download_fonts.py
    goto :end
)

echo [INFO] Python未找到，使用系统字体...

REM 创建fonts目录
if not exist "fonts" mkdir fonts

REM 检查Windows系统字体
echo.
echo 尝试从Windows系统复制中文字体...

set FONT_FOUND=0

REM 检查SimHei字体
if exist "C:\Windows\Fonts\simhei.ttf" (
    echo [INFO] 找到SimHei字体
    copy "C:\Windows\Fonts\simhei.ttf" "fonts\" >nul
    if %errorlevel% equ 0 (
        echo [SUCCESS] SimHei字体复制成功
        set FONT_FOUND=1
    ) else (
        echo [ERROR] SimHei字体复制失败
    )
)

REM 检查微软雅黑字体
if %FONT_FOUND% equ 0 (
    if exist "C:\Windows\Fonts\msyh.ttc" (
        echo [INFO] 找到微软雅黑字体
        copy "C:\Windows\Fonts\msyh.ttc" "fonts\msyh.ttc" >nul
        if %errorlevel% equ 0 (
            echo [SUCCESS] 微软雅黑字体复制成功
            set FONT_FOUND=1
        ) else (
            echo [ERROR] 微软雅黑字体复制失败
        )
    )
)

REM 检查宋体
if %FONT_FOUND% equ 0 (
    if exist "C:\Windows\Fonts\simsun.ttc" (
        echo [INFO] 找到宋体字体
        copy "C:\Windows\Fonts\simsun.ttc" "fonts\simsun.ttc" >nul
        if %errorlevel% equ 0 (
            echo [SUCCESS] 宋体字体复制成功
            set FONT_FOUND=1
        ) else (
            echo [ERROR] 宋体字体复制失败
        )
    )
)

echo.
echo ============================================================
if %FONT_FOUND% equ 1 (
    echo ✅ 字体设置完成！
    echo.
    echo 字体文件已复制到 fonts\ 目录
    echo 可以正常使用词云功能
) else (
    echo ❌ 字体设置失败！
    echo.
    echo 请手动下载中文字体：
    echo 1. 下载SimHei字体（黑体）
    echo 2. 将字体文件放入 fonts\ 目录
    echo 3. 确保文件名为 simhei.ttf
    echo.
    echo 字体下载地址：
    echo - 思源黑体: https://github.com/googlefonts/noto-cjk
    echo - 文泉驿微米黑: http://wenq.org/wqy2/index.cgi
)
echo ============================================================
echo.
pause

:end
exit /b 0