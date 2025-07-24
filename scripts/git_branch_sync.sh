#!/bin/bash

# git_branch_sync.sh - 比对本地和远程仓库分支代码差异并同步更新

# 帮助信息
show_help() {
    echo "用法: $0 [-l <local_branch>] [-r <remote_branch>] [-R <remote_name>] [-p] [-f] [-h]"
    echo "选项:"
    echo "  -l <local_branch>   本地分支名称（默认：当前分支）"
    echo "  -r <remote_branch>  远程分支名称（默认：与本地分支同名）"
    echo "  -R <remote_name>    远程仓库名称（默认：origin）"
    echo "  -p                  同步后推送本地更改到远程仓库"
    echo "  -f                  强制同步（忽略冲突）"
    echo "  -h                  显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0                            # 比对当前分支与远程同名分支的差异并同步"
    echo "  $0 -l develop -r main         # 比对本地develop分支与远程main分支差异并同步"
    echo "  $0 -l feature -r develop -p   # 同步后推送更改到远程"
    echo "  $0 -R upstream -l main        # 使用upstream作为远程仓库"
    exit 1
}

# 默认值
LOCAL_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ -z "$LOCAL_BRANCH" ]; then
    echo "错误: 无法获取当前分支名称"
    exit 1
fi
REMOTE_BRANCH=""
REMOTE_NAME="origin"
PUSH_AFTER_SYNC=false
FORCE_SYNC=false

# 解析命令行参数
while getopts "l:r:R:pfh" opt; do
    case $opt in
        l)
            LOCAL_BRANCH="$OPTARG"
            ;;
        r)
            REMOTE_BRANCH="$OPTARG"
            ;;
        R)
            REMOTE_NAME="$OPTARG"
            ;;
        p)
            PUSH_AFTER_SYNC=true
            ;;
        f)
            FORCE_SYNC=true
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

# 如果没有指定远程分支，则使用与本地分支同名的分支
if [ -z "$REMOTE_BRANCH" ]; then
    REMOTE_BRANCH="$LOCAL_BRANCH"
fi

# 确保我们在正确的目录
cd "$(dirname "$0")/.."

# 检查本地分支是否存在
if ! git rev-parse --verify "$LOCAL_BRANCH" >/dev/null 2>&1; then
    echo "错误: 本地分支 '$LOCAL_BRANCH' 不存在"
    exit 1
fi

# 确保远程仓库已添加
if ! git remote | grep -q "^$REMOTE_NAME$"; then
    echo "错误: 远程仓库 '$REMOTE_NAME' 不存在"
    echo "可用的远程仓库:"
    git remote -v
    exit 1
fi

# 获取最新的远程仓库信息
echo "获取最新的远程仓库信息..."
git fetch "$REMOTE_NAME" || { echo "获取远程仓库信息失败"; exit 1; }

# 检查远程分支是否存在
if ! git rev-parse --verify "$REMOTE_NAME/$REMOTE_BRANCH" >/dev/null 2>&1; then
    echo "错误: 远程分支 '$REMOTE_NAME/$REMOTE_BRANCH' 不存在"
    exit 1
fi

# 切换到本地分支
echo "切换到本地分支 '$LOCAL_BRANCH'..."
git checkout "$LOCAL_BRANCH" || { echo "切换分支失败"; exit 1; }

# 比较本地和远程分支差异
echo "正在比对本地分支 '$LOCAL_BRANCH' 与远程分支 '$REMOTE_NAME/$REMOTE_BRANCH' 的差异..."

# 获取两个分支间的差异文件列表
DIFF_FILES=$(git diff --name-status "$LOCAL_BRANCH" "$REMOTE_NAME/$REMOTE_BRANCH")

if [ -z "$DIFF_FILES" ]; then
    echo "没有发现差异，两个分支已同步"
    exit 0
fi

# 显示差异详情
echo "发现以下差异文件:"
echo "$DIFF_FILES"
echo

# 确认是否继续
if [ "$FORCE_SYNC" != true ]; then
    read -p "是否继续同步这些更改? (y/n): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
fi

# 创建临时分支用于同步
TEMP_BRANCH="temp_sync_${LOCAL_BRANCH}_$(date +%s)"
echo "创建临时分支 '$TEMP_BRANCH' 用于同步..."
git checkout -b "$TEMP_BRANCH" "$LOCAL_BRANCH" || { echo "创建临时分支失败"; exit 1; }

# 尝试合并远程分支（保留本地的更改）
echo "合并远程分支 '$REMOTE_NAME/$REMOTE_BRANCH' 到临时分支..."
if [ "$FORCE_SYNC" = true ]; then
    git merge --strategy-option=theirs "$REMOTE_NAME/$REMOTE_BRANCH" || {
        echo "合并失败，正在还原更改...";
        git merge --abort;
        git checkout "$LOCAL_BRANCH";
        git branch -D "$TEMP_BRANCH";
        exit 1;
    }
else
    # 尝试正常合并，保留双方的修改
    if ! git merge "$REMOTE_NAME/$REMOTE_BRANCH"; then
        echo "合并过程中发生冲突"
        echo "请手动解决冲突后，执行以下命令完成同步:"
        echo "git add ."
        echo "git commit -m \"Merge remote branch $REMOTE_NAME/$REMOTE_BRANCH into $LOCAL_BRANCH\""
        echo "git checkout $LOCAL_BRANCH"
        echo "git merge $TEMP_BRANCH"
        echo "git branch -D $TEMP_BRANCH"
        exit 1
    fi
fi

# 切回本地分支并合并临时分支
echo "切回本地分支 '$LOCAL_BRANCH'..."
git checkout "$LOCAL_BRANCH" || { echo "切换回本地分支失败"; exit 1; }

echo "将临时分支合并到本地分支..."
git merge --no-ff "$TEMP_BRANCH" -m "同步远程分支 $REMOTE_NAME/$REMOTE_BRANCH 的更改" || {
    echo "合并临时分支失败";
    echo "请手动完成合并:";
    echo "git merge $TEMP_BRANCH";
    exit 1;
}

# 删除临时分支
echo "清理临时分支..."
git branch -D "$TEMP_BRANCH"

echo "同步完成！本地分支 '$LOCAL_BRANCH' 已更新"

# 如果指定了-p选项，则推送更改到远程
if [ "$PUSH_AFTER_SYNC" = true ]; then
    echo "推送更改到远程分支 '$REMOTE_NAME/$LOCAL_BRANCH'..."
    git push "$REMOTE_NAME" "$LOCAL_BRANCH" || { echo "推送到远程分支失败"; exit 1; }
    echo "推送完成"
fi

# 显示同步结果摘要
echo
echo "同步摘要:"
echo "----------------------------------------"
echo "本地分支: $LOCAL_BRANCH"
echo "远程分支: $REMOTE_NAME/$REMOTE_BRANCH"
echo "已同步的更改:"
git log -1 --stat
echo "----------------------------------------"
echo

echo "操作完成"