# git 基础操作笔记

记录时间：2026-11-18。本文只覆盖到现在为止实际用到的命令，按「先做完再补原理」的顺序整理。

## 一、git 在管什么

三个区域：

- **工作区**：磁盘上你正在编辑的那些文件。
- **暂存区**：`git add` 之后，改动待着的地方。
- **仓库**：`git commit` 之后，封存成的一张快照。

一句话记住区别：`add` 是「我要交这个」，`commit` 是「封存」。只写文件不做 add，git 看不到；add 了不 commit，等于东西放在桌上没装箱。

## 二、每台机器做一次的配置

### 1. 确认装了

```bash
git --version
```

出现版本号就行（当前是 2.55.0.windows.2）。

### 2. 配置身份

```bash
git config --global user.name "拼音或英文名"
git config --global user.email "你的邮箱"
```

不配的话 `git commit` 会报 `Author identity unknown`，并提示 `fatal: unable to auto-detect email address`。

`--global` 表示对所有仓库生效，去掉只对当前仓库生效。名字建议用拼音或英文，有些平台对中文显示不友好。邮箱以后要推到 GitHub / Gitee 的话，必须和平台账号一致。

### 3. 中文文件名正常显示

```bash
git config --global core.quotepath false
```

不配的话 `git status` 里中文文件名会显示成 `\346\226\207\346\241\243...` 这种八进制转义。

## 三、跟着仓库走的两个文件

### .gitignore

列出「不进版本库」的东西。判断标准只有一条：**能重新生成的，放进名单更干净；手写的东西，绝不能进名单。**

本项目当前内容：

```
.venv/
__pycache__/
*.pyc
.ruff_cache/
.pytest_cache/
.env
outputs/
.idea/
*.iml
```

- `__pycache__/`、`*.pyc` 是 Python 自动生成的编译缓存
- `outputs/` 是跑一遍就会再出现的中间结果
- `.idea/`、`*.iml` 是 IDEA 的个人配置，里面有本机 JDK 路径和窗口状态，会一直变
- `.venv/` 是虚拟环境，几百兆

反过来，`samples/`、`fixtures/`、`docs/`、`project/` 这些手写的必须进版本库。

### .gitattributes

解决 Windows 上那一堆 `warning: LF will be replaced by CRLF`。

```
* text=auto eol=lf
```

意思是：按文本处理，统一存成 LF。写代码用这个最省事——`project/reader.py:27` 那种 `line.removesuffix("\n")` 的写法不会因为换行符变成 `\r\n` 而多出一个 `\r`。

## 四、建仓库（每个项目一次）

```bash
cd "D:\Java\文档分析项目"
git init
```

看到 `Initialized empty Git repository in .../.git/` 就成功了。这一步会在项目里创建一个隐藏的 `.git/` 目录，快照都存那儿，只在本机，不会自动上传。

Git Bash 里盘符要写成 `/d/`：

```bash
cd /d/Java/文档分析项目
```

中文路径在 Git Bash 下容易出问题，能用 Tab 补全就别手打。

## 五、日常循环（每次改完代码）

```bash
git status
git add .
git status
git commit -m "这一版做了什么"
```

第二个 `git status` 不能省。它是提交前最后一道检查：确认没有 `.venv`、`outputs`、`.idea` 这种东西混进待提交列表。`git add .` 收东西很干脆，收错了再想从历史里挖出来很麻烦。

`commit -m` 后面的说明一句话说清这版做了什么，不要写「update」「修改」这种。参考：

- `初始化：文档对比项目，完成读取分段与差异识别`
- `Task 4：生成 Markdown 证据报告`
- `修复：修改匹配在并列候选时误判`

## 六、看历史和状态

```bash
git status              # 当前工作区与暂存区状态
git log --oneline       # 提交历史，一行一条
git log --oneline --graph   # 有分支时看图形
```

`git status --short` 里两个字母的含义：第一位是暂存区状态，第二位是工作区状态。

- `A ` 新增且已暂存，工作区没再动
- `AM` 新增已暂存，但暂存之后又改过，需要再 `git add`
- ` M` 已跟踪的文件被改过，还没 `git add`

## 七、改坏了怎么退

```bash
git status                  # 先确认是哪个文件
git restore 文件名           # 丢弃工作区的改动，回到上次 commit 的样子
git restore --staged 文件名   # 只从暂存区拿出来，磁盘文件不动
```

`git restore` 丢掉的东西找不回来，执行前先看清楚文件。

## 八、这次踩过的坑

### 1. `bash: $'\302\226': command not found`

从网页或聊天窗口复制命令时，带进了不可见的控制字符（`\302\226` 是 UTF-8 的 C1 控制符 U+0096）。bash 把它当成命令名了。

解法：手打，或者用 Tab 补全，别直接从富文本来源粘贴。

### 2. `Author identity unknown`

见第二节第 2 条，配置 `user.name` 和 `user.email`。

### 3. `.idea/` 混进了提交

第一次 `git add .` 把 IDEA 的配置一起收了进去。修法分两步：

```bash
git rm -r --cached .idea project/.idea
```

`--cached` 的意思是只从暂存区移除，磁盘上的文件不动，IDEA 照常能用。然后把 `.idea/` 和 `*.iml` 写进 `.gitignore`。

### 4. `warning: LF will be replaced by CRLF`

Windows 换行符问题，加 `.gitattributes` 解决，见第三节。

### 5. MinTTY 里的复制粘贴

Git Bash 用的是 MinTTY 终端，不是 Windows 控制台，快捷键不一样：

- `Ctrl + Insert` 复制
- `Shift + Insert` 粘贴
- 鼠标选中文字会自动复制
- 在窗口内容区点中键也等于粘贴

想用 `Ctrl+Shift+C` / `Ctrl+Shift+V`：标题栏右键 → Options → Keys → 勾选 `Ctrl+Shift+letter shortcuts`。

## 九、还没用到的

以后要用再学，现在不用管：

- 分支：`git branch`、`git switch`、`git merge`
- 远程仓库：`git remote add`、`git push`、`git pull`
- 撤销一次已提交的改动：`git revert`
- 临时存起来：`git stash`

等要传到 GitHub 或 Gitee 的时候再回头看这一节。
