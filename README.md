# Desktop Organizer

桌面文件自动整理工具 — 按类型、按日期分文件夹，清理垃圾文件。

## 功能

- **按类型整理**：图片、文档、视频、音乐、压缩包、安装包、代码、快捷方式
- **按日期整理**：按修改日期归档到 `年-月` 文件夹
- **清理垃圾**：删除 `.tmp`、`.bak`、`.old`、`.cache`、`desktop.ini` 等
- **试运行模式**：先预览再执行，避免误操作
- **重名处理**：自动添加序号，不覆盖已有文件

## 安装

```bash
pip install desktop-organizer
```

或从源码安装：

```bash
git clone https://github.com/jiangqiuss/desktop-organizer.git
cd desktop-organizer
pip install -e .
```

## 使用

```bash
# 整理桌面（默认按类型）
desktop-organizer

# 整理指定目录
desktop-organizer D:\Downloads

# 按日期整理
desktop-organizer --mode date

# 先预览再执行
desktop-organizer --dry-run

# 清理垃圾文件
desktop-organizer --clean

# 组合使用
desktop-organizer D:\Downloads --mode type --clean
```

## 示例输出

```
扫描目录: C:\Users\Administrator\Desktop
找到 15 个文件

=== 清理垃圾文件 ===
  已删除: thumbs.db
  已删除: ~$report.docx

=== 按类型整理 ===
  photo.jpg → 图片/
  report.pdf → 文档/
  video.mp4 → 视频/
  music.mp3 → 音乐/
  archive.zip → 压缩包/
  app.exe → 安装包/
  script.py → 代码/
  shortcut.lnk → 快捷方式/

完成！移动了 13 个文件
```

## 文件类型映射

| 类型 | 扩展名 |
|------|--------|
| 图片 | .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .ico, .tiff |
| 文档 | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .md, .csv, .rtf |
| 视频 | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm |
| 音乐 | .mp3, .wav, .flac, .aac, .ogg, .wma |
| 压缩包 | .zip, .rar, .7z, .tar, .gz, .bz2 |
| 安装包 | .exe, .msi, .dmg, .deb, .rpm |
| 代码 | .py, .js, .ts, .java, .c, .cpp, .go, .rs, .html, .css, .json, .xml, .yaml, .yml, .sh, .bat |
| 快捷方式 | .lnk, .url |

## License

MIT
