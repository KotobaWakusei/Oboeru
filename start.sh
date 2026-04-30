#!/bin/bash
# 智能背单词系统启动脚本

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 启动应用
python3 app.py "$@"
