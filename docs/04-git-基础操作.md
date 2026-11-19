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

在本地项目目录执行：

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
git add .   (git add 文件路径)
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

看某一次提交具体改了什么：

```bash
git show 5698079          # 看这次提交的全部改动
git show --stat 5698079   # 只看改了哪些文件、各加减几行
```

### GitHub 网页上的文件列表

仓库首页文件列表右边那一列，显示的是**最后一次改动这个文件的提交信息**，不是文件内容，也不是创建时间。

所以刚 push 上去只有一个提交时，每个文件都显示同一条消息，看起来全一样——这是正常的，不是哪里配错了。

提交多了以后这一列会分开：改过的文件显示改它那次提交，一直没动过的还是最早那条。点那行消息进去，就是那次提交的完整 diff：这次改了哪些文件、每行加了什么删了什么。

### 一次提交该放多少东西

一次提交 = 一件说得清的事。

- `docs：补 git 基础操作笔记`
- `Task 4：生成 Markdown 证据报告`
- `修复：修改匹配在并列候选时误判`

攒十件事一起提交的坏处：历史里只有一条，出问题想回退只能整条回退；网页上那列也永远是同一句话，看不出任何信息。`git commit -m "update"` 这种，过三天连自己都不知道改了什么。

## 七、推到 GitHub / Gitee（每个项目一次）

本地 `commit` 只写进项目里的 `.git/`，不上网。要出现在平台上，得先有远程地址，再推。

### 什么时候 push

`commit` 是「我这儿存好了」，`push` 是「别人能看到了」。默认节奏是 commit 完就 push，别攒一堆。

**这些时候要 push：**

- **一天收工前。** 代码只在本地磁盘上，硬盘坏了、电脑丢了就全没了。push 过就有两份
- **换电脑、换环境、明天要接着写之前。** 不然另一台 `git pull` 拉不到你今天的改动
- **想让别人看到之前。** 放进简历想让面试官点进来，就得先 push
- **合并到 `main` 之后。** 主分支本来就该随时是能用的状态

**这些时候先别 push：**

- 代码跑不起来、测试是红的。远程是别人会看到的状态，别把半截东西放上去
- 你自己还没验证过这批改动
- 里面有密码、密钥、`.env`、数据库连接串。push 之后就留痕了，改密码也删不干净

拿不准就开一条分支推：`git push -u origin 分支名`。分支写坏了删掉，不影响 `main`。

**怎么知道有没有没推的：**

```bash
git status -sb
```

第一行长这样：

```
## main...origin/main [ahead 2]
```

`ahead 2` 就是「本地有 2 个提交没推上去」。不显示 `[ahead N]` 就是干净的，本地远程一致。

### 1. 平台上建空仓库

- **初始化选项一个都别勾**：Add README、Add .gitignore、Choose a license。本地已有这些文件，勾了会生成另一条互不相干的历史，push 会被拒（`rejected — fetch first`）
- 建议 Public，找实习时面试官点得进来

### 2. 本地关联远程

```bash
git remote add origin https://github.com/用户名/仓库名.git
git branch -M main      # 本地默认叫 master，平台默认 main，统一一下
git push -u origin main
```

`-u` 是把本地分支和远程分支绑起来，绑过以后直接 `git push` 就行，不用再写 `origin main`。

### 3. 认证

平台密码在这里无效，会报 `Support for password authentication was removed`。

Windows 版 git 自带凭据管理器，第一次 push 通常会弹浏览器让你点授权。没弹的话手动生成 token：

1. GitHub 头像 → Settings → 左侧最下 Developer settings
2. Personal access tokens → Tokens (classic) → Generate new token (classic)
3. Expiration 选 90 days，权限勾 `repo` 整块
4. 复制 `ghp_` 开头那串（只显示一次）
5. push 时 Username 填用户名，Password 粘贴 token

凭据会被记住，以后不用再输。

### 4. 确认

```bash
git remote -v      # 应看到两行 origin（fetch / push）
git status -sb     # 分支名后面出现 ...origin/main
```

刷新仓库页面，文件都在就成功了。

## 八、改坏了怎么退

```bash
git status                  # 先确认是哪个文件
git restore 文件名           # 丢弃工作区的改动，回到上次 commit 的样子
git restore --staged 文件名   # 只从暂存区拿出来，磁盘文件不动
```

`git restore` 丢掉的东西找不回来，执行前先看清楚文件。

## 九、这次踩过的坑

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

### 6. `fatal: pathspec 'docs/?[200~' did not match any files`

粘贴路径时，终端塞进了一串转义标记（bracketed paste 的开头标记 `\e[200~`），Git Bash 不认这个标记，把它当成了文件名的一部分。

解法：手打路径，或者打前几个字按 `Tab` 补全。要给整个目录就直接写 `git add docs/` 或 `git add .`。

### 7. `schannel: server closed abruptly (missing close_notify)`

push 或 fetch 时连接被断开。`schannel` 是 Windows 自带的 TLS 实现，这句话的意思是它在等服务器发「我要关了」的信号，结果连接直接被掐断。

多数情况是网络抖动，重试一次就好，这和你的操作无关。反复出现再换 TLS 后端：

```bash
git config --global http.sslBackend openssl
```

判断有没有真推上去，不要靠感觉：`git status -sb` 里分支名后面跟着 `...origin/分支名`，或者 `git branch -a` 里能看到 `remotes/origin/分支名`，才算成功。

### 8. 推了分支，网页上却找不到

两个原因，先分清是哪个：

- **看错分支**：GitHub 仓库页面左上角有个分支下拉，默认停在 `main`。刚推的分支要切过去才看得到。分支上的新文件，`main` 页面本来就不显示
- **根本没推上去**：`git status -sb` 里分支名后面没有 `...origin/分支名`，就说明没跟踪、没推成功

## 十、克隆别人的仓库

本地没有项目、只有平台地址时用它。接手别人的项目，第一条命令是 clone，不是 init。

```bash
git clone https://github.com/某人/某仓库.git
git clone https://github.com/某人/某仓库.git 自定义目录名
```

clone 一次干三件事：下载全部历史、自动配好 `origin`、自动建本地分支并跟踪远程分支。所以克隆下来的仓库不需要再 `git remote add`。

`init` 和 `clone` 的区别一句话：**从零开始用 init，拿现成的用 clone**。

## 十一、分支

分支就是一条独立的提交线。改需求、试想法、修 bug 时开一条，写坏了大不了删掉，主分支不受影响。

```bash
git branch                  # 列出本地分支，带 * 的是当前分支
git branch 分支名            # 新建分支，建完人还在原分支上
git switch 分支名            # 切换过去
git switch -c 分支名         # 新建并直接切过去（最常用）
git branch -d 分支名         # 删掉已合并的分支
git branch -D 分支名         # 强制删，未合并也删（会丢改动）
```

旧教程里的 `git checkout` 也能切分支，但 `checkout` 兼职干好几件事（还能恢复文件），容易搞混。新版本统一用 `switch` 切分支、`restore` 恢复文件。

### 合并

站在目标分支上执行，把另一条分支的改动并进来：

```bash
git switch main
git merge 分支名
```

合并完那条分支就没用了，`git branch -d 分支名` 删掉。

两边都动过的时候，git 会额外生成一次**合并提交**，输出：

```
Merge made by the 'ort' strategy.
 docs/05-分支练习.md | 3 +++
```

`'ort'` 是 git 的默认合并算法名，念出来是 "ort"，不用管它。

这时 `git log --oneline --graph` 能看出分叉和汇合：

```
*   f6c17f8 Merge branch 'practice/branch-test'
|\
| * 3fe2d42 docs:新增分支练习文件
* | 6e9a767 Update README.md
|/
* 8193fd7 docs：更新
```

读法：`|\` 是分叉点，`|/` 是汇合点，`*   `（星号后三个空格）表示这是一次合并提交，上下两行分别是两条线的最后一次提交。

如果合并时 `main` 一次都没动过，git 会直接「快进」（fast-forward），不生成合并提交，历史保持一条直线。

### 分支和远程

```bash
git push -u origin 分支名    # 第一次推某条分支要带 -u
git branch -a               # 连远程分支一起列出来
git switch 远程已有的分支名   # 新版本会自动建本地分支并跟踪远程
```

## 十二、拉取远程更新

一个地方 push 了，另一个地方得先拉下来才能接着改。

```bash
git pull        # 拉取并合并到当前分支，最常用
git fetch       # 只拉取，不动本地文件
```

`pull` = `fetch` + `merge`。一个人开发直接 `pull`；想先看看远程改了什么再决定合不合，用 `fetch`。

**只要 push 被拒**（`rejected — fetch first` 或 `non-fast-forward`），意思就是远程有你本地没有的提交，先 `git pull` 再 push。

### pull 成功长什么样

```
Updating 8193fd7..6e9a767
Fast-forward
 README.md | 2 +-
```

- `Updating A..B`：本地从 `8193fd7` 前进到 `6e9a767`
- `Fast-forward`：本地这段时间没有新提交，git 直接把指针挪过去，不产生合并提交，历史还是一条直线
- 如果这里换成 `Merge made by the 'ort' strategy.`，说明两边都动过，生成了合并提交（见第十一节）
- 最后那行 `README.md | 2 +-` 是这次拉下来改动的文件清单

### 拉之前先看工作区

本地有未提交的改动时 `pull` 可能被拒（`Your local changes would be overwritten`）。两种处理：

```bash
git stash        # 先存起来，pull 完再 git stash pop 放回来
git commit -m "..."   # 或者干脆先提交
```

别用 `git checkout .` 硬来，那会把改动直接丢掉。

## 十三、冲突怎么处理

两边改了同一个文件的同一处，或者 pull 下来时本地有未提交的改动，就会冲突。git 会停下来，在文件里留下标记：

```
<<<<<<< HEAD
本地这版的内容
=======
远程或对方分支那版的内容
>>>>>>> 分支名
```

处理步骤：

1. `git status` 看哪些文件冲突，状态是 `both modified`
2. 打开文件，人工决定留哪段、怎么拼，**把 `<<<<<<<`、`=======`、`>>>>>>>` 三行标记删干净**
3. `git add 冲突文件`
4. `git commit`（不用带 `-m`，git 会预填一条合并信息）

处理到一半想反悔，`git merge --abort` 回到合并前的状态。

别用「随便选一边」应付。冲突点往往是两个人都动过的地方，谁对得自己判断。

## 十四、暂时用不到的

- 撤销一次已提交的改动：`git revert 提交号`（生成一次反向提交，历史保留）
- 临时存起来再切分支：`git stash`、`git stash pop`
- 打版本标记：`git tag v1.0`、`git push --tags`
- 挑单个提交搬过来：`git cherry-pick 提交号`
- 改写历史：`git commit --amend`、`git rebase -i`（只在本地未推送时用，动过远程的提交会害到别人）
