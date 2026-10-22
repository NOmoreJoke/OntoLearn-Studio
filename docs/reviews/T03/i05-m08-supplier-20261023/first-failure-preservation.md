# 首失败保留

`pytest-first-failure.log` 为本次1175项真实pytest合并stdout/stderr全文，保留8项失败和原执行路径证据，故作为必要小型原始证据入库；没有独立双流或完整fixture JSONL，不能重建或回填。其他首轮/正常构建原始日志留在本树 `build/m08-validation/`，精确身份和文件UTC时间见 validation-receipt.json；文件时间不冒称精确运行计时。未改冻结probe、inputs、implementation.md或guard，未重测pytest。
