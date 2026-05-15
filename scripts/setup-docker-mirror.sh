#!/bin/bash
# Docker镜像加速器配置脚本
# 用于解决中国大陆访问Docker Hub网络问题

set -e

echo "=========================================="
echo "Docker镜像加速器配置工具"
echo "=========================================="
echo ""

# 检测操作系统
if [ -f "/proc/version" ] && grep -qi microsoft /proc/version; then
    OS_TYPE="WSL"
    echo "检测到: WSL (Windows Subsystem for Linux)"
elif [ "$(uname)" == "Darwin" ]; then
    OS_TYPE="macOS"
    echo "检测到: macOS"
else
    OS_TYPE="Linux"
    echo "检测到: Linux"
fi

echo ""
echo "注意: 此脚本将指导你配置Docker镜像加速器"
echo "对于WSL用户，需要在Windows Docker Desktop中配置"
echo ""

# 可用的镜像源列表
MIRROR_SOURCES=(
    "https://docker.m.daocloud.io"
    "https://huecker.io"
    "https://dockerhub.timeweb.cloud"
    "https://registry.docker-cn.com"
)

echo "推荐的镜像源:"
for i in "${!MIRROR_SOURCES[@]}"; do
    echo "  $((i+1)). ${MIRROR_SOURCES[$i]}"
done
echo ""

# 创建Docker daemon配置文件
DOCKER_DAEMON_CONFIG="$HOME/.docker/daemon.json"

if [ "$OS_TYPE" == "WSL" ]; then
    echo "=========================================="
    echo "WSL用户配置说明"
    echo "=========================================="
    echo ""
    echo "由于你使用的是WSL，Docker Desktop运行在Windows环境中。"
    echo "你需要在Windows的Docker Desktop中配置镜像加速器。"
    echo ""
    echo "步骤如下:"
    echo ""
    echo "1. 打开 Docker Desktop (Windows)"
    echo "2. 点击右上角 Settings (⚙️)"
    echo "3. 左侧选择 'Docker Engine'"
    echo "4. 在JSON配置中添加以下内容:"
    echo ""
    echo '{'
    echo '  "builder": {'
    echo '    "gc": {'
    echo '      "defaultKeepStorage": "20GB",'
    echo '      "enabled": true'
    echo '    }'
    echo '  },'
    echo '  "experimental": false,'
    echo '  "registry-mirrors": ['
    echo '    "https://docker.m.daocloud.io",'
    echo '    "https://huecker.io",'
    echo '    "https://dockerhub.timeweb.cloud"'
    echo '  ]'
    echo '}'
    echo ""
    echo "5. 点击 'Apply & restart'"
    echo "6. 等待Docker重启完成"
    echo "7. 回到WSL重新运行测试脚本"
    echo ""
    echo "=========================================="
    echo "验证配置是否生效"
    echo "=========================================="
    echo ""
    echo "配置完成后，在WSL中运行以下命令验证:"
    echo ""
    echo "  docker info | grep -i mirror"
    echo ""
    echo "如果看到镜像源列表，说明配置成功。"
    echo ""

    # 尝试自动检测Docker Desktop配置
    if command -v powershell.exe &> /dev/null; then
        echo "=========================================="
        echo "使用PowerShell自动配置（可选）"
        echo "=========================================="
        echo ""
        echo "你也可以使用以下PowerShell命令自动配置（需要在Windows PowerShell中运行）:"
        echo ""
        cat << 'POWERSHELL_EOF'
# 在Windows PowerShell中运行此脚本
$dockerConfigPath = "$env:USERPROFILE\.docker\daemon.json"

# 创建或读取现有配置
if (Test-Path $dockerConfigPath) {
    $config = Get-Content $dockerConfigPath | ConvertFrom-Json
} else {
    $config = @{}
}

# 添加镜像加速器
$config.'registry-mirrors' = @(
    "https://docker.m.daocloud.io",
    "https://huecker.io",
    "https://dockerhub.timeweb.cloud"
)

# 保存配置
$config | ConvertTo-Json -Depth 10 | Set-Content $dockerConfigPath

Write-Host "配置已保存到: $dockerConfigPath"
Write-Host "请重启Docker Desktop使配置生效"
POWERSHELL_EOF
        echo ""
    fi

elif [ "$OS_TYPE" == "Linux" ]; then
    echo "=========================================="
    echo "Linux用户自动配置"
    echo "=========================================="
    echo ""

    # 检查是否有root权限
    if [ "$EUID" -ne 0 ]; then
        echo "需要root权限来配置Docker daemon"
        echo "请使用 sudo 运行此脚本"
        echo ""
        echo "  sudo $0"
        echo ""
        exit 1
    fi

    # 创建配置目录
    mkdir -p /etc/docker

    # 备份现有配置
    if [ -f "/etc/docker/daemon.json" ]; then
        cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d%H%M%S)
        echo "已备份现有配置到 daemon.json.backup.*"
    fi

    # 创建新的配置文件
    cat > /etc/docker/daemon.json << 'EOF'
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://huecker.io",
    "https://dockerhub.timeweb.cloud"
  ]
}
EOF

    echo "配置文件已创建: /etc/docker/daemon.json"
    echo ""
    echo "重启Docker服务..."

    # 根据系统类型重启Docker
    if command -v systemctl &> /dev/null; then
        systemctl restart docker
        echo "Docker服务已重启 (systemctl)"
    elif command -v service &> /dev/null; then
        service docker restart
        echo "Docker服务已重启 (service)"
    else
        echo "请手动重启Docker服务"
    fi

    echo ""
    echo "验证配置..."
    sleep 2
    docker info | grep -A 5 "Registry Mirrors" || echo "配置可能未生效，请检查Docker日志"

elif [ "$OS_TYPE" == "macOS" ]; then
    echo "=========================================="
    echo "macOS用户配置说明"
    echo "=========================================="
    echo ""
    echo "在macOS上，你需要通过Docker Desktop应用配置:"
    echo ""
    echo "1. 打开 Docker Desktop"
    echo "2. 点击顶部菜单栏 Docker 图标 → Settings"
    echo "3. 选择 'Docker Engine'"
    echo "4. 添加以下配置:"
    echo ""
    echo '{'
    echo '  "registry-mirrors": ['
    echo '    "https://docker.m.daocloud.io",'
    echo '    "https://huecker.io",'
    echo '    "https://dockerhub.timeweb.cloud"'
    echo '  ]'
    echo '}'
    echo ""
    echo "5. 点击 'Apply & restart'"
    echo ""
fi

echo ""
echo "=========================================="
echo "配置完成后的测试步骤"
echo "=========================================="
echo ""
echo "1. 确保Docker正在运行:"
echo "   docker ps"
echo ""
echo "2. 测试拉取镜像:"
echo "   docker pull hello-world"
echo ""
echo "3. 运行项目测试脚本:"
echo "   ./scripts/run-all-tests.sh"
echo ""
echo "=========================================="
echo "故障排查"
echo "=========================================="
echo ""
echo "如果仍然无法连接Docker Hub，尝试:"
echo ""
echo "1. 检查网络连接"
echo "   ping registry-1.docker.io"
echo ""
echo "2. 检查Docker代理设置"
echo "   docker info | grep -i proxy"
echo ""
echo "3. 尝试其他镜像源（修改daemon.json）"
echo ""
echo "4. 查看Docker日志:"
echo "   Windows: %USERPROFILE%\\AppData\\Local\\Docker\\log.txt"
echo "   Linux: journalctl -u docker.service"
echo "   macOS: ~/Library/Containers/com.docker.docker/Data/log/"
echo ""
echo "=========================================="
echo "更多信息"
echo "=========================================="
echo ""
echo "项目文档: README.md"
echo "测试指南: DEVELOPER_TESTING_GUIDE.md"
echo "快速参考: QUICK_REFERENCE.md"
echo ""
