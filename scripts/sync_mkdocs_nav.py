#!/usr/bin/env python3
"""Synchronize MkDocs nav with Markdown files tracked in the Git index."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent.parent
MKDOCS_CONFIG = ROOT / "mkdocs.yml"
DOCS_PREFIX = "docs/"
MARKDOWN_SUFFIXES = {".md", ".markdown"}
DEFAULT_INDENT = 2

LIST_ITEM = re.compile(r"^(?P<indent>\s*)-\s+(?P<body>.*?)\s*$")


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_output(*args: str) -> str:
    result = run_git(*args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Git 命令执行失败")
    return result.stdout


def tracked_markdown_paths() -> set[str]:
    output = git_output(
        "-c",
        "core.quotepath=false",
        "ls-files",
        "--cached",
        "--",
        "docs",
    )
    return {
        nav_path
        for repository_path in output.splitlines()
        if (nav_path := to_nav_path(repository_path)) is not None
    }


def staged_same_directory_renames() -> list[tuple[str, str]]:
    output = git_output(
        "-c",
        "core.quotepath=false",
        "diff",
        "--cached",
        "--name-status",
        "--find-renames",
        "--diff-filter=R",
        "--",
        "docs",
    )
    renames: list[tuple[str, str]] = []
    for line in output.splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        old_path = to_nav_path(fields[1])
        new_path = to_nav_path(fields[2])
        if not old_path or not new_path:
            continue
        if PurePosixPath(old_path).parent == PurePosixPath(new_path).parent:
            renames.append((old_path, new_path))
    return renames


def to_nav_path(repository_path: str) -> str | None:
    if not repository_path.startswith(DOCS_PREFIX):
        return None
    nav_path = repository_path[len(DOCS_PREFIX) :]
    path = PurePosixPath(nav_path)
    if any(part.startswith(".") for part in path.parts):
        return None
    if path.suffix.lower() not in MARKDOWN_SUFFIXES:
        return None
    return nav_path


def staged_config() -> str:
    result = run_git("show", ":mkdocs.yml")
    if result.returncode != 0:
        raise RuntimeError("无法读取暂存区中的 mkdocs.yml；请确认文件已被 Git 跟踪")
    return result.stdout


def split_config(config: str) -> tuple[str, list[str], str]:
    nav_match = re.search(r"(?m)^nav:\s*(?:#.*)?$", config)
    if not nav_match:
        raise RuntimeError("mkdocs.yml 中没有找到顶层 nav 配置")

    line_end = config.find("\n", nav_match.end())
    nav_start = len(config) if line_end == -1 else line_end + 1
    next_section = re.search(r"(?m)^[^\s#][^:\n]*:\s*", config[nav_start:])
    nav_end = nav_start + next_section.start() if next_section else len(config)

    before_next_section = config[nav_start:nav_end].splitlines(keepends=True)
    while before_next_section and (
        not before_next_section[-1].strip()
        or before_next_section[-1].startswith("#")
    ):
        nav_end -= len(before_next_section.pop())

    return config[:nav_start], config[nav_start:nav_end].splitlines(keepends=True), config[nav_end:]


def item(line: str) -> tuple[int, str] | None:
    match = LIST_ITEM.match(line.rstrip("\r\n"))
    if not match or line.lstrip().startswith("#"):
        return None
    return len(match.group("indent")), match.group("body")


def strip_inline_comment(body: str) -> str:
    return re.split(r"\s+#", body, maxsplit=1)[0].rstrip()


def category_label(line: str) -> str | None:
    parsed = item(line)
    if not parsed:
        return None
    body = strip_inline_comment(parsed[1])
    if not body.endswith(":"):
        return None
    return body[:-1].strip().strip("\"'")


def leaf_path(line: str) -> str | None:
    parsed = item(line)
    if not parsed:
        return None
    body = strip_inline_comment(parsed[1])
    if body.endswith(":"):
        return None
    if ": " in body:
        body = body.rsplit(": ", maxsplit=1)[1]
    path = body.strip().strip("\"'")
    if PurePosixPath(path).suffix.lower() not in MARKDOWN_SUFFIXES:
        return None
    return path


def active_paths(lines: list[str]) -> set[str]:
    return {path for line in lines if (path := leaf_path(line)) is not None}


def root_indent(lines: list[str]) -> int:
    indents = [parsed[0] for line in lines if (parsed := item(line)) is not None]
    return min(indents, default=DEFAULT_INDENT)


def indent_step(lines: list[str]) -> int:
    indents = sorted({parsed[0] for line in lines if (parsed := item(line)) is not None})
    differences = [right - left for left, right in zip(indents, indents[1:]) if right > left]
    return min(differences, default=DEFAULT_INDENT)


def block_end(lines: list[str], parent_index: int | None, parent_indent: int) -> int:
    start = 0 if parent_index is None else parent_index + 1
    for index in range(start, len(lines)):
        parsed = item(lines[index])
        if not parsed:
            continue
        if parent_index is not None and parsed[0] <= parent_indent:
            return index
    return len(lines)


def category_contains_prefix(
    lines: list[str], category_index: int, category_indent: int, prefix: str
) -> bool:
    end = block_end(lines, category_index, category_indent)
    prefix_with_separator = f"{prefix}/"
    for line in lines[category_index + 1 : end]:
        path = leaf_path(line)
        if path and (path == prefix or path.startswith(prefix_with_separator)):
            return True
    return False


def find_child_category(
    lines: list[str],
    parent_index: int | None,
    parent_indent: int,
    child_indent: int,
    directory_name: str,
    prefix: str,
) -> int | None:
    end = block_end(lines, parent_index, parent_indent)
    start = 0 if parent_index is None else parent_index + 1
    candidates: list[int] = []

    for index in range(start, end):
        parsed = item(lines[index])
        if not parsed or parsed[0] != child_indent:
            continue
        label = category_label(lines[index])
        if label is None:
            continue
        if label.casefold() == directory_name.casefold():
            return index
        candidates.append(index)

    for index in candidates:
        if category_contains_prefix(lines, index, child_indent, prefix):
            return index
    return None


def replace_path(lines: list[str], old_path: str, new_path: str) -> bool:
    changed = False
    for index, line in enumerate(lines):
        if leaf_path(line) != old_path:
            continue
        lines[index] = line.replace(old_path, new_path, 1)
        changed = True
    return changed


def remove_paths(lines: list[str], paths: set[str]) -> int:
    original_length = len(lines)
    lines[:] = [line for line in lines if leaf_path(line) not in paths]
    return original_length - len(lines)


def prune_empty_categories(lines: list[str]) -> int:
    removed = 0
    while True:
        empty_index: int | None = None
        for index in range(len(lines) - 1, -1, -1):
            parsed = item(lines[index])
            if not parsed or category_label(lines[index]) is None:
                continue
            end = block_end(lines, index, parsed[0])
            has_child = any(
                (child := item(lines[child_index])) is not None and child[0] > parsed[0]
                for child_index in range(index + 1, end)
            )
            if not has_child:
                empty_index = index
                break
        if empty_index is None:
            return removed
        del lines[empty_index]
        removed += 1


def add_path(lines: list[str], path: str) -> bool:
    if path in active_paths(lines):
        return False

    directories = list(PurePosixPath(path).parent.parts)
    if directories == ["."]:
        directories = []

    step = indent_step(lines)
    top_indent = root_indent(lines)
    parent_index: int | None = None
    parent_indent = top_indent - step
    child_indent = top_indent

    for position, directory_name in enumerate(directories):
        prefix = "/".join(directories[: position + 1])
        category_index = find_child_category(
            lines,
            parent_index,
            parent_indent,
            child_indent,
            directory_name,
            prefix,
        )
        if category_index is None:
            insertion_index = block_end(lines, parent_index, parent_indent)
            new_lines: list[str] = []
            indent = child_indent
            for missing_directory in directories[position:]:
                new_lines.append(f"{' ' * indent}- {missing_directory}:\n")
                indent += step
            new_lines.append(f"{' ' * indent}- {path}\n")
            lines[insertion_index:insertion_index] = new_lines
            return True

        parent_index = category_index
        parent_indent = child_indent
        child_indent += step

    insertion_index = block_end(lines, parent_index, parent_indent)
    lines.insert(insertion_index, f"{' ' * child_indent}- {path}\n")
    return True


def synchronize(config: str, tracked_paths: set[str], renames: list[tuple[str, str]]) -> tuple[str, int, int, int]:
    prefix, nav_lines, suffix = split_config(config)
    renamed = 0

    for old_path, new_path in renames:
        if new_path in tracked_paths and replace_path(nav_lines, old_path, new_path):
            renamed += 1

    stale_paths = active_paths(nav_lines) - tracked_paths
    removed = remove_paths(nav_lines, stale_paths)
    prune_empty_categories(nav_lines)

    missing_paths = sorted(tracked_paths - active_paths(nav_lines), key=str.casefold)
    added = sum(add_path(nav_lines, path) for path in missing_paths)

    updated = prefix + "".join(nav_lines) + suffix
    return updated, added, removed, renamed


def has_unstaged_config_changes() -> bool:
    result = run_git("diff", "--quiet", "--", "mkdocs.yml")
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.strip() or "无法检查 mkdocs.yml 的工作区状态")
    return result.returncode == 1


def stage_config() -> None:
    result = run_git("add", "--", "mkdocs.yml")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "无法暂存 mkdocs.yml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只报告同步结果，不修改或暂存 mkdocs.yml",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = staged_config()
        updated, added, removed, renamed = synchronize(
            config,
            tracked_markdown_paths(),
            staged_same_directory_renames(),
        )
        if updated == config:
            print("[mkdocs-nav] nav 已与暂存区中的文档同步。")
            return 0

        if args.dry_run:
            print(
                f"[mkdocs-nav] 需要同步：新增 {added}，删除 {removed}，"
                f"同目录重命名 {renamed}。"
            )
            return 0

        if has_unstaged_config_changes():
            raise RuntimeError(
                "mkdocs.yml 存在未暂存修改，为避免覆盖，请先处理或暂存这些修改"
            )

        MKDOCS_CONFIG.write_text(updated, encoding="utf-8")
        stage_config()
        print(
            f"[mkdocs-nav] 已自动同步并暂存 mkdocs.yml：新增 {added}，"
            f"删除 {removed}，同目录重命名 {renamed}。"
        )
        return 0
    except RuntimeError as error:
        print(f"[mkdocs-nav] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
