"""SAMBU Studio: a keyboard-first desktop IDE for the SAMBU language.

The UI uses only Python's standard-library Tkinter. Language intelligence,
workspace checks and completions are delegated to the SAMBU IDE services.
Execution is launched with fixed argument vectors; no shell command is parsed.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from sambu.ide import IDEInspection, SambuIDE

DARK = "#101418"
PANEL = "#171e24"
PANEL_ALT = "#202a33"
EDITOR_BG = "#111820"
TEXT = "#e8edf2"
MUTED = "#8fa0ad"
ACCENT = "#e2b84b"
GREEN = "#83d6a2"
RED = "#ff7777"
BLUE = "#83b8e8"
BORDER = "#2a3742"
MAX_EDITOR_BYTES = 2_000_000
MAX_EXPLORER_NODES = 1800
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "build", "dist",
    ".idea", ".tox", ".next",
}
TEXT_SUFFIXES = {
    ".sambu", ".py", ".pyi", ".toml", ".ini", ".cfg", ".conf", ".md",
    ".rst", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".xml", ".csv",
    ".tsv", ".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx",
    ".rs", ".c", ".h", ".cpp", ".hpp", ".sh", ".bat", ".ps1", ".sql",
    ".graphql", ".gql", ".make", ".cmake", ".gitignore",
}
HIGHLIGHT_RE = re.compile(
    r"(?P<comment>\#.*$)"
    r"|(?P<string>\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*')"
    r"|(?P<number>\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b)"
    r"|(?P<keyword>\b(?:abstract|and|class|else|extends|false|final|fn|for|if|in|interface|is|let|null|or|private|protected|public|return|static|trait|true)\b)"
    r"|(?P<builtin>\b(?:print|range|len|sum|min|max|abs|round|sqrt|sin|cos|tan|log|exp|pi|e|K|kg|m|s|A|mol|cd|Hz|Pa|J|W|N|V|C|F)\b)",
    re.MULTILINE,
)

STRINGS = {
    "ru": {
        "new": "Новый", "open": "Файл", "folder": "Проект", "save": "Сохранить",
        "run": "▶ Запуск", "syntax": "Проверить", "workspace": "Проверка проекта",
        "tests": "Тесты", "build": "Сборка", "git": "Git",
        "ready": "Готово", "saved": "Сохранено", "modified": "Изменено · Ctrl+S",
        "opened": "Открыто", "no_document": "Сначала откройте или создайте документ.",
        "save_before_run": "Сохраните документ перед запуском.",
        "workspace_title": "ПРОЕКТ", "outline": "СТРУКТУРА", "problems": "ПРОБЛЕМЫ",
        "output": "ВЫВОД", "welcome": "Откройте проект или файл .sambu.",
        "run_error": "Ошибка запуска", "apple": "Устройства Apple",
        "language": "Язык", "line": "Строка", "column": "Столбец",
    },
    "en": {
        "new": "New", "open": "Open", "folder": "Project", "save": "Save",
        "run": "▶ Run", "syntax": "Check", "workspace": "Workspace check",
        "tests": "Tests", "build": "Build", "git": "Git",
        "ready": "Ready", "saved": "Saved", "modified": "Modified · Ctrl+S",
        "opened": "Opened", "no_document": "Open or create a document first.",
        "save_before_run": "Save the document before running it.",
        "workspace_title": "PROJECT", "outline": "OUTLINE", "problems": "PROBLEMS",
        "output": "OUTPUT", "welcome": "Open a project or a .sambu file.",
        "run_error": "Launch error", "apple": "Apple devices",
        "language": "Language", "line": "Line", "column": "Column",
    },
}


@dataclass
class EditorDocument:
    frame: ttk.Frame
    editor: tk.Text
    gutter: tk.Text
    path: Path | None
    uri: str
    version: int = 0
    dirty: bool = False
    loading: bool = False
    inspection: IDEInspection | None = None
    analysis_job: str | None = None


class SambuStudio:
    """Multi-document SAMBU editor and project production workbench."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang = "ru"
        self.t = STRINGS[self.lang]
        self.ide = SambuIDE()
        self.workspace: Path | None = None
        self.documents: dict[str, EditorDocument] = {}
        self.tree_paths: dict[str, Path] = {}
        self.outline_lines: list[int] = []
        self.problem_lines: list[int] = []
        self._node_count = 0
        self._job: dict[str, object] | None = None
        self._job_results: queue.Queue[tuple[str, int, str]] = queue.Queue()
        self._completion_window: tk.Toplevel | None = None
        self._completion_list: tk.Listbox | None = None
        self._completion_prefix = ""
        self._completion_doc: EditorDocument | None = None
        self._build()
        self._new_document()
        self._set_status(self.t["ready"])

    def _build(self) -> None:
        self.root.title("SAMBU Studio")
        self.root.geometry("1540x980")
        self.root.minsize(1050, 680)
        self.root.configure(bg=DARK)
        self._configure_style()
        self._build_menu()

        header = tk.Frame(self.root, bg=DARK, height=58)
        header.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(
            header, text="SAMBU", bg=DARK, fg=ACCENT,
            font=("Segoe UI", 19, "bold"),
        ).pack(side="left", padx=(4, 14))
        tk.Label(
            header, text="STUDIO  /  LANGUAGE WORKBENCH",
            bg=DARK, fg=MUTED, font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(0, 20))

        self._button(header, "new", self._new_document)
        self._button(header, "open", self.open_file)
        self._button(header, "folder", self.open_folder)
        self._button(header, "save", self.save_file)
        self._button(header, "run", self.run_current, accent=True)
        self._button(header, "syntax", self.check_current)
        self._button(header, "workspace", self.check_workspace)
        self._button(header, "tests", self.run_tests)
        self._button(header, "build", self.build_package)
        self._button(header, "git", self.git_status)

        self.language_box = ttk.Combobox(
            header, values=("RU", "EN"), width=5, state="readonly",
        )
        self.language_box.set("RU")
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)
        self.language_box.pack(side="right", padx=(8, 2))

        main = tk.PanedWindow(
            self.root, orient="horizontal", bg=DARK, sashwidth=5,
            bd=0, sashrelief="flat", opaqueresize=True,
        )
        main.pack(fill="both", expand=True, padx=12, pady=4)

        left = tk.Frame(main, bg=PANEL, width=245)
        center = tk.Frame(main, bg=DARK)
        right = tk.Frame(main, bg=PANEL, width=275)
        main.add(left, minsize=175, width=245)
        main.add(center, minsize=500)
        main.add(right, minsize=220, width=275)

        self.project_label = self._section(left, self.t["workspace_title"])
        tree_tools = tk.Frame(left, bg=PANEL)
        tree_tools.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Button(tree_tools, text="↻", width=3, command=self.refresh_explorer).pack(side="left")
        ttk.Button(tree_tools, text="+ File", command=self.create_file).pack(side="left", padx=4)
        ttk.Button(tree_tools, text="Open", command=self.open_file).pack(side="left")
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        self.tree.bind("<Double-Button-1>", self._open_tree_selection)
        self.tree.bind("<Return>", self._open_tree_selection)
        self.tree.bind("<Button-3>", self._tree_context_menu)

        vertical = tk.PanedWindow(
            center, orient="vertical", bg=DARK, sashwidth=5, bd=0,
            sashrelief="flat", opaqueresize=True,
        )
        vertical.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(vertical)
        vertical.add(self.notebook, minsize=260, height=590)
        self.notebook.bind("<<NotebookTabChanged>>", self._tab_changed)

        self.output_tabs = ttk.Notebook(vertical)
        vertical.add(self.output_tabs, minsize=115, height=205)
        output_frame = tk.Frame(self.output_tabs, bg=EDITOR_BG)
        self.output_tabs.add(output_frame, text=self.t["output"])
        self.output = tk.Text(
            output_frame, bg=EDITOR_BG, fg=GREEN, insertbackground=ACCENT,
            relief="flat", wrap="word", font=("Cascadia Mono", 10),
            padx=12, pady=10, state="disabled",
        )
        output_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview)
        self.output.configure(yscrollcommand=output_scroll.set)
        self.output.pack(side="left", fill="both", expand=True)
        output_scroll.pack(side="right", fill="y")

        self.build_output_frame = tk.Frame(self.output_tabs, bg=EDITOR_BG)
        self.output_tabs.add(self.build_output_frame, text="TASK LOG")
        self.task_output = tk.Text(
            self.build_output_frame, bg=EDITOR_BG, fg=TEXT, insertbackground=ACCENT,
            relief="flat", wrap="word", font=("Cascadia Mono", 9),
            padx=12, pady=10, state="disabled",
        )
        self.task_output.pack(fill="both", expand=True)

        self.outline_label = self._section(right, self.t["outline"])
        self.outline = tk.Listbox(
            right, bg=PANEL, fg=TEXT, selectbackground=ACCENT,
            selectforeground=DARK, relief="flat", highlightthickness=0,
            font=("Cascadia Mono", 9), height=14,
        )
        self.outline.pack(fill="both", expand=True, padx=8, pady=(2, 10))
        self.outline.bind("<Double-Button-1>", self._jump_outline)
        self.problem_label = self._section(right, self.t["problems"])
        self.problems = tk.Listbox(
            right, bg=PANEL, fg="#ff9b91", selectbackground=ACCENT,
            selectforeground=DARK, relief="flat", highlightthickness=0,
            font=("Segoe UI", 9), height=12,
        )
        self.problems.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        self.problems.bind("<Double-Button-1>", self._jump_problem)
        ttk.Button(right, text="Apple device diagnostics…", command=self.show_devices).pack(
            fill="x", padx=8, pady=(0, 10),
        )

        self.status = tk.Label(
            self.root, bg=ACCENT, fg=DARK, anchor="w", padx=12, pady=5,
            font=("Segoe UI", 9, "bold"),
        )
        self.status.pack(fill="x", side="bottom")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind_all("<Control-s>", lambda _e: self.save_file())
        self.root.bind_all("<Control-o>", lambda _e: self.open_file())
        self.root.bind_all("<Control-Shift-O>", lambda _e: self.open_folder())
        self.root.bind_all("<Control-n>", lambda _e: self._new_document())
        self.root.bind_all("<Control-f>", lambda _e: self.show_find())
        self.root.bind_all("<Control-h>", lambda _e: self.show_find(replace=True))
        self.root.bind_all("<Control-g>", lambda _e: self.go_to_line())
        self.root.bind_all("<F5>", lambda _e: self.run_current())
        self.root.bind_all("<F6>", lambda _e: self.check_workspace())
        self.root.bind_all("<F7>", lambda _e: self.run_tests())
        self.root.bind_all("<Shift-F5>", lambda _e: self.stop_job())

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=PANEL, foreground=TEXT, fieldbackground=PANEL_ALT)
        style.configure("TFrame", background=DARK)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure(
            "TButton", background=PANEL_ALT, foreground=TEXT,
            padding=(9, 6), borderwidth=0,
        )
        style.map(
            "TButton",
            background=[("active", ACCENT), ("pressed", ACCENT)],
            foreground=[("active", DARK), ("pressed", DARK)],
        )
        style.configure(
            "Accent.TButton", background=ACCENT, foreground=DARK,
            font=("Segoe UI", 9, "bold"), padding=(10, 6),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#f0cf70"), ("pressed", "#c89b32")],
            foreground=[("active", DARK), ("pressed", DARK)],
        )
        style.configure(
            "Treeview", background=PANEL, fieldbackground=PANEL,
            foreground=TEXT, rowheight=25, borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#334453")])
        style.configure(
            "Treeview.Heading", background=PANEL_ALT, foreground=ACCENT,
            relief="flat",
        )
        style.configure("TNotebook", background=DARK, borderwidth=0)
        style.configure(
            "TNotebook.Tab", background=PANEL, foreground=MUTED,
            padding=(12, 7),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", PANEL_ALT)],
            foreground=[("selected", ACCENT)],
        )
        style.configure("TCombobox", fieldbackground=PANEL_ALT, foreground=TEXT)

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root, tearoff=False, bg=PANEL, fg=TEXT)
        file_menu = tk.Menu(menu, tearoff=False, bg=PANEL, fg=TEXT)
        file_menu.add_command(label="New buffer  Ctrl+N", command=self._new_document)
        file_menu.add_command(label="Open file  Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Open project  Ctrl+Shift+O", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save  Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save as…", command=self.save_as)
        file_menu.add_command(label="Close tab", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=False, bg=PANEL, fg=TEXT)
        edit_menu.add_command(label="Find  Ctrl+F", command=self.show_find)
        edit_menu.add_command(label="Replace  Ctrl+H", command=lambda: self.show_find(replace=True))
        edit_menu.add_command(label="Go to line  Ctrl+G", command=self.go_to_line)
        edit_menu.add_command(label="Toggle line comment  Ctrl+/", command=self.toggle_comment)
        edit_menu.add_command(label="Complete  Ctrl+Space", command=self.show_completion)
        menu.add_cascade(label="Edit", menu=edit_menu)

        run_menu = tk.Menu(menu, tearoff=False, bg=PANEL, fg=TEXT)
        run_menu.add_command(label="Run current file  F5", command=self.run_current)
        run_menu.add_command(label="Check current file", command=self.check_current)
        run_menu.add_command(label="Check workspace  F6", command=self.check_workspace)
        run_menu.add_command(label="Run tests  F7", command=self.run_tests)
        run_menu.add_command(label="Build package", command=self.build_package)
        run_menu.add_command(label="Stop task  Shift+F5", command=self.stop_job)
        menu.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menu, tearoff=False, bg=PANEL, fg=TEXT)
        help_menu.add_command(label="Keyboard shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About SAMBU Studio", command=self.show_about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.configure(menu=menu)

    def _button(self, parent: tk.Widget, key: str, command, *, accent: bool = False) -> None:
        button = ttk.Button(
            parent, text=self.t[key], command=command,
            style="Accent.TButton" if accent else "TButton",
        )
        button.pack(side="left", padx=2)

    def _section(self, parent: tk.Widget, text: str) -> tk.Label:
        label = tk.Label(
            parent, text=text, bg=PANEL, fg=ACCENT, anchor="w",
            font=("Segoe UI", 9, "bold"), padx=10, pady=9,
        )
        label.pack(fill="x")
        return label

    def change_language(self, _event=None) -> None:
        self.lang = "ru" if self.language_box.get() == "RU" else "en"
        self.t = STRINGS[self.lang]
        self.project_label.configure(text=self.t["workspace_title"])
        self.outline_label.configure(text=self.t["outline"])
        self.problem_label.configure(text=self.t["problems"])
        self._set_status(self.t["ready"])

    def _set_status(self, message: str) -> None:
        tab = self._active_document()
        cursor = ""
        if tab is not None:
            line, column = tab.editor.index("insert").split(".")
            cursor = f"   Ln {line}, Col {int(column) + 1}"
            if tab.dirty:
                cursor += "   ●"
        self.status.configure(text=f"  {message}{cursor}    UTF-8    SAMBU")

    def _append_output(self, text: str, *, task: bool = False) -> None:
        widget = self.task_output if task else self.output
        widget.configure(state="normal")
        widget.insert("end", text.rstrip() + "\n")
        widget.see("end")
        widget.configure(state="disabled")
        self.output_tabs.select(self.build_output_frame if task else 0)

    def _active_document(self) -> EditorDocument | None:
        selected = self.notebook.select()
        return self.documents.get(selected) if selected else None

    def _new_document(self) -> None:
        self._create_document(None, "")

    def _create_document(self, path: Path | None, source: str) -> EditorDocument:
        frame = ttk.Frame(self.notebook)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        gutter = tk.Text(
            frame, width=5, bg="#18212a", fg="#667887", relief="flat",
            state="disabled", wrap="none", takefocus=0,
            font=("Cascadia Mono", 10), padx=8, pady=10,
        )
        editor = tk.Text(
            frame, bg=EDITOR_BG, fg=TEXT, insertbackground=ACCENT,
            selectbackground="#354b5e", relief="flat", undo=True, wrap="none",
            font=("Cascadia Mono", 10), padx=12, pady=10,
            tabs=("4c",), maxundo=-1, autoseparators=True,
        )
        vertical = ttk.Scrollbar(frame, orient="vertical")
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=editor.xview)

        def scroll_changed(first: str, last: str) -> None:
            vertical.set(first, last)
            gutter.yview_moveto(first)

        def scroll_both(*args) -> None:
            editor.yview(*args)
            gutter.yview(*args)

        editor.configure(yscrollcommand=scroll_changed, xscrollcommand=horizontal.set)
        vertical.configure(command=scroll_both)
        gutter.grid(row=0, column=0, sticky="ns")
        editor.grid(row=0, column=1, sticky="nsew")
        vertical.grid(row=0, column=2, sticky="ns")
        horizontal.grid(row=1, column=1, sticky="ew")
        editor.tag_configure("keyword", foreground="#d6a6ff")
        editor.tag_configure("builtin", foreground="#7cc7da")
        editor.tag_configure("string", foreground="#b9d88a")
        editor.tag_configure("number", foreground="#e7b875")
        editor.tag_configure("comment", foreground="#708391", font=("Cascadia Mono", 10, "italic"))
        editor.tag_configure("search", background="#715d2b", foreground="#fff2c3")
        editor.tag_configure("current_line", background="#17232d")
        editor.tag_lower("current_line")

        tab = EditorDocument(
            frame=frame, editor=editor, gutter=gutter, path=path,
            uri=str(path.resolve()) if path else f"untitled:sambu-{id(frame)}",
            loading=True,
        )
        self.documents[str(frame)] = tab
        editor.insert("1.0", source)
        editor.edit_modified(False)
        tab.loading = False
        editor.bind("<<Modified>>", lambda _e, current=tab: self._on_modified(current))
        editor.bind("<KeyRelease>", lambda _e, current=tab: self._on_key_release(current))
        editor.bind("<ButtonRelease-1>", lambda _e, current=tab: self._update_cursor(current))
        editor.bind("<MouseWheel>", lambda _e, current=tab: self._after_scroll(current))
        editor.bind("<Tab>", lambda _e, current=tab: self._indent(current))
        editor.bind("<ISO_Left_Tab>", lambda _e, current=tab: self._outdent(current))
        editor.bind("<Shift-Tab>", lambda _e, current=tab: self._outdent(current))
        editor.bind("<Return>", lambda _e, current=tab: self._newline(current))
        editor.bind("<Control-slash>", lambda _e: self.toggle_comment())
        editor.bind("<Control-space>", lambda _e: self.show_completion())
        editor.bind("<Escape>", lambda _e: self._hide_completion())
        editor.bind("<Configure>", lambda _e, current=tab: self._update_gutter(current))
        self.notebook.add(frame, text=self._tab_title(tab))
        self.notebook.select(frame)
        self._update_gutter(tab)
        self._highlight(tab)
        editor.focus_set()
        self._set_status(self.t["ready"])
        return tab

    def _tab_title(self, tab: EditorDocument) -> str:
        name = tab.path.name if tab.path else "untitled.sambu"
        return f"{name}{'  ●' if tab.dirty else ''}"

    def _update_tab_title(self, tab: EditorDocument) -> None:
        try:
            self.notebook.tab(tab.frame, text=self._tab_title(tab))
        except tk.TclError:
            pass

    def _on_modified(self, tab: EditorDocument) -> None:
        if not tab.editor.edit_modified():
            return
        tab.editor.edit_modified(False)
        if tab.loading:
            return
        tab.dirty = True
        self._update_tab_title(tab)
        self._update_gutter(tab)
        self._set_status(self.t["modified"])
        self._schedule_analysis(tab)

    def _on_key_release(self, tab: EditorDocument) -> None:
        self._update_cursor(tab)
        self._update_current_line(tab)

    def _update_cursor(self, tab: EditorDocument) -> None:
        if tab is self._active_document():
            self._set_status(self.t["ready"])

    def _update_current_line(self, tab: EditorDocument) -> None:
        tab.editor.tag_remove("current_line", "1.0", "end")
        line = tab.editor.index("insert").split(".")[0]
        tab.editor.tag_add("current_line", f"{line}.0", f"{line}.end")
        tab.editor.tag_lower("current_line")

    def _after_scroll(self, tab: EditorDocument) -> None:
        self._update_gutter(tab)

    def _update_gutter(self, tab: EditorDocument) -> None:
        try:
            count = int(tab.editor.index("end-1c").split(".")[0])
            visible = "\n".join(str(n) for n in range(1, count + 1)) + "\n"
            tab.gutter.configure(state="normal")
            tab.gutter.delete("1.0", "end")
            tab.gutter.insert("1.0", visible)
            tab.gutter.configure(state="disabled")
            first, _last = tab.editor.yview()
            tab.gutter.yview_moveto(first)
        except tk.TclError:
            return

    def _highlight(self, tab: EditorDocument) -> None:
        editor = tab.editor
        try:
            source = editor.get("1.0", "end-1c")
            for tag in ("keyword", "builtin", "string", "number", "comment"):
                editor.tag_remove(tag, "1.0", "end")
            for match in HIGHLIGHT_RE.finditer(source):
                tag = match.lastgroup
                if not tag:
                    continue
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                editor.tag_add(tag, start, end)
        except tk.TclError:
            return

    def _schedule_analysis(self, tab: EditorDocument) -> None:
        if tab.analysis_job:
            try:
                self.root.after_cancel(tab.analysis_job)
            except tk.TclError:
                pass
        tab.analysis_job = self.root.after(350, lambda current=tab: self._analyse(current))

    def _analyse(self, tab: EditorDocument) -> IDEInspection | None:
        tab.analysis_job = None
        try:
            source = tab.editor.get("1.0", "end-1c")
            current = self.ide.document_version(tab.uri)
            next_version = max(tab.version + 1, (current or 0) + 1)
            if current is None:
                report = self.ide.open_document(tab.uri, source, version=next_version)
            else:
                report = self.ide.change_document(tab.uri, source, version=next_version)
            tab.version = next_version
            tab.inspection = report
            if tab is self._active_document():
                self._render_inspection(report)
            return report
        except (OSError, ValueError, RuntimeError, TypeError) as exc:
            self._append_output(f"IDE inspection failed: {exc}")
            return None

    def _render_inspection(self, report: IDEInspection) -> None:
        self.outline.delete(0, "end")
        self.outline_lines.clear()

        def add_symbols(symbols, depth: int = 0) -> None:
            for symbol in symbols:
                prefix = "  " * depth
                self.outline.insert("end", f"{prefix}{symbol.kind:10} {symbol.name}  :{symbol.start_line}")
                self.outline_lines.append(symbol.start_line)
                add_symbols(symbol.children, depth + 1)

        add_symbols(report.symbols)
        self.problems.delete(0, "end")
        self.problem_lines.clear()
        for diagnostic in report.diagnostics:
            self.problems.insert(
                "end",
                f"{diagnostic.severity.upper():5} L{diagnostic.line}:{diagnostic.column} "
                f"{diagnostic.code}  {diagnostic.message[:120]}",
            )
            self.problem_lines.append(diagnostic.line)
        if report.syntax_valid:
            self.problems.insert("end", "✓ Syntax valid")
            self.problem_lines.append(1)
            self._set_status(
                f"Syntax OK · {report.token_count} tokens · {report.line_count} lines · "
                f"SHA-256 {report.sha256[:10]}"
            )
        else:
            self._set_status(f"{len(report.diagnostics)} syntax diagnostic(s)")

    def _tab_changed(self, _event=None) -> None:
        tab = self._active_document()
        if tab is None:
            return
        if tab.inspection is None or tab.dirty:
            self._analyse(tab)
        elif tab.inspection is not None:
            self._render_inspection(tab.inspection)
        tab.editor.focus_set()
        self._update_cursor(tab)

    def _jump_to_line(self, line: int) -> None:
        tab = self._active_document()
        if tab is None:
            return
        tab.editor.mark_set("insert", f"{max(1, line)}.0")
        tab.editor.see("insert")
        tab.editor.focus_set()
        self._update_current_line(tab)

    def _jump_outline(self, _event=None) -> None:
        selection = self.outline.curselection()
        if selection and selection[0] < len(self.outline_lines):
            self._jump_to_line(self.outline_lines[selection[0]])

    def _jump_problem(self, _event=None) -> None:
        selection = self.problems.curselection()
        if selection and selection[0] < len(self.problem_lines):
            self._jump_to_line(self.problem_lines[selection[0]])

    def open_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open source file",
            filetypes=[
                ("SAMBU source", "*.sambu"), ("Text and source files", "*.py *.md *.toml *.json *.yaml *.yml *.xml"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self._load_file(Path(filename))

    def _load_file(self, path: Path) -> None:
        try:
            size = path.stat().st_size
            if size > MAX_EDITOR_BYTES:
                raise ValueError(f"File exceeds the editor limit of {MAX_EDITOR_BYTES:,} bytes.")
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror("SAMBU Studio", str(exc))
            return
        for tab in self.documents.values():
            if tab.path and tab.path.resolve() == path.resolve():
                self.notebook.select(tab.frame)
                return
        self.workspace = self.workspace or path.parent
        tab = self._create_document(path, source)
        tab.uri = str(path.resolve())
        self._analyse(tab)
        self.refresh_explorer()
        self._set_status(f"{self.t['opened']}: {path.name}")

    def open_folder(self) -> None:
        folder = filedialog.askdirectory(title="Open SAMBU project folder")
        if folder:
            self.workspace = Path(folder).resolve()
            self.refresh_explorer()
            self._set_status(f"Project: {self.workspace}")

    def refresh_explorer(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree_paths.clear()
        self._node_count = 0
        if self.workspace is None or not self.workspace.is_dir():
            self.tree.insert("", "end", text="Open a project folder…")
            return
        root_id = self._insert_tree_node("", self.workspace, depth=0)
        if root_id:
            self.tree.item(root_id, open=True)
        self._set_status(f"Project refreshed: {self.workspace.name}")

    def _insert_tree_node(self, parent: str, path: Path, depth: int) -> str | None:
        if self._node_count >= MAX_EXPLORER_NODES:
            return None
        self._node_count += 1
        label = f"📁 {path.name}" if path.is_dir() else path.name
        node = f"node-{self._node_count}"
        try:
            self.tree.insert(parent, "end", iid=node, text=label, open=(depth == 0))
        except tk.TclError:
            return None
        self.tree_paths[node] = path
        if not path.is_dir() or depth >= 5:
            return node
        try:
            children = sorted(
                os.scandir(path),
                key=lambda item: (not item.is_dir(follow_symlinks=False), item.name.casefold()),
            )
        except OSError:
            return node
        for entry in children:
            if entry.name in IGNORED_DIRS or entry.name.startswith(".git"):
                continue
            try:
                if entry.is_symlink():
                    continue
                child = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    self._insert_tree_node(node, child, depth + 1)
                elif child.suffix.lower() in TEXT_SUFFIXES or child.name in {".gitignore", "Makefile"}:
                    self._insert_tree_node(node, child, depth + 1)
            except OSError:
                continue
            if self._node_count >= MAX_EXPLORER_NODES:
                break
        return node

    def _open_tree_selection(self, _event=None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        path = self.tree_paths.get(selection[0])
        if path and path.is_file():
            self._load_file(path)
        elif path and path.is_dir():
            self.tree.item(selection[0], open=not self.tree.item(selection[0], "open"))

    def _tree_context_menu(self, event) -> None:
        node = self.tree.identify_row(event.y)
        if node:
            self.tree.selection_set(node)
        menu = tk.Menu(self.root, tearoff=False, bg=PANEL, fg=TEXT)
        menu.add_command(label="Open", command=self._open_tree_selection)
        menu.add_command(label="New SAMBU file…", command=self.create_file)
        menu.add_command(label="Refresh project", command=self.refresh_explorer)
        menu.tk_popup(event.x_root, event.y_root)

    def create_file(self) -> None:
        if self.workspace is None:
            self.open_folder()
        if self.workspace is None:
            return
        name = simpledialog.askstring("New SAMBU file", "File name:", initialvalue="module.sambu")
        if not name:
            return
        candidate_name = Path(name)
        if candidate_name.is_absolute() or ".." in candidate_name.parts or len(candidate_name.parts) != 1:
            messagebox.showerror("SAMBU Studio", "Use a single file name without directory traversal.")
            return
        if not candidate_name.suffix:
            candidate_name = candidate_name.with_suffix(".sambu")
        if candidate_name.suffix.lower() != ".sambu":
            messagebox.showerror("SAMBU Studio", "New language files must use the .sambu extension.")
            return
        target = self.workspace / candidate_name
        if target.exists():
            messagebox.showerror("SAMBU Studio", f"File already exists: {target.name}")
            return
        try:
            target.write_text("# New SAMBU module\n\n", encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("SAMBU Studio", str(exc))
            return
        self._load_file(target)

    def save_file(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        if tab.path is None:
            self.save_as()
            return
        self._write_document(tab, tab.path)

    def save_as(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".sambu",
            filetypes=[("SAMBU source", "*.sambu"), ("All files", "*.*")],
        )
        if not filename:
            return
        target = Path(filename)
        self._write_document(tab, target)

    def _write_document(self, tab: EditorDocument, path: Path) -> None:
        source = tab.editor.get("1.0", "end-1c")
        try:
            path.write_text(source, encoding="utf-8", newline="\n")
        except OSError as exc:
            messagebox.showerror("SAMBU Studio", str(exc))
            return
        old_uri = tab.uri
        if old_uri != str(path.resolve()):
            self.ide.close_document(old_uri)
            tab.uri = str(path.resolve())
            tab.path = path
            tab.version = 0
            tab.inspection = None
        tab.path = path
        tab.dirty = False
        tab.editor.edit_modified(False)
        self._update_tab_title(tab)
        self.refresh_explorer()
        self._analyse(tab)
        self._set_status(f"{self.t['saved']}: {path.name}")

    def _ask_save(self, tab: EditorDocument) -> bool:
        if not tab.dirty:
            return True
        name = tab.path.name if tab.path else "untitled.sambu"
        answer = messagebox.askyesnocancel("Unsaved changes", f"Save changes to {name}?")
        if answer is None:
            return False
        if answer:
            if tab.path is None:
                self.save_as()
            else:
                self._write_document(tab, tab.path)
            return not tab.dirty
        return True

    def close_current_tab(self) -> None:
        tab = self._active_document()
        if tab is None or not self._ask_save(tab):
            return
        self.ide.close_document(tab.uri)
        key = str(tab.frame)
        self.documents.pop(key, None)
        self.notebook.forget(tab.frame)
        if not self.documents:
            self._new_document()

    def _on_close(self) -> None:
        for tab in list(self.documents.values()):
            if not self._ask_save(tab):
                return
        self.stop_job()
        self.root.destroy()

    def check_current(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        report = self._analyse(tab)
        if report is None:
            return
        self._append_output(
            f"{tab.path or 'untitled'}: {'syntax OK' if report.syntax_valid else 'syntax errors'}\n"
            f"{report.line_count} lines · {report.token_count} tokens · SHA-256 {report.sha256}",
        )
        self._set_status("Syntax OK" if report.syntax_valid else "Syntax errors found")

    def check_workspace(self) -> None:
        root = self.workspace
        if root is None:
            tab = self._active_document()
            root = tab.path.parent if tab and tab.path else Path.cwd()
        try:
            report = self.ide.inspect_workspace(root)
            lines = [
                f"Workspace check: {root}",
                f"Parsed {report.valid_files}/{report.files_checked} SAMBU source files",
                f"Status: {'PASS' if report.valid else 'NEEDS ATTENTION'}",
            ]
            lines.extend(
                f"{issue.path}:{issue.line}:{issue.column} [{issue.code}] {issue.message}"
                for issue in report.issues
            )
            self._append_output("\n".join(lines), task=True)
            self._set_status("Workspace checks passed" if report.valid else "Workspace needs attention")
        except (OSError, ValueError, RuntimeError) as exc:
            self._append_output(f"Workspace check failed: {exc}", task=True)
            self._set_status("Workspace check failed")

    def _project_root(self, tab: EditorDocument | None = None) -> Path:
        if self.workspace is not None:
            return self.workspace
        if tab is not None and tab.path is not None:
            for candidate in (tab.path.parent, *tab.path.parents):
                if (candidate / "pyproject.toml").is_file() or (candidate / ".git").exists():
                    return candidate
            return tab.path.parent
        return Path.cwd()

    def run_current(self) -> None:
        tab = self._active_document()
        if tab is None:
            messagebox.showinfo("SAMBU Studio", self.t["no_document"])
            return
        if tab.path is None or tab.dirty:
            if tab.path is not None:
                if not self._ask_save(tab):
                    return
            else:
                self.save_as()
            if tab.path is None or tab.dirty:
                return
        command = [sys.executable, "-m", "sambu", str(tab.path)]
        self._start_job(command, f"Run {tab.path.name}", cwd=self._project_root(tab), timeout=120)

    def run_tests(self) -> None:
        root = self._project_root(self._active_document())
        tests = root / "tests"
        if not tests.is_dir():
            messagebox.showinfo("SAMBU Studio", f"No tests directory found in {root}")
            return
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        self._start_job(command, "Unit tests", cwd=root, timeout=240)

    def build_package(self) -> None:
        root = self._project_root(self._active_document())
        if not (root / "pyproject.toml").is_file():
            messagebox.showinfo("SAMBU Studio", "No pyproject.toml found in the project root.")
            return
        command = [sys.executable, "-m", "build"]
        self._start_job(command, "Package build (python -m build)", cwd=root, timeout=240)

    def git_status(self) -> None:
        root = self._project_root(self._active_document())
        if not (root / ".git").exists():
            messagebox.showinfo("SAMBU Studio", f"No Git repository found in {root}")
            return
        self._start_job(["git", "status", "--short", "--branch"], "Git status", cwd=root, timeout=30)

    def _start_job(self, command: list[str], label: str, *, cwd: Path, timeout: int) -> None:
        if self._job is not None:
            messagebox.showwarning("SAMBU Studio", "A task is already running. Stop it before starting another.")
            return
        self._job = {"label": label, "process": None, "cancelled": False}
        self._append_output(f"\n$ {' '.join(command)}\n[{label} started]", task=True)

        def worker() -> None:
            process = None
            try:
                process = subprocess.Popen(
                    command, cwd=str(cwd), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                    errors="replace", shell=False,
                )
                if self._job is not None:
                    self._job["process"] = process
                try:
                    output, _ = process.communicate(timeout=timeout)
                    code = process.returncode
                except subprocess.TimeoutExpired:
                    process.kill()
                    output, _ = process.communicate()
                    output = (output or "") + f"\nTask exceeded the {timeout}s time limit."
                    code = 124
            except OSError as exc:
                output = f"{type(exc).__name__}: {exc}"
                code = 127
            self._job_results.put((label, code, output or "(no output)"))

        threading.Thread(target=worker, name="sambu-studio-task", daemon=True).start()
        self.root.after(120, self._poll_job)

    def _poll_job(self) -> None:
        if self._job is None:
            return
        try:
            label, code, output = self._job_results.get_nowait()
        except queue.Empty:
            self.root.after(120, self._poll_job)
            return
        self._append_output(f"{output}\n[{label} finished · exit code {code}]", task=True)
        self._job = None
        self._set_status(f"{label}: {'PASS' if code == 0 else 'FAILED'} · exit {code}")

    def stop_job(self) -> None:
        if self._job is None:
            return
        process = self._job.get("process")
        if process is not None:
            try:
                process.terminate()
                self._set_status("Stop requested")
            except OSError as exc:
                self._append_output(f"Could not stop task: {exc}", task=True)

    def _indent(self, tab: EditorDocument):
        editor = tab.editor
        try:
            start = editor.index("sel.first linestart")
            end = editor.index("sel.last lineend")
        except tk.TclError:
            start = editor.index("insert linestart")
            end = editor.index("insert lineend")
        line = start
        while editor.compare(line, "<=", end):
            editor.insert(line, "    ")
            line = editor.index(f"{line}+1line")
        return "break"

    def _outdent(self, tab: EditorDocument):
        editor = tab.editor
        try:
            start = editor.index("sel.first linestart")
            end = editor.index("sel.last lineend")
        except tk.TclError:
            start = editor.index("insert linestart")
            end = editor.index("insert lineend")
        line = start
        while editor.compare(line, "<=", end):
            prefix = editor.get(line, f"{line}+4c")
            if prefix.startswith("    "):
                editor.delete(line, f"{line}+4c")
            elif prefix.startswith("\t"):
                editor.delete(line, f"{line}+1c")
            line = editor.index(f"{line}+1line")
        return "break"

    def _newline(self, tab: EditorDocument):
        editor = tab.editor
        line = editor.get("insert linestart", "insert")
        indent = re.match(r"[ \t]*", line).group(0)
        editor.insert("insert", "\n" + indent)
        return "break"

    def toggle_comment(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        editor = tab.editor
        try:
            first = int(editor.index("sel.first").split(".")[0])
            last = int(editor.index("sel.last").split(".")[0])
        except tk.TclError:
            first = last = int(editor.index("insert").split(".")[0])
        lines = [editor.get(f"{line}.0", f"{line}.end") for line in range(first, last + 1)]
        uncomment = all(not value.strip() or value.lstrip().startswith("#") for value in lines)
        for offset, value in enumerate(lines):
            line_no = first + offset
            if not value.strip():
                continue
            leading = len(value) - len(value.lstrip())
            position = f"{line_no}.{leading}"
            if uncomment:
                editor.delete(position, f"{position}+1c")
                if editor.get(position, f"{position}+1c") == " ":
                    editor.delete(position, f"{position}+1c")
            else:
                editor.insert(position, "# ")
        editor.edit_modified(True)

    def show_find(self, *, replace: bool = False) -> None:
        tab = self._active_document()
        if tab is None:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Find and replace" if replace else "Find")
        dialog.configure(bg=PANEL)
        dialog.transient(self.root)
        dialog.resizable(False, False)
        tk.Label(dialog, text="Find", bg=PANEL, fg=TEXT).grid(row=0, column=0, padx=10, pady=8)
        find_entry = ttk.Entry(dialog, width=34)
        find_entry.grid(row=0, column=1, padx=8, pady=8)
        replace_entry = None
        if replace:
            tk.Label(dialog, text="Replace", bg=PANEL, fg=TEXT).grid(row=1, column=0, padx=10, pady=8)
            replace_entry = ttk.Entry(dialog, width=34)
            replace_entry.grid(row=1, column=1, padx=8, pady=8)

        def find_next() -> None:
            needle = find_entry.get()
            if not needle:
                return
            editor = tab.editor
            editor.tag_remove("search", "1.0", "end")
            start = editor.index("insert")
            found = editor.search(needle, start, stopindex="end", nocase=True)
            if not found:
                found = editor.search(needle, "1.0", stopindex=start, nocase=True)
            if found:
                end = f"{found}+{len(needle)}c"
                editor.tag_add("search", found, end)
                editor.mark_set("insert", end)
                editor.see(found)
                editor.focus_set()

        def replace_one() -> None:
            needle = find_entry.get()
            if not needle or replace_entry is None:
                return
            editor = tab.editor
            try:
                selected = editor.get("sel.first", "sel.last")
            except tk.TclError:
                selected = ""
            if selected.casefold() == needle.casefold():
                start = editor.index("sel.first")
                end = editor.index("sel.last")
                editor.delete(start, end)
                editor.insert(start, replace_entry.get())
                editor.mark_set("insert", f"{start}+{len(replace_entry.get())}c")
            find_next()

        def replace_all() -> None:
            needle = find_entry.get()
            if not needle or replace_entry is None:
                return
            editor = tab.editor
            source = editor.get("1.0", "end-1c")
            changed = source.replace(needle, replace_entry.get())
            if changed != source:
                editor.delete("1.0", "end")
                editor.insert("1.0", changed)
                editor.edit_modified(True)
            dialog.destroy()

        buttons = tk.Frame(dialog, bg=PANEL)
        buttons.grid(row=2 if replace else 1, column=0, columnspan=2, sticky="e", padx=8, pady=8)
        ttk.Button(buttons, text="Find next", command=find_next).pack(side="left", padx=3)
        if replace:
            ttk.Button(buttons, text="Replace", command=replace_one).pack(side="left", padx=3)
            ttk.Button(buttons, text="Replace all", command=replace_all).pack(side="left", padx=3)
        ttk.Button(buttons, text="Close", command=dialog.destroy).pack(side="left", padx=3)
        find_entry.focus_set()
        dialog.bind("<Return>", lambda _e: find_next())

    def go_to_line(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        line = simpledialog.askinteger("Go to line", "Line number:", minvalue=1)
        if line is not None:
            self._jump_to_line(line)

    def show_completion(self) -> None:
        tab = self._active_document()
        if tab is None:
            return
        editor = tab.editor
        before = editor.get("insert linestart", "insert")
        match = re.search(r"[A-Za-z_][A-Za-z_0-9]*$", before)
        prefix = match.group(0) if match else ""
        try:
            values = self.ide.complete(prefix, limit=40)
        except (TypeError, ValueError):
            values = ()
        if not values:
            self._set_status("No completions")
            return
        self._hide_completion()
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=BORDER)
        listing = tk.Listbox(
            popup, bg=PANEL, fg=TEXT, selectbackground=ACCENT,
            selectforeground=DARK, relief="flat", height=min(10, len(values)),
            width=32, font=("Cascadia Mono", 10),
        )
        listing.pack(fill="both", expand=True, padx=1, pady=1)
        for value in values:
            listing.insert("end", value)
        listing.selection_set(0)
        box = editor.bbox("insert")
        if box:
            x = editor.winfo_rootx() + box[0]
            y = editor.winfo_rooty() + box[1] + box[3]
        else:
            x = editor.winfo_rootx() + 40
            y = editor.winfo_rooty() + 40
        popup.geometry(f"+{x}+{y}")
        listing.bind("<Double-Button-1>", lambda _e: self._accept_completion())
        listing.bind("<Return>", lambda _e: self._accept_completion())
        listing.bind("<Escape>", lambda _e: self._hide_completion())
        self._completion_window = popup
        self._completion_list = listing
        self._completion_prefix = prefix
        self._completion_doc = tab
        listing.focus_set()

    def _accept_completion(self) -> None:
        if self._completion_list is None or self._completion_doc is None:
            return
        selection = self._completion_list.curselection()
        if not selection:
            return
        value = self._completion_list.get(selection[0])
        editor = self._completion_doc.editor
        if self._completion_prefix:
            editor.delete(f"insert-{len(self._completion_prefix)}c", "insert")
        editor.insert("insert", value)
        editor.focus_set()
        self._hide_completion()
        editor.edit_modified(True)

    def _hide_completion(self) -> None:
        if self._completion_window is not None:
            try:
                self._completion_window.destroy()
            except tk.TclError:
                pass
        self._completion_window = None
        self._completion_list = None
        self._completion_doc = None

    def show_shortcuts(self) -> None:
        messagebox.showinfo(
            "Keyboard shortcuts",
            "Ctrl+N  New buffer\nCtrl+O  Open file\nCtrl+Shift+O  Open project\n"
            "Ctrl+S  Save\nCtrl+F  Find\nCtrl+H  Replace\nCtrl+G  Go to line\n"
            "Ctrl+/  Toggle comment\nCtrl+Space  Completion\nF5  Run file\n"
            "F6  Workspace check\nF7  Run tests\nShift+F5  Stop current task",
        )

    def show_about(self) -> None:
        messagebox.showinfo(
            "About SAMBU Studio",
            "SAMBU Studio — desktop workbench for the SAMBU language.\n\n"
            "Includes multi-file editing, syntax highlighting, document outline, "
            "diagnostics, bounded lexical completion, run/test/build tasks and "
            "workspace checks.\n\n"
            "The analyzer currently guarantees parsing and declared workspace checks; "
            "it is not a full static type/effect analyzer or native compiler.",
        )

    def show_devices(self) -> None:
        try:
            from sambu_ide.device_diagnostics import scan_apple_devices
            report = scan_apple_devices()
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("Apple device diagnostics", str(exc))
            return
        window = tk.Toplevel(self.root)
        window.title("Apple device diagnostics")
        window.geometry("760x520")
        window.configure(bg=DARK)
        tk.Label(
            window, text="APPLE DEVICE LINK", bg=DARK, fg=ACCENT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 8))
        box = tk.Text(
            window, bg=PANEL, fg=TEXT, relief="flat",
            font=("Cascadia Mono", 10), padx=14, pady=12, wrap="word",
        )
        box.pack(fill="both", expand=True, padx=18, pady=12)
        import json
        box.insert("1.0", json.dumps(report, ensure_ascii=False, indent=2))
        box.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    SambuStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
