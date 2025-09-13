#!/bin/bash
# setup4host.sh - set up virtual environment, install dependencies and create systemd file
# 确保脚本运行幂等，有更新时保证运行一次脚本就可以满足更新的需要

program_name="oneclickopen"
current_uid=$(id -u)
current_dir=$(pwd)

# 确保存在虚拟环境并安装包
if [ ! -d .env ]
then
    python3 -m venv .env
fi
source .env/bin/activate
pip install -r requirements.txt

# 创建 systemd 配置文件
if [ ! -f ${program_name}.service ]
then
cat > ./${program_name}.service <<EOF
[Unit]
Description=OneClickOpen FastAPI App
After=network.target

[Service]
WorkingDirectory=${current_dir}
User=${current_uid}
Group=${current_uid}
Type=simple
ExecStart=${current_dir}/.env/bin/uvicorn main:app --host 0.0.0.0 --port 7500
ExecStop=/bin/kill -s HUP $MAINPID
Environment=PYTHONUNBUFFERED=1
RestartSec=15
Restart=on-failure

[Install]
WantedBy=default.target
EOF
fi

chmod 644 ${program_name}.service

# vim: expandtab shiftwidth=4 softtabstop=4
