"""命令行入口"""
import argparse
import sys
from pathlib import Path

from .organizer import (
    scan_directory,
    organize_by_type,
    organize_by_date,
    clean_junk,
)


def main():
    parser = argparse.ArgumentParser(
        prog="desktop-organizer",
        description="桌面文件自动整理工具 — 按类型、按日期分文件夹，清理垃圾文件",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=str(Path.home() / "Desktop"),
        help="要整理的目录路径（默认：桌面）",
    )
    parser.add_argument(
        "--mode",
        choices=["type", "date"],
        default="type",
        help="整理模式：type=按类型，date=按日期（默认：type）",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理垃圾文件（.tmp, .bak, .old 等）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示计划，不实际移动文件",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()
    source = Path(args.source)

    if not source.exists():
        print(f"错误：目录不存在 {source}", file=sys.stderr)
        sys.exit(1)

    if not source.is_dir():
        print(f"错误：{source} 不是目录", file=sys.stderr)
        sys.exit(1)

    print(f"扫描目录: {source}")
    files = scan_directory(source)
    print(f"找到 {len(files)} 个文件")

    if args.clean:
        print("\n=== 清理垃圾文件 ===")
        if args.dry_run:
            junk = [f.name for f in source.iterdir() if f.is_file() and (
                f.suffix.lower() in [".tmp", ".bak", ".old", ".cache"] or
                f.name.lower() in ["desktop.ini", "thumbs.db"]
            )]
            if junk:
                for j in junk:
                    print(f"  将删除: {j}")
            else:
                print("  没有垃圾文件")
        else:
            junk = clean_junk(source)
            if junk:
                for j in junk:
                    print(f"  已删除: {j}")
            else:
                print("  没有垃圾文件")
        files = scan_directory(source)

    if not files:
        print("\n没有文件需要整理")
        return

    mode_name = "类型" if args.mode == "type" else "日期"
    print(f"\n=== 按{mode_name}整理 ===")

    if args.dry_run:
        for f in files:
            if args.mode == "type":
                print(f"  {f['name']} → {f['type']}/")
            else:
                print(f"  {f['name']} → {f['modified'].strftime('%Y-%m')}/")
        print(f"\n[试运行] 共 {len(files)} 个文件将被移动")
    else:
        if args.mode == "type":
            moved = organize_by_type(files, source)
        else:
            moved = organize_by_date(files, source)
        print(f"\n完成！移动了 {moved} 个文件")


if __name__ == "__main__":
    main()
