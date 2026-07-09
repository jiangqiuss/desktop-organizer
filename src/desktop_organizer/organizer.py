"""
桌面文件自动整理工具
功能：按类型、按日期分文件夹，清理垃圾文件
"""
import shutil
from datetime import datetime
from pathlib import Path

# 配置：文件类型 → 文件夹名
FILE_TYPES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff"],
    "文档": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".rtf"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "音乐": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "安装包": [".exe", ".msi", ".dmg", ".deb", ".rpm"],
    "代码": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh", ".bat"],
    "快捷方式": [".lnk", ".url"],
}

JUNK_EXTENSIONS = [".tmp", ".bak", ".old", ".cache"]
JUNK_PATTERNS = ["desktop.ini", "thumbs.db", "~$"]


def get_file_type(ext: str) -> str:
    """根据扩展名返回文件类型"""
    ext = ext.lower()
    for type_name, extensions in FILE_TYPES.items():
        if ext in extensions:
            return type_name
    return "其他"


def resolve_dest(dest: Path) -> Path:
    """处理重名文件，返回不冲突的目标路径"""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while dest.exists():
        dest = dest.parent / f"{stem}_{counter}{suffix}"
        counter += 1
    return dest


def scan_directory(path: Path) -> list[dict]:
    """扫描目录，返回文件信息列表"""
    files = []
    for item in path.iterdir():
        if item.is_file():
            files.append({
                "path": item,
                "name": item.name,
                "ext": item.suffix,
                "size": item.stat().st_size,
                "modified": datetime.fromtimestamp(item.stat().st_mtime),
                "type": get_file_type(item.suffix),
            })
    return files


def organize_by_type(files: list[dict], target_dir: Path) -> int:
    """按类型整理文件"""
    moved = 0
    for f in files:
        type_dir = target_dir / f["type"]
        type_dir.mkdir(exist_ok=True)
        dest = resolve_dest(type_dir / f["name"])
        shutil.move(str(f["path"]), str(dest))
        moved += 1
    return moved


def organize_by_date(files: list[dict], target_dir: Path) -> int:
    """按日期整理文件（年-月）"""
    moved = 0
    for f in files:
        date_dir = target_dir / f["modified"].strftime("%Y-%m")
        date_dir.mkdir(exist_ok=True)
        dest = resolve_dest(date_dir / f["name"])
        shutil.move(str(f["path"]), str(dest))
        moved += 1
    return moved


def clean_junk(path: Path) -> list[str]:
    """清理垃圾文件"""
    cleaned = []
    for item in path.iterdir():
        if item.is_file():
            if item.suffix.lower() in JUNK_EXTENSIONS:
                cleaned.append(item.name)
                item.unlink()
            elif item.name.lower() in [p.lower() for p in JUNK_PATTERNS]:
                cleaned.append(item.name)
                item.unlink()
    return cleaned
