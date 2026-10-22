#!/bin/zsh
set -eu
stage_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ ! -f "$stage_dir/browser/index.html" ]]; then
  print -u2 '未找到 browser/index.html，请保留完整验收包目录。'
  exit 1
fi
/usr/bin/open "$stage_dir/browser/index.html"
