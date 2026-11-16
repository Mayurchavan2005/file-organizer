"""
Auto File Organizer - GUI Version
by Mayur

Press a button, pick a folder, and the organizer does the work.
This is the GUI version of the CLI tool (file_organizer.py).

Run:  python file_organizer_gui.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

from file_organizer import organize, undo, get_category


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto File Organizer")
        self.root.geometry("520x460")
        self.root.resizable(False, False)

        self.folder = Path.home() / "Downloads"

        tk.Label(root, text="Auto File Organizer", font=("Arial", 18, "bold")).pack(pady=15)
        tk.Label(root, text="Clean up Downloads or any folder in one click",
                 font=("Arial", 10)).pack()

        self.path_label = tk.Label(root, text=f"Folder: {self.folder}",
                                   font=("Arial", 9), wraplength=480, fg="grey")
        self.path_label.pack(pady=10)

        tk.Button(root, text="Choose Folder", command=self.choose_folder,
                  font=("Arial", 11), width=20, bg="#4CAF50", fg="white").pack(pady=5)

        tk.Button(root, text="Organize", command=self.start_organize,
                  font=("Arial", 12, "bold"), width=20, bg="#2196F3", fg="white").pack(pady=10)

        tk.Button(root, text="Undo Last Run", command=self.start_undo,
                  font=("Arial", 11), width=20, bg="#FF9800", fg="white").pack(pady=5)

        self.output = scrolledtext.ScrolledText(root, height=12, width=60, font=("Consolas", 9))
        self.output.pack(padx=15, pady=5)
        self.output.insert(tk.END, "Ready! Choose a folder and press Organize.\n")

    def choose_folder(self):
        chosen = filedialog.askdirectory(initialdir=str(self.folder))
        if chosen:
            self.folder = Path(chosen)
            self.path_label.config(text=f"Folder: {self.folder}")

    def start_organize(self):
        self.output.insert(tk.END, f"\nOrganizing: {self.folder}...\n")
        # Run in a separate thread so the UI does not freeze
        threading.Thread(target=self._run, daemon=True).start()

    def start_undo(self):
        self.output.insert(tk.END, f"\nUndoing last run in: {self.folder}...\n")
        # Run in a separate thread so the UI does not freeze
        threading.Thread(target=self._run_undo, daemon=True).start()

    def _run_undo(self):
        try:
            moved_back, skipped = undo(self.folder, dry_run=False)
            if moved_back == 0:
                self.output.insert(tk.END, "\nNothing to undo.\n")
                messagebox.showinfo("Nothing to undo", "The last run was already undone, or there is no run to undo.")
            else:
                self.output.insert(tk.END, f"\nDone! {moved_back} files moved back.\n")
                messagebox.showinfo("Done!", f"Last run undone! {moved_back} files moved back.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _run(self):
        try:
            organize(self.folder, dry_run=False)
            self.output.insert(tk.END, "\nDone! Folder is clean.\n")
            messagebox.showinfo("Done!", "Folder organized!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
