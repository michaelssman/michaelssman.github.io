# 项目协作规范

## MkDocs 导航同步

- Git 提交前由 `.githooks/pre-commit` 自动运行 `python3 scripts/sync_mkdocs_nav.py`。
- 脚本以 Git 暂存区中的 `docs/` Markdown 文件为准，自动处理 `mkdocs.yml` 中 `nav` 的新增、删除和重命名，并自动暂存更新后的 `mkdocs.yml`。
- 同目录重命名保留原有分组和位置；新增文档或跨目录移动会按文件目录插入对应分组，缺少分组时使用目录名创建。
- 脚本保留已有中文标题和人工排序，只追加缺少的文档并移除失效路径。
- 如果 `mkdocs.yml` 存在未暂存修改，脚本必须停止，避免覆盖用户修改；先处理或暂存这些修改后再提交。
- 不要使用 `--no-verify` 绕过同步。
- 首次克隆仓库后运行 `git config core.hooksPath .githooks`，启用仓库内维护的提交前校验。
