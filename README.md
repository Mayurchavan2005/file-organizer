# Auto File Organizer

A small Python tool that sorts the files in a folder into sub-folders by file type. I built it because my Downloads folder was always full of mixed files and finding anything took too long.

## The problem

My Downloads folder had everything mixed together: photos, videos, PDFs, zip files, installers and code files. Searching for one file meant scrolling through a long list. Sorting by hand took time and I kept putting it off, so the folder only got worse.

This tool sorts the folder in one run, and shows what it will do before it moves anything.

## What it does

- Sorts files into Images, Videos, Documents, Music, Archives, Code, Apps and Others
- If a file with the same name already exists in the target folder, it saves the new one as `photo (1).jpg` instead of overwriting it
- Dry-run mode shows what would move, without moving anything
- Undo mode (`--undo`) moves files from the last run back to where they were, using `organizer_log.txt`. If a file with the same name is already back in the folder, it saves the restored file as `photo (1).jpg` instead of overwriting it. Running `--undo` twice does nothing the second time. The GUI has an Undo Last Run button for the same thing.
- Writes a log of every move to `organizer_log.txt`, so I can check what went where
- Two versions: command line and a small GUI

## Tech stack and why I chose it

- Python, standard library only (`pathlib`, `shutil`, `argparse`, `tkinter`)
- I chose the standard library so there is nothing to install. It runs on any Windows machine with Python.
- `pathlib` for file paths, because it handles Windows paths cleanly
- `tkinter` for the GUI version, because it comes with Python and keeps the project to one language

## How to run it

Python 3.8 or newer is needed. No packages to install.

Command line version:

```bash
# Organize the Downloads folder
python file_organizer.py

# Organize a different folder
python file_organizer.py "C:\Users\Mayur\Documents"

# See what would happen first, without moving anything
python file_organizer.py --dry-run

# Move files from the last run back to where they were
python file_organizer.py --undo

# See what undo would do first, without moving anything
python file_organizer.py --undo --dry-run
```

GUI version:

```bash
python file_organizer_gui.py
```

Pick a folder, press Organize, and it sorts the files. Press Undo Last Run to move files from the last run back to where they were.

## Example

Before:

```
Downloads/
  photo.jpg
  movie.mp4
  resume.pdf
  song.mp3
  project.zip
```

After:

```
Downloads/
  Images/photo.jpg
  Videos/movie.mp4
  Documents/resume.pdf
  Music/song.mp3
  Archives/project.zip
```

## What I did myself

- The duplicate-name logic: checking for a free name and adding (1), (2) and so on
- Dry-run mode, so the tool never moves a file before I have seen the plan
- The log file, so every move can be checked afterwards
- The decision to skip the script itself and the log file, so the tool does not move its own files

## Challenges and learnings

- Moving files cannot be undone with Ctrl+Z. That is why I added dry-run first and a log file. I tested on a copy of a folder before running it on my real Downloads. Now `--undo` moves files from the last run back, so a mistake can be reversed.
- Two files can have the same name. My first version would have overwritten the older file. I fixed it by checking for a free name and numbering the copy, the way Windows does it.
- The tool kept trying to move its own script and log file. I learned to keep an exclude list and to test with the script sitting inside the folder it organizes.
- The GUI froze while files were moving. I moved the work to a separate thread so the window stays responsive.

## AI use

I used AI for boilerplate and debugging. The problem, the design and the logic are mine. I ran the code myself, tested it on sample files, and fixed the bugs I found.

## Screenshots

To add: a screenshot of the Downloads folder before and after a run, and one of the GUI window. (Take these on your own machine after running it.)

## Next step

The project is on GitHub now. What is left is to test it on my own Windows machine and take the screenshots.
