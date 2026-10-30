#!/usr/bin/env python3
"""通用 iOS Bugly 主应用 dSYM 上传工具；默认交互选择 Xcode 归档。"""

# 使用流程：发现/选择归档 → 核验主程序与 dSYM → 调用官方 Java 工具 → 保存脱敏结果。
# --list 和 --check 仅做本地读取/检查；实际上传后仍需网页核对版本和 UUID。
# Python 语法学习说明见同目录的《Python基础语法学习笔记.md》。
import argparse
import datetime as dt
import getpass
import json
import os
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_ARCHIVES = Path.home() / 'Library/Developer/Xcode/Archives'
JAVA = '/usr/bin/java'
DWARFDUMP = '/usr/bin/dwarfdump'
# 名称匹配仅用于筛选候选；工具来源仍需由用户确认来自 Bugly 官方。
TOOL_JAR_PATTERN = re.compile(r'bugly[^/]*upload[^/]*symbol[^/]*\.jar$', re.I)


class UserError(Exception):
    """可直接展示且不包含凭据的操作错误。"""


@dataclass(frozen=True)
class Archive:
    path: Path  # .xcarchive 的绝对路径。
    product: Path  # 归档内主应用 .app。
    binary: Path  # 主应用可执行文件。
    dsym: Path  # 主应用对应的 .app.dSYM。
    name: str  # 展示名称，不能用于区分正式包和测试包。
    bundle_id: str  # App 分组与本次凭据复用的依据。
    version: str  # 应用版本号。
    build: str  # 构建编号。
    created_at: dt.datetime  # 带时区的归档时间，用于排序。


@dataclass(frozen=True)
class ToolPackage:
    source: Path  # 用户提供的 ZIP 或 JAR。
    member: Optional[str] = None  # ZIP 内的 JAR 名称；直接提供 JAR 时为空。

    # 只读取所选成员到固定临时文件名，不任意解压 ZIP，也不修改原始下载文件。
    def prepare(self, directory):
        target = directory / 'bugly-upload-symbol.jar'
        if self.member is None:
            shutil.copy2(self.source, target)
        else:
            with zipfile.ZipFile(self.source) as package:
                target.write_bytes(package.read(self.member))
        return target


def inside(parent, child):
    """拒绝归档元数据或符号链接把读取范围引到归档之外。"""
    child = child.resolve()
    try:
        child.relative_to(parent.resolve())
    except ValueError:
        raise UserError('归档中的路径越界：' + str(child)) from None
    return child


# 读取归档与主应用的元数据；文件存在性和 UUID 对应关系留给 validate_archive 检查。
def read_archive(path):
    path = Path(path).expanduser().resolve()
    if path.suffix != '.xcarchive' or not path.is_dir():
        raise UserError('不是有效的 .xcarchive 目录：' + str(path))
    try:
        with inside(path, path / 'Info.plist').open('rb') as source:
            meta = plistlib.load(source)
        if not isinstance(meta, dict) or not isinstance(meta.get('ApplicationProperties'), dict):
            raise UserError('归档信息不是有效的应用归档结构：' + str(path))
        # 不信任 plist 声明的路径；主应用必须位于归档的 Products/Applications 内。
        product_root = inside(path, path / 'Products/Applications')
        product = inside(product_root, path / 'Products' / meta['ApplicationProperties']['ApplicationPath'])
        if product.suffix != '.app':
            raise UserError('归档不包含主应用：' + str(path))
        with inside(product, product / 'Info.plist').open('rb') as source:
            info = plistlib.load(source)
        if not isinstance(info, dict):
            raise UserError('主应用 Info.plist 不是字典结构：' + str(path))
        # 拒绝明确声明其他平台的归档；缺少平台声明时不单凭这一项拒绝。
        platforms = info.get('CFBundleSupportedPlatforms', [])
        if platforms and platforms != ['iPhoneOS']:
            raise UserError('仅支持 iOS 真机归档：' + str(path))
        fields = [info.get(key, '') for key in (
            'CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion', 'CFBundleExecutable')]
        if not all(isinstance(value, str) and value.strip() for value in fields):
            raise UserError('归档缺少 Bundle ID、版本、Build 或可执行文件信息：' + str(path))
        bundle, version, build, executable = (value.strip() for value in fields)
        # 可执行文件名以 CFBundleExecutable 为准，不依赖应用显示名。
        binary = inside(product, product / executable)
        dsym = inside(path, path / 'dSYMs' / (product.name + '.dSYM'))
        # 最新归档以 CreationDate 为准，不用版本号或文件复制时间替代。
        created = meta.get('CreationDate')
        if not isinstance(created, dt.datetime):
            raise UserError('归档缺少 CreationDate，无法可靠判断归档顺序：' + str(path))
        # plist 的无时区日期按 UTC 解释，再转换成本机时区显示。
        if created.tzinfo is None:
            created = created.replace(tzinfo=dt.timezone.utc)
        return Archive(path, product, binary, dsym,
                       str(info.get('CFBundleDisplayName') or info.get('CFBundleName') or product.stem),
                       bundle, version, build, created.astimezone())
    except (OSError, KeyError, TypeError, ValueError, plistlib.InvalidFileException) as error:
        raise UserError('无法读取归档（' + type(error).__name__ + '）：' + str(path)) from None


# 时间相同时按路径稳定排序；版本号不能代表归档的新旧。
def latest_first(archives):
    return sorted(archives, key=lambda item: (item.created_at, str(item.path)), reverse=True)


# 坏归档先记录错误，继续发现其他归档；是否允许继续由 main 按运行模式决定。
def discover_archives(roots):
    archives, errors, candidates = [], [], set()
    for value in roots:
        root = Path(value).expanduser().resolve()
        if not root.is_dir():
            errors.append('归档目录不存在：' + str(root))
            continue
        if root.suffix == '.xcarchive':
            candidates.add(root)
            continue
        def walk_error(error):
            errors.append('无法读取目录：' + str(error.filename))
        # 不进入目录链接；发现归档后剪枝，避免继续扫描归档内的 dSYM、Framework 等内容。
        for current, directories, _ in os.walk(root, followlinks=False, onerror=walk_error):
            for name in list(directories):
                if name.endswith('.xcarchive'):
                    candidates.add((Path(current) / name).resolve())
                    directories.remove(name)
    for path in sorted(candidates):
        try:
            archives.append(read_archive(path))
        except UserError as error:
            errors.append(str(error))
    return latest_first(archives), errors


# 读取全部 (UUID, 架构)；相同版本号不代表来自同一次构建。
def uuid_set(path):
    try:
        result = subprocess.run([DWARFDUMP, '--uuid', str(path)],
                                capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise UserError('无法执行 UUID 检查（' + type(error).__name__ + '）：' + str(path)) from None
    values = set(re.findall(r'UUID: ([0-9A-Fa-f-]+) \(([^)]+)\)', result.stdout))
    if result.returncode != 0 or not values:
        raise UserError('无法读取 UUID：' + str(path))
    return {(value.upper(), arch) for value, arch in values}


def validate_symbol_members(dsym):
    """不跟随 dSYM 内部链接，防止把归档外文件带入上传副本。"""
    try:
        if not stat.S_ISDIR(Path(dsym).lstat().st_mode):
            raise UserError('dSYM 必须是实际目录，不能是符号链接：' + str(dsym))
    except OSError:
        raise UserError('无法检查 dSYM 目录：' + str(dsym)) from None
    # 任何成员读不到都不能忽略：上传输入必须完整通过检查。
    def walk_error(error):
        raise UserError('无法检查 dSYM 内容：' + str(error.filename))
    for current, directories, files in os.walk(dsym, followlinks=False, onerror=walk_error):
        for name in directories + files:
            member = Path(current) / name
            try:
                mode = member.lstat().st_mode
            except OSError:
                raise UserError('无法检查 dSYM 成员：' + str(member)) from None
            if stat.S_ISLNK(mode):
                raise UserError('dSYM 内含符号链接，请使用完整原始符号表：' + str(member))
            if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise UserError('dSYM 内含非普通文件：' + str(member))


# 先检查元数据/路径快照，再要求主程序和 dSYM 的全部 UUID/架构完全一致。
# 快照比较不是对整个归档逐字节校验。
def validate_archive(archive):
    if read_archive(archive.path) != archive:
        raise UserError('归档在选择后发生变化，请重新选择：' + str(archive.path))
    if not archive.binary.is_file() or not archive.dsym.is_dir():
        raise UserError('归档缺少主程序或对应的 .app.dSYM：' + str(archive.path))
    validate_symbol_members(archive.dsym)
    binaries, symbols = uuid_set(archive.binary), uuid_set(archive.dsym)
    if binaries != symbols:
        raise UserError('主程序与 dSYM 的 UUID/架构不一致：' + str(archive.path))
    return symbols


def parse_selection(text, count):
    """用户输入从 1 开始；返回去重且保留输入顺序的下标。"""
    text = text.strip().lower().replace('，', ',')
    if text in ('all', '全部'):
        return list(range(count))
    if not text:
        raise UserError('请输入编号，例如 1,3 或 1-3')
    selected = []
    for token in text.split(','):
        match = re.fullmatch(r'\s*(\d+)\s*(?:-\s*(\d+)\s*)?', token)
        if not match:
            raise UserError('编号格式不正确：' + token)
        start, end = int(match.group(1)), int(match.group(2) or match.group(1))
        if start < 1 or end > count or end < start:
            raise UserError('编号超出范围：' + token)
        for index in range(start - 1, end):
            if index not in selected:
                selected.append(index)
    return selected


def ask_selection(prompt, count, default=None):
    while True:
        answer = input(prompt).strip()
        if not answer and default is not None:
            answer = default
        try:
            return parse_selection(answer, count)
        except UserError as error:
            print(str(error))


def archive_label(archive):
    return '{} {}（{}） | {} | {}'.format(
        archive.name, archive.version, archive.build,
        archive.created_at.strftime('%Y-%m-%d %H:%M:%S %z'), archive.bundle_id)


# 按 Bundle ID 分组，避免把显示名相同的正式包和测试包混为同一 App。
def choose_archives(archives):
    groups = {}
    for archive in latest_first(archives):
        groups.setdefault(archive.bundle_id, []).append(archive)
    bundles = sorted(groups)
    print('\n选择 App（按 Bundle ID 区分，测试包也会独立列出）：')
    for index, bundle in enumerate(bundles, 1):
        group = groups[bundle]
        print('{}. {} | {} | {} 份归档'.format(index, group[0].name, bundle, len(group)))
    choices = ask_selection('App 编号，可多选，例如 1,3；all 表示全部：', len(bundles))
    selected = []
    for index in choices:
        group = groups[bundles[index]]
        print('\n{}：归档时间倒序，第一项不一定是最高版本号。'.format(bundles[index]))
        for number, archive in enumerate(group, 1):
            print('{}. {}\n   {}'.format(number, archive_label(archive), archive.path))
        versions = ask_selection('归档编号，可多选；直接回车选择 1（时间最新）：', len(group), '1')
        selected.extend(group[number] for number in versions)
    return selected


# 仅检查名称与 ZIP/JAR 结构，不能据此验证官方来源或数字签名。
def inspect_tool(path):
    path = Path(path).expanduser().resolve()
    try:
        if path.suffix.lower() not in ('.jar', '.zip'):
            raise UserError('上传工具必须是官方 .jar 或 .zip：' + str(path))
        with zipfile.ZipFile(path) as package:
            if path.suffix.lower() == '.jar':
                if 'META-INF/MANIFEST.MF' not in package.namelist():
                    raise UserError('JAR 缺少清单文件：' + str(path))
                return ToolPackage(path)
            matches = [item for item in package.infolist()
                       if not item.is_dir() and not item.filename.startswith('__MACOSX/')
                       and TOOL_JAR_PATTERN.fullmatch(Path(item.filename).name)]
            # ZIP 内必须恰好有一份可识别且非空的上传 JAR，避免自动选错版本。
            if len(matches) != 1 or matches[0].file_size == 0:
                raise UserError('ZIP 必须只含一份可识别的 Bugly 上传 JAR，请用 --tool 指定正确文件：' + str(path))
            return ToolPackage(path, matches[0].filename)
    except (OSError, zipfile.BadZipFile) as error:
        raise UserError('无法读取上传工具（' + type(error).__name__ + '）：' + str(path)) from None


# 明确指定的工具无效时直接失败，不自动换成其他文件。
def choose_tool(explicit):
    if explicit:
        return inspect_tool(explicit)
    candidates = set()
    roots = (Path(__file__).resolve().parent, Path(__file__).resolve().parent / 'tools', Path.home() / 'Downloads')
    for root in roots:
        if not root.is_dir():
            continue
        for pattern in ('bugly*upload*symbol*.zip', 'bugly*upload*symbol*.jar', 'bugly*/*upload*symbol*.jar'):
            candidates.update(item.resolve() for item in root.glob(pattern) if item.is_file())
    packages = []
    for candidate in sorted(candidates):
        try:
            packages.append(inspect_tool(candidate))
        except UserError as error:
            print('跳过工具：' + str(error), file=sys.stderr)
    if not packages:
        raise UserError('未找到官方 Bugly 上传工具；请下载官方 ZIP/JAR，并通过 --tool 指定路径')
    if len(packages) == 1:
        return packages[0]
    print('\n找到多份上传工具，请选择本次使用的一份：')
    for index, package in enumerate(packages, 1):
        print('{}. {}'.format(index, package.source))
    while True:
        selected = ask_selection('工具编号：', len(packages))
        if len(selected) == 1:
            return packages[selected[0]]
        print('每次只能选择一份工具。')


# 只替换凭据完整原值，不识别编码、截断或其他未知敏感信息；不改变进程参数可见性。
def safe_log(text, app_id, app_key):
    # 先替换长值，避免短值与长值重叠时留下未脱敏的后缀。
    for secret in sorted((app_id, app_key), key=len, reverse=True):
        if secret:
            text = text.replace(secret, '[已隐藏]')
    return text


# 工具可能失败却退出 0：还须有服务状态且全部为 0、有成功文字、无失败标记。
# 这里只判断工具输出；Bugly 网页中的版本与 UUID 仍需人工核对。
def upload_succeeded(exit_code, text):
    statuses = re.findall(r'\bstatusCode\b[\s"\x27]*[:=][\s"\x27]*(-?\d+)\b', text)
    failure_markers = ('上传符号表出错', '上传失败', 'plugin execute result status: failure', '##[error]')
    return (exit_code == 0 and bool(statuses) and all(int(value) == 0 for value in statuses)
            and '上传成功' in text and not any(marker in text for marker in failure_markers))


# 仅检查输入形式，不验证 Key 真伪、权限或与 Bundle ID 的对应关系。
def ask_credentials(archive):
    print('\n请输入此 Bugly 应用的配置：{} | {}'.format(archive.name, archive.bundle_id))
    app_id = input('Bugly App ID：').strip()
    # 隐藏输入回显，不代表 Java 运行时的命令行参数对系统观察者不可见。
    app_key = getpass.getpass('Bugly App Key（输入时不显示）：').strip()
    if any(not value or value.startswith('-') or any(char.isspace() or ord(char) < 32 or ord(char) == 127
                                                    for char in value) for value in (app_id, app_key)):
        raise UserError('App ID / App Key 为空或含不合法字符，未发起上传')
    return app_id, app_key


# 上传输入使用临时副本；工具工作目录放在临时区域，避免污染原始归档和 dSYM。
def upload_one(archive, uuids, jar, work, log_path, credentials):
    staged = work / archive.dsym.name
    validate_symbol_members(archive.dsym)
    # 复制时不展开链接；复制后检查成员与 UUID 是否仍符合核验要求。
    shutil.copytree(archive.dsym, staged, symlinks=True)
    validate_symbol_members(staged)
    if uuid_set(staged) != uuids:
        raise UserError('临时副本 UUID 与已核验内容不一致，未发起上传')
    app_id, app_key = credentials
    # App Key 会出现在 Java 进程参数中，不得打印 command；日志脱敏不能消除这种可见性。
    command = [JAVA, '-jar', str(jar), '-appid', app_id, '-appkey', app_key,
               '-version', archive.version, '-platform', 'IOS', '-inputSymbol', str(staged)]
    process, output = None, []
    try:
        # 从此处启动实际上传；Popen 返回不代表服务端已经接收或上传成功。
        process = subprocess.Popen(command, cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace')
        with log_path.open('w', encoding='utf-8') as log:
            for line in process.stdout:
                # 必须先脱敏再展示和保存，不输出原始进程日志。
                clean = safe_log(line, app_id, app_key)
                output.append(clean)
                print(clean, end='', flush=True)
                log.write(clean)
                log.flush()
        exit_code = process.wait()
    finally:
        # 异常或中断时也终止并回收子进程，避免遗留上传任务。
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        # 减少列表持有凭据的时间，不等于可靠内存擦除。
        command.clear()
    if not upload_succeeded(exit_code, ''.join(output)):
        raise UserError('未取得完整成功证据；请检查脱敏日志和 Bugly 后台后再决定是否重试')


# 按选择顺序上传；单项失败停止后续任务，返回状态仅代表工具端证据。
def upload_selected(selected, verified, tool, output_parent):
    output_parent = Path(output_parent).expanduser().resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    # 结果目录持久保留，独立于稍后自动清理的上传工作目录。
    output_dir = Path(tempfile.mkdtemp(prefix='Bugly上传结果-' + dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-',
                                     dir=output_parent))
    report_path = output_dir / '上传结果.json'
    # 报告不保存凭据；脚本没有网页核验步骤，console_verified 始终保持 False。
    report = {'created_at': dt.datetime.now().astimezone().isoformat(), 'apps': [
        {'app': item.name, 'bundle_id': item.bundle_id, 'version': item.version, 'build': item.build,
         'archive': str(item.path), 'uuids': [{'uuid': value, 'arch': arch} for value, arch in sorted(verified[item.path])],
         'status': '未开始', 'console_verified': False} for item in selected]}
    def save_report():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # 上传前先保存初始状态，准备工具失败时也留有结果记录。
    save_report()
    print('\n脱敏结果目录：' + str(output_dir), flush=True)
    # 同一 Bundle ID 在本次运行中复用凭据，不持久保存。
    credentials = {}
    try:
        with tempfile.TemporaryDirectory(prefix='bugly-user-upload-') as temp:
            temp = Path(temp)
            jar = tool.prepare(temp)
            for index, archive in enumerate(selected):
                item = report['apps'][index]
                item['status'] = '准备上传，尚未确认成功'
                save_report()
                print('\n上传 {}：{}'.format(index + 1, archive_label(archive)), flush=True)
                try:
                    if archive.bundle_id not in credentials:
                        credentials[archive.bundle_id] = ask_credentials(archive)
                    # 每份归档使用独立工作目录，避免同名 dSYM 或中间文件互相覆盖。
                    work = temp / str(index)
                    work.mkdir(mode=0o700)
                    upload_one(archive, verified[archive.path], jar, work,
                               output_dir / ('{:02d}.log'.format(index + 1)), credentials[archive.bundle_id])
                    item['status'] = '上传工具返回成功，待网页核验版本和 UUID'
                except KeyboardInterrupt:
                    # 中断时服务器可能已收到数据，需要核对后台后再决定是否重试。
                    item['status'] = '用户中断；是否已上传需核对 Bugly 后台'
                    raise
                except Exception as error:
                    item['status'] = '未确认成功；后续归档未继续上传'
                    item['error_type'] = type(error).__name__
                    # 第三方异常可能携带进程参数，只展示友好业务错误或未知错误的类型。
                    message = str(error) if isinstance(error, UserError) else type(error).__name__
                    print('已停止：' + message, file=sys.stderr)
                    return 1
                finally:
                    # 成功、失败或中断都尝试保存最新进度。
                    save_report()
    finally:
        # 释放本次缓存，不保证字符串已从内存擦除或进程参数不再可见。
        credentials.clear()
        print('结果文件：' + str(report_path))
    print('所选归档均已取得工具成功结果。请在 Bugly 符号表列表核对版本和 UUID；网页核验尚未完成。')
    return 0


# 总入口：先完成所有所选归档的核验，再开始任何上传。
# --list / --check 在凭据读取与上传之前返回。
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--list', action='store_true', help='列出归档，不读取凭据、不上传')
    action.add_argument('--check', action='store_true', help='核验所有发现或明确指定的归档，不读取凭据、不上传')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--archive', action='append', type=Path, help='指定 .xcarchive，可重复')
    source.add_argument('--archives-dir', action='append', type=Path, help='归档搜索根目录，可重复；默认 Xcode Archives')
    parser.add_argument('--tool', type=Path, help='指定官方上传工具 ZIP/JAR；默认在工具目录和 Downloads 查找')
    parser.add_argument('--output-dir', type=Path, default=Path.home() / 'Desktop', help='脱敏结果父目录，默认桌面')
    args = parser.parse_args(argv)
    archives, errors = discover_archives(args.archive or args.archives_dir or [DEFAULT_ARCHIVES])
    for message in errors:
        print('跳过：' + message, file=sys.stderr)
    if not archives:
        raise UserError('没有可用的 iOS .xcarchive，请检查目录或使用 --archive 指定归档')
    # 明确指定的归档必须全部可读，不能静默漏掉坏归档后继续上传。
    if args.archive and errors:
        raise UserError('明确指定的归档中有读取失败项，本次不会继续上传其余归档')
    if args.list:
        for index, archive in enumerate(archives, 1):
            print('{}. {}\n   {}'.format(index, archive_label(archive), archive.path))
        print('共 {} 份归档、{} 个 Bundle ID；未上传。'.format(len(archives), len({item.bundle_id for item in archives})))
        return 1 if errors else 0
    if not args.check and not sys.stdin.isatty():
        raise UserError('上传需要在交互式终端运行；自动核验请使用 --check')
    selected = archives if args.check or args.archive else choose_archives(archives)
    verified, failed = {}, []
    for archive in selected:
        try:
            verified[archive.path] = validate_archive(archive)
            print('核验通过：{}\n   UUID：{}'.format(archive_label(archive),
                  '; '.join('{} ({})'.format(value, arch) for value, arch in sorted(verified[archive.path]))))
        except UserError as error:
            failed.append(str(error))
            print('核验失败：' + str(error), file=sys.stderr)
    # 任一所选归档核验失败就阻止整批上传；--check 也不能忽略扫描错误。
    if failed or (args.check and errors):
        raise UserError('部分归档未通过核验，未发起任何上传')
    if args.check:
        # --check 只在明确指定工具时检查其结构，不执行 Java 或联网。
        if args.tool:
            print('工具包可读取：' + str(inspect_tool(args.tool).source))
        print('CHECK_OK：归档检查通过；未读取凭据、未联网上传。')
        return 0
    tool = choose_tool(args.tool)
    try:
        subprocess.run([JAVA, '-version'], capture_output=True, check=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        raise UserError('Java 不可用，请安装兼容官方上传工具的 Java 后再运行') from None
    print('本次使用工具：' + str(tool.source))
    return upload_selected(selected, verified, tool, args.output_dir)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print('\n已中断。', file=sys.stderr)
        raise SystemExit(130)
    except UserError as error:
        print('未完成：' + str(error), file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        # 未知异常可能包含凭据或命令参数，兜底只展示错误类型。
        print('未完成：' + type(error).__name__ + '；未输出可能含凭据的原始异常内容。', file=sys.stderr)
        raise SystemExit(1)
