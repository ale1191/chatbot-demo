@echo off
echo ======================================
echo    Chatbot-Demo 启动脚本正在执行...
echo ======================================

:: 检查并安装依赖
if exist "requirements.txt" (
    echo 正在检查并安装依赖包...
    pip install -r requirements.txt -q
    echo 依赖包检查完毕！
) else (
    echo 未找到 requirements.txt，跳过依赖检查。
)

:: 检查并复制环境变量文件
if not exist ".env" (
    if exist ".env.example" (
        echo 未找到 .env 文件，正在从 .env.example 复制...
        copy .env.example .env
        echo 请编辑 .env 文件，配置好你的 API Key 后再运行本脚本！
        pause
        exit /b 1
    )
) else (
    echo 环境变量 .env 已就绪。
)

:: 启动后端和前端
echo 正在启动项目...
start "Chatbot-Backend" cmd /k python backend.py
start "Chatbot-Frontend" cmd /k python frontend.py

echo ======================================
echo    项目已启动！请前往浏览器访问。
echo ======================================
pause