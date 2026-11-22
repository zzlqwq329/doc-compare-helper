# 文档对比与证据报告助手

一句话：同一份制度的两个版本，识别出未变 / 修改 / 删除 / 新增 / 跨章移动，输出一份每条都能定位回原文的证据报告。

**定位**：实习作品集项目。求职方向是安全开发 / 后端开发。

## 技术栈

刻意做成四层，每层对应一个面试能讲的能力面：

| 层 | 技术 | 职责 | 对应能力面 |
|---|---|---|---|
| 分析 | Python 3.14 + 标准库 | 读取、分段、条款匹配、差异识别、报告渲染 | 算法、数据处理、单元测试 |
| 后端 | Java 21 + Spring Boot + Spring Security + MySQL | 登录、资源授权、HTTP 接口、任务调度、报告发布 | 后端工程、权限模型、SQL |
| Worker | Python 独立进程 | 领取任务、回报进度、提交结果 | 异步、幂等、中断恢复 |
| Agent | 模型 API + 工具调用 | 差异解释、检索辅助、引用校验 | Prompt 工程、工具参数校验、注入防护 |

**安全不是单独一层，是贯穿每一层的约束**：越权防护（阶段 3）、上传校验（阶段 3）、prompt injection 防护（阶段 2）、任务幂等与审计（阶段 4）。这是走安全开发方向要讲的东西。

## 目录结构

```
project/            Python 分析层
  reader.py         读取与分段
  compare.py        条款匹配与差异识别
  report.py         报告渲染（阶段 1 待建）
  test_*.py         测试
java/                Java 后端（阶段 3 待建）
  src/main/java/    接口、权限、任务调度
  src/test/java/    接口测试与越权测试
samples/            两份样本（V1 13 段 / V2 14 段）
fixtures/           人工标注答案（只读）
docs/               需求、进度、各 Task 说明
outputs/            运行产物（gitignore）
```

## 关键代码

`project/reader.py`
```python
def parse_blocks(path: Path, version_id: str) -> list[Block]
# Block: version_id / block_id / section / line_start / line_end / raw_text
```

`project/compare.py`
```python
MIN_SIMILARITY: Final = 0.60

def compare_versions(v1_blocks: list[Block], v2_blocks: list[Block]) -> list[dict]
# item: {"type": str, "old": Block | None, "new": Block | None}
# type ∈ unchanged / moved / modified / deleted / added / needs_review

def unique_best_candidate(candidates: list[tuple[str, float]]) -> str | None
def group_by_text(blocks: list[Block]) -> dict[str, list[str]]
```

对外 HTTP 接口共 8 个，统一前缀 `/api/v1`，设计见 `docs/项目需求与接口设计.md`。

## 阶段与通过条件

| 阶段 | 交付 | 通过条件 |
|---|---|---|
| 0 样本与规则 | 两个版本 + 人工答案 | 能说明每一处变化及其原文位置 |
| 1 基础对比 | TXT/Markdown 对比与 Markdown 报告 | 新增、删除、修改、移动都有对应证据；全部段落都有处理记录 |
| 2 证据报告 | 文本 PDF、模型解释、引用校验 | 每条结论可追溯，模型推断单独标明 |
| 3 Java 业务 | 上传、版本、任务、报告下载 | 用户能走完整流程，数据按用户隔离 |
| 4 可靠任务 | 独立 Worker、恢复、重试与幂等 | 中断后能恢复，旧执行结果不能覆盖新结果 |
| 5–6 扩展 | 检索、受限 Agent、组织授权 | 根据前面版本的实际问题逐项加入 |

当前走到哪一步，看 `docs/progress.md`，不要凭印象。

## 环境

- Python：`.venv\Scripts\python.exe`（3.14.10），pytest 9.2.0 已装
- 跑测试：`.\.venv\Scripts\python.exe -m pytest project/ -v`
- git 分支 main，远程 `github.com/zzlqwq329/doc-compare-helper`

## 全局规矩

1. `fixtures/expected-changes.json` 是人工标注的标准答案，**只读**。程序运行时不许读它，测试读取是允许的。
2. 不许写死绝对路径，用 `Path(__file__).resolve().parents[N]` 算根目录。
3. 不许用 `pytest.skip` / `try-except` 吞异常 / `assert True` 糊弄测试。
4. 分析层只依赖标准库，引入第三方库要先说明理由。
5. 代码风格 PEP 8，注释写「为什么」不写「是什么」，中文注释。
6. 改动被测代码前先跑一遍测试存基线，改完再跑，对比结果。
