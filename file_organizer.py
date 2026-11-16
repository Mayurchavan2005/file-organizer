"""
Auto File Organizer - by Mayur
================================================
Sorts the files in a folder (default: Downloads) into
separate folders by file type.

Features:
- Images, Videos, Documents, Music, Archives, Code, Apps, Others
- If a file with the same name already exists, saves it with a
  new name: photo (1).jpg
- --dry-run shows what would happen, without moving anything
- --undo moves files from the last run back to where they were
- Writes a log of every run: organizer_log.txt
- No external library needed, only Python

How to run:
    python file_organizer.py
    python file_organizer.py "C:\\Users\\Mayur\\Downloads"
    python file_organizer.py --dry-run
    python file_organizer.py "D:\\My Files" --dry-run
    python file_organizer.py --undo
    python file_organizer.py --undo --dry-run
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".ico"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".ts"},
    "Apps": {".exe", ".msi"},
}


def get_category(file_path: Path) -> str:
    """Find the category from the file extension."""
    ext = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def get_unique_path(destination: Path) -> Path:
    """If a file with the same name exists, add (1), (2) and so on."""
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = destination.parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def organize(folder: Path, dry_run: bool = False):
    """Main work: sort the files in the folder."""
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return

    print(f"\nOrganizing: {folder}")
    if dry_run:
        print("DRY RUN mode - no files will be moved, only shown\n")

    moved = {}
    skipped = 0
    log_lines = [f"File Organizer Log - {datetime.now()}\nFolder: {folder}\n"]

    files = [p for p in folder.iterdir() if p.is_file()]

    files = [p for p in files if p.name not in ("file_organizer.py", "file_organizer_gui.py", "organizer_log.txt")]

    if not files:
        print("Folder is already clean, no files found!")
        return

    for file_path in files:
        category = get_category(file_path)
        target_folder = folder / category

        if not dry_run:
            target_folder.mkdir(exist_ok=True)

        target_path = get_unique_path(target_folder / file_path.name)

        if dry_run:
            print(f"  {file_path.name}  ->  {category}/")
        else:
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  {file_path.name}  ->  {category}/")
            except Exception as e:
                print(f"  {file_path.name} could not be moved: {e}")
                skipped += 1
                continue

        moved[category] = moved.get(category, 0) + 1
        log_lines.append(f"{file_path.name} -> {category}/{target_path.name}\n")

    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    total = sum(moved.values())
    for category, count in sorted(moved.items()):
        print(f"  {category}: {count} files")
    print(f"  Total: {total} files")
    if skipped:
        print(f"  Skipped: {skipped} files")
    print("=" * 40)

    if not dry_run:
        log_file = folder / "organizer_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.writelines(log_lines + [f"Total moved: {total}\n\n"])
        print(f"\nLog saved to: {log_file}")


def undo(folder: Path, dry_run: bool = False):
    """Move files from the last run back to the folder they came from.

    It reads organizer_log.txt, takes only the last run, and moves each
    file back in reverse order. If a file with the same name is already
    back in the folder, it saves the restored file as photo (1).jpg
    instead of overwriting it. Files that are no longer in their
    category folder are skipped, not treated as an error.
    Returns (moved_back, skipped) so callers such as the GUI can
    report the real result instead of assuming it worked.
    """
    log_file = folder / "organizer_log.txt"
    if not log_file.exists():
        print(f"No log file found: {log_file}")
        print("Nothing to undo. Organize a folder first.")
        return (0, 0)

    lines = log_file.read_text(encoding="utf-8").splitlines()

    runs = []
    current_run = None
    last_undo_after_last_log = False
    for line in lines:
        if line.startswith("File Organizer Log - "):
            current_run = []
            runs.append(current_run)
            last_undo_after_last_log = False
        elif line.startswith("File Organizer Undo - "):
            current_run = None
            last_undo_after_last_log = True
        elif current_run is not None and " -> " in line:
            current_run.append(line.strip())

    if not runs or not runs[-1]:
        print("No moves found in the log. Nothing to undo.")
        return (0, 0)

    if last_undo_after_last_log:
        print("The last run was already undone. Nothing to undo.")
        return (0, 0)

    print(f"\nUndoing last run in: {folder}")
    if dry_run:
        print("DRY RUN mode - no files will be moved, only shown\n")

    moved_back = 0
    skipped = 0
    undo_lines = [f"File Organizer Undo - {datetime.now()}\nFolder: {folder}\n"]

    for move in reversed(runs[-1]):
        original_name, moved_name = move.split(" -> ")
        category, moved_file = moved_name.split("/", 1)
        source = folder / category / moved_file
        target = get_unique_path(folder / original_name)

        if dry_run:
            if not source.exists():
                print(f"  {category}/{moved_file} not found, skipped")
                skipped += 1
                continue
            print(f"  {category}/{moved_file}  ->  {target.name}")
            moved_back += 1
            continue

        if not source.exists():
            print(f"  {category}/{moved_file} not found, skipped")
            skipped += 1
            continue

        try:
            shutil.move(str(source), str(target))
            print(f"  {category}/{moved_file}  ->  {target.name}")
            moved_back += 1
            undo_lines.append(f"{moved_file} -> {target.name}\n")
        except Exception as e:
            print(f"  {moved_file} could not be moved back: {e}")
            skipped += 1

    if not dry_run and moved_back:
        with open(log_file, "a", encoding="utf-8") as f:
            f.writelines(undo_lines + ["\n"])
        print(f"\nUndo saved to: {log_file}")

    print(f"\nMoved back: {moved_back} files")
    if skipped:
        print(f"Skipped: {skipped} files")
    return (moved_back, skipped)


def main():
    parser = argparse.ArgumentParser(description="Auto File Organizer - clean up Downloads!")
    parser.add_argument("folder", nargs="?", default=None,
                        help="Which folder should be organized? (default: Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only show what would happen, move no files")
    parser.add_argument("--undo", action="store_true",
                        help="Move files from the last run back to where they were")
    args = parser.parse_args()

    if args.folder:
        folder = Path(args.folder)
    elif args.undo:
        folder = Path.home() / "Downloads"
    else:
        folder = Path.home() / "Downloads"
        user_input = input(f"Organize this folder? [{folder}] (Enter = Yes, or type a new path): ").strip()
        if user_input:
            folder = Path(user_input)

    if args.undo:
        undo(folder, dry_run=args.dry_run)
        return

    organize(folder, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
