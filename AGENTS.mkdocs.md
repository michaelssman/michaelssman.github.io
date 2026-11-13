# MkDocs 维护与提交规范

修改站点工程、导航、文档路径或提交本仓库前读取。只修改正文时不需要提前运行导航同步。

- 仅修改站点源码、脚本、依赖或构建行为时，读取 `~/.codex/personal-rules/engineering.md`，并同步相关站点说明；正文编辑和普通导航条目维护不加载工程分册。
- Git 提交前由 [.githooks/pre-commit](.githooks/pre-commit) 自动运行 `python3 scripts/sync_mkdocs_nav.py`。
- [同步脚本](scripts/sync_mkdocs_nav.py)以 Git 暂存区中的 `docs/` Markdown 文件为准，自动处理 `mkdocs.yml` 中 `nav` 的新增、删除和重命名，并自动暂存更新后的配置。
- 同目录重命名保留原有分组和位置；新增文档或跨目录移动按文件目录插入对应分组，缺少分组时使用目录名创建。保留已有中文标题和人工排序，只追加缺少的文档并移除失效路径。
- `docs/.hidden/` 及其他名称以 `.` 开头的目录不加入 `nav`。根目录的 `AGENTS*.md` 不属于站点文档，不移入 `docs/`。
- 如果 `mkdocs.yml` 存在未暂存修改，脚本必须停止，避免覆盖用户修改；先处理或暂存这些修改后再提交。
- 不使用 `--no-verify` 绕过同步。首次克隆后运行 `git config core.hooksPath .githooks`，启用仓库内的提交前校验。
- 需要只检查暂存区导航时，在仓库根目录运行 `python3 scripts/sync_mkdocs_nav.py --dry-run`；它不会修改或暂存文件，也不代表未暂存文档已被校验。
