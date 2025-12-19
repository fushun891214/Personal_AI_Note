#!/bin/bash
# 檢查 Docker 容器內的字體路徑

echo "=== 檢查容器內的 Noto CJK 字體 ==="
docker run --rm ai-notes-summary find /usr/share/fonts -name "*Noto*CJK*" -type f

echo ""
echo "=== 檢查所有中文字體 ==="
docker run --rm ai-notes-summary find /usr/share/fonts -name "*.ttc" -o -name "*.ttf" | grep -i -E "(noto|cjk|chinese)"

echo ""
echo "=== 檢查 fonts-noto-cjk 套件是否安裝 ==="
docker run --rm ai-notes-summary dpkg -l | grep noto
