"""SAMBU Duck Studio: a lightweight Tkinter desktop IDE."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sambu.ide import SambuIDE

DARK = "#050505"
PANEL = "#11171C"
PANEL_ALT = "#0D1115"
YELLOW = "#FCEE0A"
YELLOW_HOVER = "#FFF67A"
YELLOW_PRESSED = "#A69B00"
SURFACE_HOVER = "#202A31"
BORDER = "#2A353D"
TEXT = "#FFFFFF"
MUTED = "#A6B2BC"
GREEN = "#4CAF50"
RED = "#FF003C"

STRINGS = {
    "en": {
        "file": "File", "open": "Open", "save": "Save", "save_as": "Save as",
        "run": "Run ▶", "check": "Check syntax", "devices": "iPhone / iPad",
        "workspace": "Workspace", "outline": "Outline", "output": "Output",
        "diagnostics": "Diagnostics", "welcome": "Open a .sambu file or start typing.",
        "saved": "Saved", "opened": "Opened", "valid": "Syntax OK",
        "invalid": "Syntax errors found", "no_file": "Save the document before running it.",
        "run_error": "Could not run SAMBU", "device_title": "Apple device diagnostics",
        "scan": "Scan device", "device_hint": "Connect an iPhone/iPad by USB, unlock it and approve Trust on the device.",
        "language": "Language", "ready": "Ready", "line": "Line",
        "new": "New", "about": "SAMBU Duck Studio · experimental alpha",
    },
    "ru": {
        "file": "Файл", "open": "Открыть", "save": "Сохранить", "save_as": "Сохранить как",
        "run": "Запустить ▶", "check": "Проверить синтаксис", "devices": "iPhone / iPad",
        "workspace": "Проект", "outline": "Структура", "output": "Вывод",
        "diagnostics": "Диагностика", "welcome": "Откройте файл .sambu или начните вводить код.",
        "saved": "Сохранено", "opened": "Открыто", "valid": "Синтаксис корректен",
        "invalid": "Обнаружены ошибки синтаксиса", "no_file": "Сначала сохраните документ.",
        "run_error": "Не удалось запустить SAMBU", "device_title": "Диагностика устройств Apple",
        "scan": "Проверить устройство", "device_hint": "Подключите iPhone/iPad по USB, разблокируйте и подтвердите «Доверять этому компьютеру».",
        "language": "Язык", "ready": "Готово", "line": "Строка",
        "new": "Новый", "about": "SAMBU Duck Studio · экспериментальная alpha",
    },
}


class DuckStudio:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang = "ru"
        self.t = STRINGS[self.lang]
        self.path: Path | None = None
        self.ide = SambuIDE()
        self.version = 0
        self._init_ui_scale()
        self._build()
        self._set_text()
        self._set_status(self.t["ready"])

    def _init_ui_scale(self) -> None:
        """Load a persistent vector/font scaling factor for the IDE."""
        self.scale_file = Path.home() / ".sambu" / "ide.json"
        self.ui_scale = 1.0
        try:
            config = json.loads(self.scale_file.read_text(encoding="utf-8"))
            self.ui_scale = float(config.get("ui_scale", 1.0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
        self.ui_scale = max(0.80, min(1.60, self.ui_scale))
        try:
            self.base_tk_scaling = float(self.root.tk.call("tk", "scaling"))
            self.root.tk.call("tk", "scaling", self.base_tk_scaling * self.ui_scale)
        except tk.TclError:
            self.base_tk_scaling = 1.0
        for sequence, delta in (
            ("<Control-plus>", 0.10), ("<Control-equal>", 0.10),
            ("<Control-minus>", -0.10),
        ):
            self.root.bind_all(sequence, lambda _event, value=delta: self.adjust_ui_scale(value))
        self.root.bind_all("<Control-0>", lambda _event: self.adjust_ui_scale(0, reset=True))

    def adjust_ui_scale(self, delta: float = 0.0, *, reset: bool = False) -> None:
        self.ui_scale = 1.0 if reset else max(0.80, min(1.60, round(self.ui_scale + delta, 2)))
        try:
            self.root.tk.call("tk", "scaling", self.base_tk_scaling * self.ui_scale)
            self.scale_file.parent.mkdir(parents=True, exist_ok=True)
            self.scale_file.write_text(json.dumps({"ui_scale": self.ui_scale}, indent=2), encoding="utf-8")
        except (OSError, tk.TclError):
            pass
        if hasattr(self, "zoom_value"):
            self.zoom_value.configure(text=f"{round(self.ui_scale * 100)}%")
        self._set_status(f"UI scale {round(self.ui_scale * 100)}%")

    def _build(self):
        self.root.title("SAMBU Duck Studio")
        self.root.geometry("1440x900")
        self.root.minsize(960, 600)
        self.root.configure(bg=DARK)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=PANEL, foreground=TEXT, fieldbackground=PANEL_ALT)
        style.configure("TFrame", background=DARK)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure(
            "TButton", background=PANEL_ALT, foreground=TEXT,
            padding=(12, 9), borderwidth=0, focuscolor=YELLOW,
        )
        style.map(
            "TButton",
            background=[("pressed", YELLOW_PRESSED), ("active", SURFACE_HOVER)],
            foreground=[("pressed", DARK), ("active", TEXT)],
        )
        style.configure(
            "Accent.TButton", background=YELLOW, foreground=DARK,
            font=("Segoe UI", 10, "bold"), padding=(15, 9), borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("pressed", YELLOW_PRESSED), ("active", YELLOW_HOVER)],
            foreground=[("pressed", DARK), ("active", DARK)],
        )
        style.configure("TCombobox", fieldbackground=PANEL_ALT, foreground=TEXT, arrowcolor=YELLOW)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_ALT)], foreground=[("readonly", TEXT)])

        header = tk.Frame(self.root, bg=DARK, height=58)
        header.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(header, text="🦆 SAMBU", bg=DARK, fg=YELLOW, font=("Segoe UI", 19, "bold")).pack(side="left")
        tk.Label(header, text="DUCK STUDIO", bg=DARK, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10, 24))
        self.open_btn = ttk.Button(header, command=self.open_file)
        self.open_btn.pack(side="left", padx=3)
        self.save_btn = ttk.Button(header, command=self.save_file)
        self.save_btn.pack(side="left", padx=3)
        self.run_btn = ttk.Button(header, style="Accent.TButton", command=self.run_file)
        self.run_btn.pack(side="left", padx=(12, 3))
        self.check_btn = ttk.Button(header, command=self.check_source)
        self.check_btn.pack(side="left", padx=3)
        self.lang_box = ttk.Combobox(header, values=("RU", "EN"), width=5, state="readonly")
        self.lang_box.set("RU")
        self.lang_box.bind("<<ComboboxSelected>>", self.change_language)
        self.lang_box.pack(side="right", padx=4)
        self.zoom_value = tk.Label(header, text=f"{round(self.ui_scale * 100)}%",
                                   bg=DARK, fg=MUTED, font=("Segoe UI", 9), width=5)
        self.zoom_value.pack(side="right", padx=(4, 2))
        ttk.Button(header, text="+", width=3, command=lambda: self.adjust_ui_scale(0.10)).pack(side="right", padx=2)
        ttk.Button(header, text="−", width=3, command=lambda: self.adjust_ui_scale(-0.10)).pack(side="right", padx=2)

        body = tk.PanedWindow(self.root, orient="horizontal", bg=DARK, sashwidth=5, bd=0, sashrelief="flat")
        body.pack(fill="both", expand=True, padx=14, pady=4)
        left = tk.Frame(body, bg=PANEL, width=220)
        center = tk.Frame(body, bg=DARK)
        right = tk.Frame(body, bg=PANEL, width=270)
        body.add(left, minsize=170, width=220)
        body.add(center, minsize=450)
        body.add(right, minsize=210, width=270)

        self.project_title = self._section(left, "WORKSPACE")
        self.files = tk.Listbox(left, bg=PANEL, fg=TEXT, selectbackground=YELLOW, selectforeground=DARK,
                                relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=YELLOW, font=("Consolas", 10))
        self.files.pack(fill="both", expand=True, padx=10, pady=8)
        self.files.bind("<Double-Button-1>", self.open_selected)

        editor_head = tk.Frame(center, bg=PANEL, height=34)
        editor_head.pack(fill="x")
        self.file_label = tk.Label(editor_head, text="untitled.sambu", bg=PANEL, fg=YELLOW, padx=12, pady=8)
        self.file_label.pack(side="left")
        self.editor = tk.Text(center, bg="#0D1115", fg=TEXT, insertbackground=YELLOW,
                              selectbackground="#252400", relief="flat", undo=True, wrap="none", highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=YELLOW,
                              font=("Cascadia Code", 11), padx=14, pady=12, tabs=("4c",))
        self.editor.pack(fill="both", expand=True)
        self.editor.insert("1.0", '# Welcome to SAMBU Duck Studio\n\nlet greeting = "Hello, duck!"\nprint(greeting)\n')
        self.editor.bind("<KeyRelease>", self._on_edit)
        self.editor.bind("<Control-s>", lambda _e: self.save_file())
        self.editor.bind("<Control-o>", lambda _e: self.open_file())
        self.editor.bind("<F5>", lambda _e: self.run_file())

        bottom = tk.Frame(center, bg=PANEL, height=190)
        bottom.pack(fill="both", expand=False)
        self.output_title = self._section(bottom, "OUTPUT")
        self.output = tk.Text(bottom, height=8, bg=DARK, fg=GREEN, relief="flat",
                              font=("Consolas", 10), padx=10, pady=8, highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=YELLOW, state="disabled")
        self.output.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.outline_title = self._section(right, "OUTLINE")
        self.outline = tk.Listbox(right, bg=PANEL, fg=TEXT, relief="flat", highlightthickness=0,
                                  font=("Consolas", 10), height=12, highlightthickness=1,
                                  highlightbackground=BORDER, highlightcolor=YELLOW)
        self.outline.pack(fill="both", expand=True, padx=10, pady=8)
        self.diag_title = self._section(right, "DIAGNOSTICS")
        self.diagnostics = tk.Listbox(right, bg=PANEL, fg=RED, relief="flat", highlightthickness=0,
                                      font=("Segoe UI", 9), height=10, highlightthickness=1,
                                      highlightbackground=BORDER, highlightcolor=YELLOW)
        self.diagnostics.pack(fill="both", expand=True, padx=10, pady=8)
        self.devices_btn = ttk.Button(right, command=self.show_devices)
        self.devices_btn.pack(fill="x", padx=10, pady=(2, 10))

        self.status = tk.Label(self.root, bg=PANEL, fg=YELLOW, anchor="w", padx=12, pady=5,
                               font=("Segoe UI", 9, "bold"))
        self.status.pack(fill="x", side="bottom")

    def _section(self, parent, text):
        label = tk.Label(parent, text=text, bg=PANEL, fg=YELLOW, anchor="w",
                         font=("Segoe UI", 9, "bold"), padx=10, pady=9)
        label.pack(fill="x")
        return label

    def _set_text(self):
        self.open_btn.configure(text=self.t["open"])
        self.save_btn.configure(text=self.t["save"])
        self.run_btn.configure(text=self.t["run"])
        self.check_btn.configure(text=self.t["check"])
        self.project_title.configure(text=self.t["workspace"].upper())
        self.output_title.configure(text=self.t["output"].upper())
        self.outline_title.configure(text=self.t["outline"].upper())
        self.diag_title.configure(text=self.t["diagnostics"].upper())
        self.devices_btn.configure(text=self.t["devices"])
        self.lang_box.set(self.lang.upper())

    def change_language(self, _event=None):
        self.lang = "ru" if self.lang_box.get() == "RU" else "en"
        self.t = STRINGS[self.lang]
        self._set_text()

    def _set_status(self, message):
        self.status.configure(text=f"  {message}")

    def _write_output(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text.rstrip() + "\n")
        self.output.configure(state="disabled")

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("SAMBU source", "*.sambu"), ("All files", "*.*")])
        if filename:
            self._load(Path(filename))

    def _load(self, path: Path):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("SAMBU", str(exc))
            return
        self.path = path
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", source)
        self.file_label.configure(text=path.name)
        self._refresh_workspace()
        self.check_source()
        self._set_status(f"{self.t['opened']}: {path}")

    def open_selected(self, _event=None):
        selection = self.files.curselection()
        if not selection:
            return
        item = self.files.get(selection[0])
        if item.endswith(".sambu"):
            candidate = (self.path.parent if self.path else Path.cwd()) / item
            if candidate.is_file():
                self._load(candidate)

    def save_file(self):
        if self.path is None:
            name = filedialog.asksaveasfilename(defaultextension=".sambu",
                                                filetypes=[("SAMBU source", "*.sambu")])
            if not name:
                return
            self.path = Path(name)
        try:
            self.path.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8", newline="\n")
        except OSError as exc:
            messagebox.showerror("SAMBU", str(exc))
            return
        self.file_label.configure(text=self.path.name)
        self._refresh_workspace()
        self._set_status(f"{self.t['saved']}: {self.path}")

    def _on_edit(self, _event=None):
        self._set_status("Modified · Ctrl+S to save")

    def _refresh_workspace(self):
        self.files.delete(0, "end")
        if self.path and self.path.parent.is_dir():
            for child in sorted(self.path.parent.iterdir()):
                if child.is_file() and (child.suffix == ".sambu" or child.name in {"README.md", "pyproject.toml"}):
                    self.files.insert("end", child.name)

    def check_source(self):
        source = self.editor.get("1.0", "end-1c")
        self.version += 1
        uri = str(self.path.resolve()) if self.path else "untitled:duck-studio"
        try:
            if self.ide.document_version(uri) is None:
                report = self.ide.open_document(uri, source, version=self.version)
            else:
                report = self.ide.change_document(uri, source, version=self.version)
        except Exception as exc:
            self._write_output(str(exc))
            return
        self.outline.delete(0, "end")
        self.diagnostics.delete(0, "end")
        for symbol in report.symbols:
            self.outline.insert("end", f"{symbol.kind:10} {symbol.name}  :{symbol.start_line}")
            for child in symbol.children:
                self.outline.insert("end", f"  ↳ {child.name}  :{child.start_line}")
        for diagnostic in report.diagnostics:
            self.diagnostics.insert("end", f"{diagnostic.code} L{diagnostic.line}: {diagnostic.message}")
        if report.syntax_valid:
            self.diagnostics.insert("end", self.t["valid"])
            self._set_status(f"{self.t['valid']} · {report.token_count} tokens · SHA256 {report.sha256[:12]}")
        else:
            self._set_status(self.t["invalid"])

    def run_file(self):
        if self.path is None:
            messagebox.showinfo("SAMBU", self.t["no_file"])
            self.save_file()
            if self.path is None:
                return
        self.save_file()
        self.check_source()
        command = [sys.executable, "-m", "sambu", str(self.path)]
        try:
            result = subprocess.run(command, cwd=str(self.path.parent), capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=30, check=False)
            combined = result.stdout
            if result.stderr:
                combined += ("\n" if combined else "") + result.stderr
            self._write_output(combined or f"Process exited with code {result.returncode}")
            self._set_status(f"Exit code: {result.returncode}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._write_output(f"{self.t['run_error']}: {exc}")
            self._set_status(self.t["run_error"])

    def show_devices(self):
        from .device_diagnostics import scan_apple_devices
        report = scan_apple_devices()
        win = tk.Toplevel(self.root)
        win.title(self.t["device_title"])
        win.geometry("760x520")
        win.configure(bg=DARK)
        tk.Label(win, text="🦆  APPLE DEVICE LINK", bg=DARK, fg=YELLOW,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 8))
        tk.Label(win, text=self.t["device_hint"], bg=DARK, fg=MUTED,
                 wraplength=700, justify="left").pack(anchor="w", padx=18, pady=6)
        box = tk.Text(win, bg=PANEL, fg=TEXT, relief="flat", font=("Consolas", 10),
                      padx=14, pady=12, wrap="word")
        box.pack(fill="both", expand=True, padx=18, pady=12)
        box.insert("1.0", json.dumps(report, ensure_ascii=False, indent=2))
        box.configure(state="disabled")
        ttk.Button(win, text=self.t["scan"], command=lambda: [win.destroy(), self.show_devices()]).pack(
            anchor="e", padx=18, pady=(0, 16))


def main():
    root = tk.Tk()
    DuckStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
