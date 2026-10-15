#!/usr/bin/env python3
"""使用临时归档和 mock 验证上传边界；不联网、不调用真实上传工具。"""

import datetime
import contextlib
import io
import json
import plistlib
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import bugly_upload as subject


ARM_UUID = "01234567-89AB-CDEF-0123-456789ABCDEF"
X86_UUID = "FEDCBA98-7654-3210-FEDC-BA9876543210"
OTHER_UUID = "11111111-2222-3333-4444-555555555555"
ARM_SYMBOL = (ARM_UUID, "arm64")
X86_SYMBOL = (X86_UUID, "x86_64")
SUCCESS_OUTPUT = 'response: {"statusCode": 0}\n上传成功\n'
VALIDATION_ERRORS = subject.UserError


class ArchiveFixtureMixin:
    """提供最小 Xcode 归档，所有测试文件都位于临时目录。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bugly-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive_fixture(self, label="Example", bundle="com.example.app",
                        version="1.0", build="1", created_at=None):
        archive = self.root / (label + ".xcarchive")
        product = archive / "Products" / "Applications" / "Example.app"
        product.mkdir(parents=True)
        info = {
            "CFBundleDisplayName": "测试应用",
            "CFBundleName": "Example",
            "CFBundleIdentifier": bundle,
            "CFBundleShortVersionString": version,
            "CFBundleVersion": build,
            "CFBundleExecutable": "Example",
        }
        self.write_plist(product / "Info.plist", info)
        (product / "Example").write_bytes(b"mock Mach-O binary")
        dwarf = archive / "dSYMs" / "Example.app.dSYM" / "Contents" / "Resources" / "DWARF"
        dwarf.mkdir(parents=True)
        (dwarf / "Example").write_bytes(b"mock DWARF symbols")
        metadata = {
            "CreationDate": created_at or datetime.datetime(2026, 9, 14, 9, 49),
            "Name": "Example",
            "ApplicationProperties": {
                "ApplicationPath": "Applications/Example.app",
                "CFBundleIdentifier": bundle,
                "CFBundleShortVersionString": version,
                "CFBundleVersion": build,
            },
        }
        self.write_plist(archive / "Info.plist", metadata)
        return archive

    @staticmethod
    def write_plist(path, value):
        with path.open("wb") as stream:
            plistlib.dump(value, stream)

    @staticmethod
    def read_plist(path):
        with path.open("rb") as stream:
            return plistlib.load(stream)


class ArchiveFixtureTests(ArchiveFixtureMixin, unittest.TestCase):
    """验证归档边界，以及版本选择不会混淆不同应用。"""

    def test_read_archive_reads_product_metadata(self):
        path = self.archive_fixture(version="4.2.10", build="7")
        archive = subject.read_archive(path)
        self.assertEqual(archive.path, path.resolve())
        self.assertEqual(archive.bundle_id, "com.example.app")
        self.assertEqual(archive.version, "4.2.10")
        self.assertEqual(archive.build, "7")
        self.assertEqual(archive.binary.name, "Example")
        self.assertEqual(archive.dsym.name, "Example.app.dSYM")

    def test_latest_first_uses_archive_date_instead_of_version_number(self):
        older = subject.read_archive(self.archive_fixture(
            label="HigherVersion", version="4.3.0",
            created_at=datetime.datetime(2026, 9, 11, 1, 18)))
        newer = subject.read_archive(self.archive_fixture(
            label="LaterArchive", version="4.2.10",
            created_at=datetime.datetime(2026, 9, 11, 9, 49)))
        ordered = subject.latest_first([older, newer])
        self.assertEqual([item.version for item in ordered], ["4.2.10", "4.3.0"])

    def test_discovery_keeps_apps_with_same_name_and_different_bundle_ids(self):
        self.archive_fixture(label="Alpha", bundle="com.example.alpha")
        self.archive_fixture(label="Beta", bundle="com.example.beta")
        archives, errors = subject.discover_archives([self.root])
        self.assertEqual(errors, [])
        self.assertEqual(len(archives), 2)
        self.assertEqual({item.bundle_id for item in archives}, {
            "com.example.alpha", "com.example.beta"})
        self.assertEqual(len(subject.latest_first(archives)), 2)

    def test_discovery_reports_bad_archive_without_hiding_valid_archive(self):
        self.archive_fixture(label="Valid")
        (self.root / "Broken.xcarchive").mkdir()
        archives, errors = subject.discover_archives([self.root])
        self.assertEqual(len(archives), 1)
        self.assertTrue(errors)

    def test_discovery_deduplicates_overlapping_search_roots(self):
        path = self.archive_fixture()
        archives, errors = subject.discover_archives([self.root, path])
        self.assertEqual(len(archives), 1)
        self.assertEqual(errors, [])

    def test_application_path_cannot_escape_archive(self):
        path = self.archive_fixture()
        metadata = self.read_plist(path / "Info.plist")
        metadata["ApplicationProperties"]["ApplicationPath"] = "../../Outside.app"
        outside = self.root / "Outside.app"
        outside.mkdir()
        self.write_plist(outside / "Info.plist", {
            "CFBundleIdentifier": "com.example.escape",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1",
            "CFBundleExecutable": "Outside",
        })
        (outside / "Outside").write_bytes(b"outside binary")
        self.write_plist(path / "Info.plist", metadata)
        with self.assertRaises(VALIDATION_ERRORS):
            subject.read_archive(path)

    def test_symlink_product_cannot_escape_archive(self):
        path = self.archive_fixture()
        product = path / "Products" / "Applications" / "Example.app"
        external = self.root / "Outside.app"
        product.rename(external)
        product.symlink_to(external, target_is_directory=True)
        with self.assertRaises(VALIDATION_ERRORS):
            subject.read_archive(path)

    def test_executable_path_cannot_escape_archive(self):
        path = self.archive_fixture()
        product = path / "Products" / "Applications" / "Example.app"
        info = self.read_plist(product / "Info.plist")
        outside = self.root / "OutsideBinary"
        outside.write_bytes(b"outside binary")
        info["CFBundleExecutable"] = str(outside)
        self.write_plist(product / "Info.plist", info)
        with self.assertRaises(VALIDATION_ERRORS):
            subject.read_archive(path)

    def test_matching_multi_arch_uuids_pass(self):
        archive = subject.read_archive(self.archive_fixture())
        expected = {ARM_SYMBOL, X86_SYMBOL}
        with mock.patch.object(subject, "uuid_set", side_effect=[expected, expected]):
            self.assertEqual(subject.validate_archive(archive), expected)

    def test_uuid_mismatch_rejects_same_architecture(self):
        archive = subject.read_archive(self.archive_fixture())
        with mock.patch.object(subject, "uuid_set", side_effect=[
                {ARM_SYMBOL}, {(OTHER_UUID, "arm64")}]):
            with self.assertRaises(VALIDATION_ERRORS):
                subject.validate_archive(archive)

    def test_missing_architecture_rejects_partial_uuid_match(self):
        archive = subject.read_archive(self.archive_fixture())
        with mock.patch.object(subject, "uuid_set", side_effect=[
                {ARM_SYMBOL, X86_SYMBOL}, {ARM_SYMBOL}]):
            with self.assertRaises(VALIDATION_ERRORS):
                subject.validate_archive(archive)

    def test_dsym_external_symlink_is_rejected_before_uuid_validation(self):
        archive = subject.read_archive(self.archive_fixture())
        outside = self.root / "private-source.txt"
        outside.write_text("fixture outside the symbol bundle", encoding="utf-8")
        (archive.dsym / "unexpected-member").symlink_to(outside)
        with mock.patch.object(subject, "uuid_set", return_value={ARM_SYMBOL}) as verify:
            with self.assertRaises(VALIDATION_ERRORS):
                subject.validate_archive(archive)
        verify.assert_not_called()


class UUIDParsingTests(unittest.TestCase):
    """mock dwarfdump 的标准输出，避免依赖本机 Xcode 工具链。"""

    def test_uuid_parser_normalizes_case_and_preserves_architecture(self):
        output = (
            f"UUID: {ARM_UUID.lower()} (arm64) /tmp/Example\n"
            f"UUID: {X86_UUID} (x86_64) /tmp/Example\n"
        )
        result = subprocess.CompletedProcess([], 0, stdout=output, stderr="")
        with mock.patch.object(subject.subprocess, "run", return_value=result):
            self.assertEqual(subject.uuid_set(Path("/tmp/Example")), {ARM_SYMBOL, X86_SYMBOL})

    def test_empty_dwarfdump_output_is_rejected(self):
        result = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with mock.patch.object(subject.subprocess, "run", return_value=result):
            with self.assertRaises(VALIDATION_ERRORS):
                subject.uuid_set(Path("/tmp/Example"))


class SelectionTests(unittest.TestCase):
    def test_all_selects_each_item(self):
        self.assertEqual(subject.parse_selection("all", 4), [0, 1, 2, 3])

    def test_commas_ranges_and_duplicates(self):
        self.assertEqual(subject.parse_selection("1, 3-4, 3", 5), [0, 2, 3])

    def test_invalid_or_out_of_range_selection_is_rejected(self):
        for value in ("0", "6", "1-6", "-1", "4-2", "abc", ""):
            with self.subTest(value=value):
                with self.assertRaises(VALIDATION_ERRORS):
                    subject.parse_selection(value, 5)


class UploadResultTests(unittest.TestCase):
    """exit 0、部分成功和旧成功行都不足以证明整个上传成功。"""

    def test_success_requires_exit_zero_and_both_success_markers(self):
        self.assertTrue(subject.upload_succeeded(0, SUCCESS_OUTPUT))
        self.assertFalse(subject.upload_succeeded(1, SUCCESS_OUTPUT))
        self.assertFalse(subject.upload_succeeded(0, ""))
        self.assertFalse(subject.upload_succeeded(0, '{"statusCode": 0}\n'))
        self.assertFalse(subject.upload_succeeded(0, "上传成功\n"))

    def test_failure_markers_override_previous_success(self):
        for failure in (
            "上传符号表出错",
            "plugin execute result status: failure",
            '{"statusCode": 1001}',
            '{"statusCode": -1}',
        ):
            with self.subTest(failure=failure):
                self.assertFalse(subject.upload_succeeded(0, SUCCESS_OUTPUT + failure + "\n"))

    def test_nonzero_status_alone_never_succeeds(self):
        self.assertFalse(subject.upload_succeeded(0, '{"statusCode": 10}\n上传成功\n'))

    def test_safe_log_redacts_overlapping_secrets_in_longest_first_order(self):
        app_id = "12345"
        app_key = "12345-secret-key"
        clean = subject.safe_log(f"id={app_id}; key={app_key}; key={app_key}", app_id, app_key)
        self.assertNotIn(app_id, clean)
        self.assertNotIn(app_key, clean)
        self.assertNotIn("-secret-key", clean)
        self.assertIn("id=", clean)

    def test_safe_log_ignores_empty_secrets(self):
        self.assertEqual(subject.safe_log("ordinary output", "", ""), "ordinary output")


class ToolPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bugly-tool-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def jar_bytes():
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as jar:
            jar.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
            jar.writestr("Example.class", b"mock class")
        return output.getvalue()

    def test_direct_jar_is_supported(self):
        path = self.root / "buglyqq-upload-symbol.jar"
        path.write_bytes(self.jar_bytes())
        self.assertIsNotNone(subject.inspect_tool(path))

    def test_zip_discovers_unique_official_jar_without_fixed_version(self):
        path = self.root / "bugly-tool-v99.zip"
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("bugly-v99/tools/buglyqq-upload-symbol.jar", self.jar_bytes())
            package.writestr("bugly-v99/README.txt", "fixture")
        self.assertIsNotNone(subject.inspect_tool(path))

    def test_multiple_candidate_jars_are_rejected(self):
        path = self.root / "ambiguous.zip"
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("old/buglyqq-upload-symbol.jar", self.jar_bytes())
            package.writestr("new/buglyqq-upload-symbol.jar", self.jar_bytes())
        with self.assertRaises(VALIDATION_ERRORS):
            subject.inspect_tool(path)

    def test_zip_without_upload_jar_is_rejected(self):
        path = self.root / "unrelated.zip"
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("unrelated.jar", self.jar_bytes())
        with self.assertRaises(VALIDATION_ERRORS):
            subject.inspect_tool(path)

    def test_empty_jar_is_rejected(self):
        path = self.root / "buglyqq-upload-symbol.jar"
        path.write_bytes(b"")
        with self.assertRaises(VALIDATION_ERRORS):
            subject.inspect_tool(path)


class UploadExecutionTests(ArchiveFixtureMixin, unittest.TestCase):
    """替换进程和凭据输入，验证复制、执行参数与批次报告边界。"""

    def upload_context(self):
        archive = subject.read_archive(self.archive_fixture(version="4.2.10", build="7"))
        work = self.root / "work"
        work.mkdir()
        jar = self.root / "dummy.jar"
        log = self.root / "upload.log"
        credentials = ("fixture-app-id", "fixture-secret-key")
        return archive, work, jar, log, credentials

    def read_report(self):
        paths = list((self.root / "results").glob("*/上传结果.json"))
        self.assertEqual(len(paths), 1)
        return json.loads(paths[0].read_text(encoding="utf-8"))

    def test_upload_one_uses_verified_copy_and_redacts_console_and_log(self):
        archive, work, jar, log, credentials = self.upload_context()
        output = f"arguments: {credentials[0]} {credentials[1]}\n" + SUCCESS_OUTPUT
        captured = {}

        def fake_popen(command, **kwargs):
            # 实际代码会清空 command；在调用时复制，检查真正传给进程的参数。
            captured["command"] = command.copy()
            captured["cwd"] = kwargs["cwd"]
            process = mock.Mock()
            process.stdout = io.StringIO(output)
            process.wait.return_value = 0
            process.poll.return_value = 0
            return process

        console = io.StringIO()
        with mock.patch.object(subject, "uuid_set", return_value={ARM_SYMBOL}) as verify, \
                mock.patch.object(subject.subprocess, "Popen", side_effect=fake_popen), \
                contextlib.redirect_stdout(console):
            subject.upload_one(archive, {ARM_SYMBOL}, jar, work, log, credentials)

        command = captured["command"]
        staged = Path(command[command.index("-inputSymbol") + 1])
        self.assertEqual(command[command.index("-platform") + 1], "IOS")
        self.assertEqual(command[command.index("-version") + 1], "4.2.10")
        self.assertEqual(command[command.index("-jar") + 1], str(jar))
        self.assertEqual(captured["cwd"], work)
        self.assertEqual(staged.parent, work)
        self.assertNotEqual(staged.resolve(), archive.dsym.resolve())
        verify.assert_called_once_with(staged)
        source_files = list(archive.dsym.rglob("Example"))
        self.assertEqual(len(source_files), 1)
        self.assertEqual((staged / source_files[0].relative_to(archive.dsym)).read_bytes(), source_files[0].read_bytes())
        for text in (console.getvalue(), log.read_text(encoding="utf-8")):
            self.assertIn("上传成功", text)
            for secret in credentials:
                self.assertNotIn(secret, text)

    def test_upload_one_exit_zero_without_complete_evidence_raises(self):
        archive, work, jar, log, credentials = self.upload_context()
        process = mock.Mock()
        process.stdout = io.StringIO('{"statusCode": 0}\n')
        process.wait.return_value = 0
        process.poll.return_value = 0
        with mock.patch.object(subject, "uuid_set", return_value={ARM_SYMBOL}), \
                mock.patch.object(subject.subprocess, "Popen", return_value=process), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(VALIDATION_ERRORS):
                subject.upload_one(archive, {ARM_SYMBOL}, jar, work, log, credentials)
        self.assertIn("statusCode", log.read_text(encoding="utf-8"))

    def test_new_symlink_in_copied_dsym_stops_before_uuid_or_java(self):
        archive, work, jar, log, credentials = self.upload_context()
        outside = self.root / "private-source.txt"
        outside.write_text("fixture outside the symbol bundle", encoding="utf-8")
        actual_copytree = subject.shutil.copytree

        def copy_then_add_external_link(source, destination, *args, **kwargs):
            copied = actual_copytree(source, destination, *args, **kwargs)
            # 在源文件检查完成后引入外链，验证副本仍有独立的安全边界。
            if Path(source) == archive.dsym:
                (Path(destination) / "unexpected-member").symlink_to(outside)
            return copied

        with mock.patch.object(subject.shutil, "copytree", side_effect=copy_then_add_external_link), \
                mock.patch.object(subject, "uuid_set", return_value={ARM_SYMBOL}) as verify, \
                mock.patch.object(subject.subprocess, "Popen") as launch:
            with self.assertRaises(VALIDATION_ERRORS):
                subject.upload_one(archive, {ARM_SYMBOL}, jar, work, log, credentials)
        verify.assert_not_called()
        launch.assert_not_called()

    def test_batch_reuses_credentials_per_bundle_and_requires_console_verification(self):
        archives = [
            subject.read_archive(self.archive_fixture(label="AlphaOld", bundle="com.example.alpha", version="1.0")),
            subject.read_archive(self.archive_fixture(label="AlphaNew", bundle="com.example.alpha", version="2.0")),
            subject.read_archive(self.archive_fixture(label="Beta", bundle="com.example.beta")),
        ]
        verified = {archive.path: {ARM_SYMBOL} for archive in archives}
        credentials = [("alpha-id", "alpha-secret"), ("beta-id", "beta-secret")]
        tool = mock.Mock()
        tool.prepare.return_value = self.root / "dummy.jar"
        with mock.patch.object(subject, "ask_credentials", side_effect=credentials) as ask, \
                mock.patch.object(subject, "upload_one") as upload, \
                contextlib.redirect_stdout(io.StringIO()):
            status = subject.upload_selected(archives, verified, tool, self.root / "results")

        self.assertEqual(status, 0)
        self.assertEqual(ask.call_args_list, [mock.call(archives[0]), mock.call(archives[2])])
        self.assertEqual([call.args[-1] for call in upload.call_args_list],
                         [credentials[0], credentials[0], credentials[1]])
        report = self.read_report()
        self.assertEqual(len(report["apps"]), 3)
        for item in report["apps"]:
            self.assertIs(item["console_verified"], False)
            self.assertIn("上传工具返回成功", item["status"])
        report_text = json.dumps(report)
        for pair in credentials:
            for secret in pair:
                self.assertNotIn(secret, report_text)

    def test_batch_failure_stops_following_uploads_and_preserves_partial_report(self):
        archives = [subject.read_archive(self.archive_fixture(
            label=label, bundle="com.example." + label.lower()))
            for label in ("Alpha", "Beta", "Gamma")]
        verified = {archive.path: {ARM_SYMBOL} for archive in archives}
        tool = mock.Mock()
        tool.prepare.return_value = self.root / "dummy.jar"
        with mock.patch.object(subject, "ask_credentials", return_value=("fixture-id", "fixture-key")) as ask, \
                mock.patch.object(subject, "upload_one", side_effect=[None, subject.UserError("模拟上传失败")]) as upload, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = subject.upload_selected(archives, verified, tool, self.root / "results")

        self.assertEqual(status, 1)
        self.assertEqual(upload.call_count, 2)
        self.assertEqual(ask.call_count, 2)
        items = self.read_report()["apps"]
        self.assertEqual(len(items), 3)
        self.assertIn("上传工具返回成功", items[0]["status"])
        self.assertIn("未确认成功", items[1]["status"])
        self.assertEqual(items[1]["error_type"], "UserError")
        self.assertEqual(items[2]["status"], "未开始")
        self.assertTrue(all(item["console_verified"] is False for item in items))


if __name__ == "__main__":
    unittest.main(verbosity=2)
