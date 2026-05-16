@echo off
chcp 65001 >nul
echo ========================================
echo    IPv6 公网地址检测工具
echo ========================================
echo.

echo [1] 检查IPv6配置...
ipconfig | findstr "IPv6"
echo.

echo [2] 测试IPv6网络连接...
ping -6 -n 4 ipv6.google.com 2>nul
if %errorlevel% equ 0 (
    echo ✓ IPv6网络连接正常
) else (
    echo ✗ IPv6网络不可达
)
echo.

echo [3] 获取本机IPv6地址...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv6" ^| findstr /v "临时 首选"') do (
    echo 检测到的IPv6地址: %%a
)
echo.

echo [4] 测试公网IPv6可达性...
echo 请访问以下网站测试你的IPv6地址：
echo   - https://test-ipv6.com
echo   - https://ipv6-test.com
echo.

echo [5] 检查端口开放情况...
echo 请确保以下端口未被防火墙阻止：
echo   - 80 (HTTP)
echo   - 443 (HTTPS)
echo.

echo ========================================
echo 检测完成！
echo ========================================
pause
