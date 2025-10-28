#!/bin/bash
set -e

WORK_DIR="/tmp"
LOG_FILE="$WORK_DIR/logs/entrypoint.log"

log() {
  echo "[$(date '+%F %T')] $1" | tee -a "$LOG_FILE"
}

log "🚀 启动 entrypoint.sh"

# 生成导航页（appuser）
if [ -f /tmp/navpage/generate_nav.py ]; then
  log "[INFO] 执行 generate_nav.py（appuser）"
  su -s /bin/bash appuser -c "python3 /tmp/navpage/generate_nav.py" && log "[OK] 导航页生成完成"
else
  log "[SKIP] 未找到 generate_nav.py"
fi

# 更新 hosts（appuser）
if [ -x /tmp/update_hosts.sh ]; then
  log "[INFO] 执行 update_hosts.sh（appuser）"
  su -s /bin/bash appuser -c "/tmp/update_hosts.sh" && log "[OK] hosts 更新完成"
else
  log "[SKIP] 未找到 update_hosts.sh"
fi

# 延迟执行 TXT → HTML 转换器（appuser）
if [ -x /tmp/txt_to_html.sh ]; then
  log "[INFO] 延迟 180 秒后执行 txt_to_html.sh（appuser）"
  (sleep 180 && su -s /bin/bash appuser -c "/tmp/txt_to_html.sh" && log "[OK] TXT → HTML 转换完成") &
else
  log "[SKIP] 未找到 txt_to_html.sh"
fi

# 启动 nginx（后台）
if command -v nginx >/dev/null 2>&1; then
  log "[INFO] 启动 nginx"
  nginx
  log "[OK] nginx 已启动"
else
  log "[SKIP] 未找到 nginx 可执行文件"
fi

# 启动日志服务
log "[INFO] 启动 rsyslog 和 cron"
rm -f /run/rsyslogd.pid || true
pgrep -x rsyslogd >/dev/null || rsyslogd
pgrep -x cron >/dev/null || cron
log "[OK] 日志服务已启动"

# 启动健康检查服务
log "[INFO] 启动健康检查服务"
nohup /tmp/health_server.sh >> "$LOG_FILE" 2>&1 &
log "[OK] 健康检查服务已启动"

# 启动导航页 HTTP 服务（BusyBox）
busybox httpd -p 8080 -h "$WORK_DIR/navpage" &
log "[OK] HTTP 服务已启动"

# 启动主进程
log "[INFO] 启动主进程 seven1.sh（appuser）"
exec su -s /bin/bash appuser -c "/tmp/seven1.sh"
