"""Command-line entry point for SAMBU."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .interpreter import execute
from .lexer import SambuSyntaxError
from .runtime import SambuRuntimeError


def _new_project(argv: list[str]) -> int:
    from .project import ProjectGenerationError, create_project

    parser = argparse.ArgumentParser(prog="sambu new")
    parser.add_argument("name", help="lowercase application name, e.g. blog_app")
    parser.add_argument("--path", type=Path, help="destination directory (defaults to NAME)")
    args = parser.parse_args(argv)
    try:
        created = create_project(args.name, args.path)
    except ProjectGenerationError as exc:
        print(f"sambu new: {exc}", file=sys.stderr)
        return 2
    destination = args.path if args.path is not None else Path(args.name)
    print(f"Created SAMBU project {args.name!r} at {destination} ({len(created)} files).")
    print("Run: sambu " + str(destination / "src" / "main.sambu"))
    return 0


def _generate(argv: list[str]) -> int:
    from .project import ProjectGenerationError, generate_scaffold

    parser = argparse.ArgumentParser(prog="sambu generate")
    subparsers = parser.add_subparsers(dest="action", required=True)
    scaffold = subparsers.add_parser("scaffold", help="generate model/controller/view starters")
    scaffold.add_argument("model", help="PascalCase singular model name, e.g. Post")
    scaffold.add_argument("fields", nargs="+", help="field declarations such as title:string")
    scaffold.add_argument("--path", type=Path, default=Path("."), help="SAMBU project root")
    args = parser.parse_args(argv)
    try:
        created = generate_scaffold(args.path, args.model, args.fields)
    except ProjectGenerationError as exc:
        print(f"sambu generate scaffold: {exc}", file=sys.stderr)
        return 2
    print(f"Generated {len(created)} scaffold files for {args.model}.")
    for path in created:
        print(f"  {path}")
    print("Note: generated MVC, routing, ORM and migration files are starters, not an active web runtime.")
    return 0


def _machine(argv: list[str]) -> int:
    import json
    from .machine import SambuMachine

    parser = argparse.ArgumentParser(prog="sambu machine")
    commands = parser.add_subparsers(dest="action", required=True)
    check = commands.add_parser("check", help="parse-check every .sambu file in a workspace")
    check.add_argument("path", type=Path)
    check.add_argument("--json", action="store_true", dest="as_json")
    sample = commands.add_parser("sample", help="take a deterministic sample of typed AST statements")
    sample.add_argument("path", type=Path)
    sample.add_argument("--ratio", type=int, default=100, help="sample one statement per N statements in each file")
    sample.add_argument("--seed", type=int, default=0)
    sample.add_argument("--json", action="store_true", dest="as_json")
    architecture = commands.add_parser("architecture", help="validate the reference plywood layer graph")
    architecture.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    machine = SambuMachine(profile="sealed")
    try:
        if args.action == "check":
            report = machine.check_workspace(args.path)
            if args.as_json:
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"SAMBU Machine: {report.valid_files}/{report.files_checked} source files parsed")
                for issue in report.issues:
                    print(f"{issue.path}:{issue.line}:{issue.column}: {issue.code}: {issue.message}")
                for issue in report.architecture.issues:
                    print(f"architecture: {issue}")
            return 0 if report.valid else 1
        if args.action == "sample":
            report = machine.sample_code(args.path, denominator=args.ratio, seed=args.seed)
            if args.as_json:
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(
                    f"Sampled {report.statements_sampled}/{report.statements_found} AST statements "
                    f"from {report.files_scanned} files at 1:{report.denominator} (seed={report.seed})."
                )
                for item in report.samples:
                    print(f"\n{item.path}:{item.start_line}-{item.end_line} [{item.statement_type}]")
                    print(item.excerpt)
            return 0
        result = machine.inspect_architecture()
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("SAMBU plywood architecture")
            print(" -> ".join(result["order"]))
            for issue in result["issues"]:
                print(f"ERROR: {issue}")
        return 0 if result["valid"] else 1
    except Exception as exc:
        print(f"sambu machine: {exc}", file=sys.stderr)
        return 2



def _device(argv: list[str]) -> int:
    import json
    from .apple_devices import AppleDeviceToolkit

    parser = argparse.ArgumentParser(prog="sambu device")
    commands = parser.add_subparsers(dest="action", required=True)
    diagnose = commands.add_parser("diagnose", help="inspect Apple USB drivers, libimobiledevice and connected devices")
    diagnose.add_argument("--bin-dir", type=Path, help="directory containing idevice_id, ideviceinfo and idevicepair")
    diagnose.add_argument("--udid", help="limit inspection to one already connected device")
    diagnose.add_argument("--lang", choices=("en", "ru"), default="en")
    diagnose.add_argument("--timeout", type=float, default=8.0)
    diagnose.add_argument("--json", action="store_true", dest="as_json")
    smoke = commands.add_parser("test", help="run non-destructive iPhone/iPad hardware smoke tests")
    smoke.add_argument("--bin-dir", type=Path, help="directory containing libimobiledevice tools")
    smoke.add_argument("--udid", help="test one already connected device")
    smoke.add_argument("--lang", choices=("en", "ru"), default="en")
    smoke.add_argument("--timeout", type=float, default=8.0)
    smoke.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        toolkit = AppleDeviceToolkit(
            bin_dir=args.bin_dir,
            language=args.lang,
            timeout=args.timeout,
        )
        if args.action == "diagnose":
            report = toolkit.diagnose(udid=args.udid)
            if args.as_json:
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(toolkit.locale.gettext("report_title"))
                print(f"{toolkit.locale.gettext('platform_label')}: {report.platform}")
                print(f"{toolkit.locale.gettext('tools_label')}:")
                for item in report.tools:
                    state = toolkit.locale.gettext(
                        "tool_state_available" if item.available else "tool_state_missing"
                    )
                    suffix = f" — {item.version}" if item.version else ""
                    print(f"  {item.name}: {state}{suffix}")
                print(f"{toolkit.locale.gettext('devices_label')}: {len(report.devices)}")
                for device in report.devices:
                    print(
                        f"  {device.name or device.udid}: {device.family}; "
                        f"{device.product_type or toolkit.locale.gettext('model_unavailable')}; "
                        f"{toolkit.locale.gettext('device_ios_label')} {device.ios_version or toolkit.locale.gettext('version_unavailable')}; "
                        f"{toolkit.locale.gettext('pairing_label')}={device.pairing_valid}"
                    )
                for item in report.diagnostics:
                    status_key = {
                        "ok": "test_status_ok",
                        "warning": "test_status_warning",
                        "error": "test_status_error",
                        "unsupported": "test_status_unsupported",
                    }.get(item.status, "test_status_warning")
                    print(f"[{toolkit.locale.gettext(status_key)}] {item.message}")
                    if item.recommendation:
                        print(f"  -> {item.recommendation}")
            return 0

        report = toolkit.run_hardware_smoke(udid=args.udid)
        if args.as_json:
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"{toolkit.locale.gettext('smoke_title')} — {report.devices_tested}")
            for item in report.tests:
                suffix = f" [{item.device_udid}]" if item.device_udid else ""
                status_key = {
                    "pass": "test_status_pass",
                    "fail": "test_status_fail",
                    "skip": "test_status_skip",
                    "warn": "test_status_warn",
                }.get(item.status, "test_status_warning")
                print(f"[{toolkit.locale.gettext(status_key)}] {item.name}{suffix}: {item.message}")
        return 0 if report.passed else 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"sambu device: {exc}", file=sys.stderr)
        return 2



def _lexicon(argv: list[str]) -> int:
    import json
    from .articulatory import ARTICULATORY_WORDS, filter_articulatory_words

    parser = argparse.ArgumentParser(prog="sambu lexicon")
    parser.add_argument("--family", help="family code or name, e.g. V or measure")
    parser.add_argument(
        "--status", choices=("active", "keyword", "builtin", "reserved"),
        help="filter by implementation status",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args(argv)
    if isinstance(args.limit, bool) or not 1 <= args.limit <= 200:
        parser.error("--limit must be from 1 to 200")
    try:
        entries = filter_articulatory_words(family=args.family, status=args.status)
    except ValueError as exc:
        parser.error(str(exc))
    selected = entries[:args.limit]
    if args.as_json:
        print(json.dumps(
            [entry.to_dict() for entry in selected],
            ensure_ascii=False,
            indent=2,
        ))
    else:
        print(
            f"SAMBU articulatory lexicon: {len(selected)}/{len(entries)} shown "
            f"({len(ARTICULATORY_WORDS)} total)"
        )
        for entry in selected:
            target = f" -> {entry.target}" if entry.target else ""
            print(
                f"{entry.word:6} {entry.pronunciation:8} "
                f"{entry.status:8} {entry.meaning}{target}"
            )
    return 0


def _ide(argv: list[str]) -> int:
    import json
    from .ide import SambuIDE

    parser = argparse.ArgumentParser(prog="sambu ide")
    commands = parser.add_subparsers(dest="action", required=True)
    inspect = commands.add_parser("inspect", help="inspect one .sambu document")
    inspect.add_argument("path", type=Path)
    inspect.add_argument("--format", choices=("text", "json"), default="text")
    workspace = commands.add_parser("workspace", help="parse-check a .sambu workspace")
    workspace.add_argument("path", type=Path)
    workspace.add_argument("--format", choices=("text", "json"), default="text")
    complete = commands.add_parser("complete", help="list built-in and keyword completions")
    complete.add_argument("prefix", nargs="?", default="")
    complete.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)
    ide = SambuIDE()
    try:
        if args.action == "inspect":
            source = args.path.read_text(encoding="utf-8")
            report = ide.open_document(str(args.path.resolve()), source)
            if args.format == "json":
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"{report.uri} — {'syntax OK' if report.syntax_valid else 'syntax errors'}")
                print(f"Lines: {report.line_count} | tokens: {report.token_count} | SHA-256: {report.sha256}")
                for symbol in report.symbols:
                    print(f"{symbol.kind:10} {symbol.name} ({symbol.start_line}-{symbol.end_line})")
                    for child in symbol.children:
                        print(f"  {child.kind:8} {child.name} ({child.start_line}-{child.end_line})")
                for diagnostic in report.diagnostics:
                    print(
                        f"{diagnostic.line}:{diagnostic.column}: "
                        f"{diagnostic.code}: {diagnostic.message}"
                    )
            return 0 if report.syntax_valid else 1
        if args.action == "workspace":
            report = ide.inspect_workspace(args.path)
            if args.format == "json":
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"SAMBU IDE: {report.valid_files}/{report.files_checked} files parsed")
                for issue in report.issues:
                    print(f"{issue.path}:{issue.line}:{issue.column}: {issue.code}: {issue.message}")
            return 0 if report.valid else 1
        values = ide.complete(args.prefix, limit=args.limit)
        print("\n".join(values))
        return 0
    except Exception as exc:
        print(f"sambu ide: {exc}", file=sys.stderr)
        return 2



def _dialect(argv: list[str]) -> int:
    """Run, check, or emit one of the supported SAMBU dialect profiles."""
    from .dialects import DialectSyntaxError, transpile
    from .parser import parse_ast

    parser = argparse.ArgumentParser(prog="sambu dialect")
    parser.add_argument("profile", choices=("pascal", "delphi", "fortran"))
    parser.add_argument("file", type=Path, help="source file written in the selected dialect subset")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="translate and parse-check without executing")
    mode.add_argument("--show-translated", action="store_true", help="print the generated canonical SAMBU source")
    mode.add_argument("--emit-sambu", type=Path, help="write generated canonical SAMBU source to this path")
    args = parser.parse_args(argv)

    try:
        source = args.file.read_text(encoding="utf-8")
        result = transpile(source, args.profile)
        if args.check:
            parse_ast(result.generated_source)
            print(f"SAMBU {result.dialect} profile: syntax OK ({len(result.source_lines)} generated lines)")
            return 0
        if args.show_translated:
            print(result.generated_source, end="")
            return 0
        if args.emit_sambu is not None:
            args.emit_sambu.write_text(result.generated_source, encoding="utf-8")
            print(f"Generated SAMBU source: {args.emit_sambu}")
            return 0
        execute(result.generated_source)
        return 0
    except (DialectSyntaxError, SambuSyntaxError, SambuRuntimeError, RuntimeError, ValueError, TypeError, ZeroDivisionError, IndexError, AttributeError, OSError) as exc:
        print(f"{args.file}: {exc}", file=sys.stderr)
        return 1



def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "new":
        return _new_project(arguments[1:])
    if arguments and arguments[0] == "generate":
        return _generate(arguments[1:])
    if arguments and arguments[0] == "machine":
        return _machine(arguments[1:])
    if arguments and arguments[0] == "ide":
        return _ide(arguments[1:])
    if arguments and arguments[0] == "device":
        return _device(arguments[1:])
    if arguments and arguments[0] == "lexicon":
        return _lexicon(arguments[1:])
    if arguments and arguments[0] == "dialect":
        return _dialect(arguments[1:])

    parser = argparse.ArgumentParser(
        prog="sambu",
        description="SAMBU — a scientific language and convention-based project toolkit.",
    )
    parser.add_argument("file", nargs="?", help="SAMBU source file (.sambu)")
    parser.add_argument("-c", "--code", help="execute source passed as a string")
    parser.add_argument("--version", action="version", version=f"SAMBU {__version__}")
    args = parser.parse_args(arguments)

    if bool(args.file) == bool(args.code):
        parser.error("provide exactly one source file or -c/--code")

    if args.code is not None:
        source = args.code
        filename = "<command>"
    else:
        path = Path(args.file)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"sambu: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        filename = str(path)

    try:
        execute(source)
    except (SambuSyntaxError, SambuRuntimeError, RuntimeError, ValueError, TypeError, ZeroDivisionError, IndexError, AttributeError) as exc:
        print(f"{filename}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
