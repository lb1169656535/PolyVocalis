#!/bin/bash

# 输入目录
INPUT_DIR="$HOME/project/data/xjia_wav"

# 输出目录（自动创建日期子目录）
OUTPUT_ROOT="./output"
OUTPUT_DIR="${OUTPUT_ROOT}/$(date +%Y%m%d)"
mkdir -p "${OUTPUT_DIR}"

# 并行工作参数
GPU_ID=0
THREADS=4
WORD_THRESHOLD=15

# 获取排序后的文件列表（按数字顺序）
mapfile -t FILES < <(ls "${INPUT_DIR}"/*.wav | sort -V)

# 显示任务信息
echo "━━━━━━ 批量处理任务 ━━━━━━"
echo "• 输入文件: ${#FILES[@]} 个"
echo "• 输出目录: ${OUTPUT_DIR}"
echo "• 线程数: ${THREADS}"
echo "• GPU设备: ${GPU_ID}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"

# 进度计数器
COUNT=0

# 遍历处理
for FILE in "${FILES[@]}"; do
    ((COUNT++))
    FILENAME=$(basename "${FILE}")
    
    echo "▶ 正在处理 (${COUNT}/${#FILES[@]}) ${FILENAME}"
    
    # 执行处理命令
    python app.py \
        -i "${FILE}" \
        -o "${OUTPUT_DIR}" \
        -w ${WORD_THRESHOLD} \
        -t ${THREADS} \
        --gpu ${GPU_ID}

    # 检查退出状态
    if [ $? -ne 0 ]; then
        echo "❌ 处理失败: ${FILENAME}"
        exit 1
    fi
done

echo "✅ 全部文件处理完成！"
