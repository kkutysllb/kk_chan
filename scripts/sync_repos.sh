#!/bin/bash

# 帮助信息
show_help() {
    echo "用法: $0 [-b <branch>] [-n] [-m <commit_message>] [-h]"
    echo "选项:"
    echo "  -b <branch>        指定要同步的分支名称（默认：main）"
    echo "  -n                 如果指定的分支不存在，则创建新分支"
    echo "  -m <message>       提交信息（如果不提供则只同步不提交）"
    echo "  -h                 显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 -b develop -m \"feat: 添加新功能\""
    echo "  $0 -b main         # 仅同步main分支"
    echo "  $0 -b v0.11 -n -m \"fix: 修复bug\"  # 创建新分支v0.11并提交"
    exit 1
}

# 默认值
BRANCH="main"
COMMIT_MESSAGE=""
CREATE_NEW_BRANCH=false

# 解析命令行参数
while getopts "b:m:nh" opt; do
    case $opt in
        b)
            BRANCH="$OPTARG"
            ;;
        m)
            COMMIT_MESSAGE="$OPTARG"
            ;;
        n)
            CREATE_NEW_BRANCH=true
            ;;
        h)
            show_help
            ;;
        \?)
            echo "无效的选项: -$OPTARG" >&2
            show_help
            ;;
    esac
done

# 确保我们在正确的目录
cd "$(dirname "$0")/.."

# 检查分支是否存在
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    if [ "$CREATE_NEW_BRANCH" = true ]; then
        echo "分支 '$BRANCH' 不存在，正在创建新分支..."
        git checkout -b "$BRANCH" || exit 1
        echo "已创建并切换到新分支 '$BRANCH'"
    else
        echo "错误: 分支 '$BRANCH' 不存在"
        echo "如果要创建新分支，请使用 -n 选项"
        exit 1
    fi
else
    # 切换到指定分支
    echo "切换到分支 '$BRANCH'..."
    git checkout "$BRANCH" || exit 1
fi

# 如果提供了提交信息，则执行提交
if [ ! -z "$COMMIT_MESSAGE" ]; then
    echo "准备提交更改..."
    
    # 检查是否有更改需要提交
    if [ -z "$(git status --porcelain)" ]; then
        echo "没有需要提交的更改"
    else
        # 添加所有更改
        echo "添加更改到暂存区..."
        git add .

        # 提交更改
        echo "提交更改..."
        git commit -m "$COMMIT_MESSAGE" || exit 1
    fi
fi

# 添加远程仓库（如果还没添加）
# GitHub
if ! git remote | grep -q "^github$"; then
    echo "添加 GitHub 远程仓库..."
    git remote add github https://github.com/kkutysllb/Sn_5GC_GraphAgent.git
fi

# 同步到GitHub仓库
if [ "$CREATE_NEW_BRANCH" = true ]; then
    echo "推送到 GitHub(origin) (新分支)..."
    git push --set-upstream origin "$BRANCH"
else
    echo "推送到 GitHub(origin)..."
    git push origin "$BRANCH"
fi

echo "同步完成！"