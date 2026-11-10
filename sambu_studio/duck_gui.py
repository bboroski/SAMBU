"""SAMBU Duck Studio: an optional, read-only desktop workspace UI.

The Tkinter shell wraps SAMBU Studio's existing local Magento XML inspector.
It never starts Magento, connects to services, or modifies the inspected
project. JSON report export is an explicit user action.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import queue
import threading
from typing import Any


PALETTE = {
    "sidebar": "#142235", "sidebar_muted": "#91A2B7", "sidebar_active": "#243A52",
    "page": "#F3F6FA", "card": "#FFFFFF", "ink": "#18283B", "muted": "#718096",
    "line": "#E3EAF1", "teal": "#23877E", "teal_soft": "#E5F4F1",
    "amber": "#C28A32", "amber_soft": "#FFF4E1", "red": "#C45B60",
    "red_soft": "#FCEDEF", "blue": "#557EB2", "blue_soft": "#EAF1FA",
    "green": "#328466", "green_soft": "#E7F4ED",
}


@dataclass(frozen=True)
class Summary:
    files: int
    preferences: int
    plugins: int
    topics: int
    consumers: int
    exchanges: int
    bindings: int
    publishers: int
    errors: int
    warnings: int


def summary_from_report(report: Any) -> Summary:
    """Extract a stable, display-only summary from InspectionReport or JSON."""
    payload = report.to_dict() if hasattr(report, "to_dict") else report
    summary = payload.get("summary", {})
    return Summary(
        files=int(summary.get("files_scanned", 0)),
        preferences=int(summary.get("preferences", 0)),
        plugins=int(summary.get("plugins", 0)),
        topics=int(summary.get("topics", 0)),
        consumers=int(summary.get("consumers", 0)),
        exchanges=int(summary.get("exchanges", 0)),
        bindings=int(summary.get("bindings", 0)),
        publishers=int(summary.get("publishers", 0)),
        errors=int(summary.get("errors", 0)),
        warnings=int(summary.get("warnings", 0)),
    )


def health_label(summary: Summary) -> tuple[str, str]:
    if summary.errors:
        return "ACTION REQUIRED", "red"
    if summary.warnings:
        return "REVIEW SUGGESTED", "amber"
    return "STATIC CHECKS PASSED", "green"


def file_rows_from_report(report: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Summarise recognised XML files and surface warnings as review rows."""
    count_by_file: dict[str, int] = {}
    fields = ("preferences", "plugins", "topics", "consumers", "exchanges", "bindings", "publishers")
    for field in fields:
        for record in report.get(field, []):
            path = str(record.get("path", ""))
            count_by_file[path] = count_by_file.get(path, 0) + 1
    severity_by_file: dict[str, str] = {}
    priority = {"info": 0, "warning": 1, "error": 2}
    for item in report.get("diagnostics", []):
        path = str(item.get("path", ""))
        severity = str(item.get("severity", "info")).lower()
        previous = severity_by_file.get(path, "info")
        if priority.get(severity, 0) > priority.get(previous, 0):
            severity_by_file[path] = severity
    rows = []
    for path in report.get("files_scanned", []):
        severity = severity_by_file.get(path, "info")
        status = "ERROR" if severity == "error" else "REVIEW" if severity == "warning" else "PASSED"
        rows.append((path, str(count_by_file.get(path, 0)), status))
    return rows or [("No supported XML files found", "0", "REVIEW")]


class DuckStudioApp:
    """Tkinter desktop application for local SAMBU Studio inspection."""

    def __init__(self, root: Any):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.root.title("SAMBU Duck Studio")
        self.root.geometry("1440x920")
        self.root.minsize(1120, 740)
        self.root.configure(bg=PALETTE["page"])
        self.root.option_add("*Font", "TkDefaultFont 10")

        self.workspace: Path | None = None
        self.report: Any | None = None
        self.payload: dict[str, Any] | None = None
        self.active_view = "overview"
        self.busy = False
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self._configure_styles()
        self._build_shell()
        self._show_overview()
        self.root.after(100, self._drain_events)

    def _configure_styles(self) -> None:
        style = self.ttk.Style()
        try:
            style.theme_use("clam")
        except self.tk.TclError:
            pass
        style.configure(
            "Treeview", background="white", foreground=PALETTE["ink"],
            fieldbackground="white", rowheight=34, borderwidth=0,
            font=("TkDefaultFont", 9),
        )
        style.configure(
            "Treeview.Heading", background="#F5F8FB", foreground=PALETTE["muted"],
            font=("TkDefaultFont", 8), relief="flat",
        )
        style.map(
            "Treeview", background=[("selected", "#E9F2F7")],
            foreground=[("selected", PALETTE["ink"])],
        )
        style.configure(
            "Vertical.TScrollbar", background="#D8E1EA", troughcolor="#F5F7FA",
            bordercolor="#F5F7FA", arrowcolor="#7F91A6",
        )

    def _build_shell(self) -> None:
        tk = self.tk
        self.shell = tk.Frame(self.root, bg=PALETTE["page"])
        self.shell.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(self.shell, bg=PALETTE["sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = tk.Frame(self.sidebar, bg=PALETTE["sidebar"], padx=22, pady=24)
        brand.pack(fill="x")
        tk.Label(brand, text="🦆", bg=PALETTE["sidebar"], fg="white",
                 font=("TkDefaultFont", 26)).pack(anchor="w")
        tk.Label(brand, text="SAMBU", bg=PALETTE["sidebar"], fg="white",
                 font=("TkDefaultFont", 19, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Label(brand, text="DUCK STUDIO", bg=PALETTE["sidebar"], fg="#82C8BE",
                 font=("TkDefaultFont", 8, "bold")).pack(anchor="w", pady=(1, 0))
        tk.Frame(self.sidebar, bg="#31445B", height=1).pack(fill="x", padx=20, pady=(2, 18))
        tk.Label(self.sidebar, text="WORKSPACE", bg=PALETTE["sidebar"], fg="#70849B",
                 font=("TkDefaultFont", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 10))
        self.nav_buttons: dict[str, Any] = {}
        for key, title, glyph in [
            ("overview", "Overview", "▦"),
            ("inspector", "XML Inspector", "⌕"),
            ("reports", "Reports & findings", "☷"),
        ]:
            button = tk.Button(
                self.sidebar, text=f"  {glyph}    {title}", anchor="w",
                command=lambda view=key: self.show_view(view),
                bg=PALETTE["sidebar"], fg="#CFD8E3",
                activebackground=PALETTE["sidebar_active"], activeforeground="white",
                relief="flat", bd=0, padx=18, pady=12, font=("TkDefaultFont", 10),
                cursor="hand2", highlightthickness=0,
            )
            button.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[key] = button
        footer = tk.Frame(self.sidebar, bg=PALETTE["sidebar"], padx=20, pady=18)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, bg="#31445B", height=1).pack(fill="x", pady=(0, 15))
        tk.Label(footer, text="LOCAL · READ ONLY", bg=PALETTE["sidebar"],
                 fg="#82C8BE", font=("TkDefaultFont", 8, "bold")).pack(anchor="w")
        tk.Label(
            footer, text="No production writes\nNo network calls", bg=PALETTE["sidebar"],
            fg=PALETTE["sidebar_muted"], font=("TkDefaultFont", 8), justify="left",
        ).pack(anchor="w", pady=(6, 0))

        self.main = tk.Frame(self.shell, bg=PALETTE["page"])
        self.main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(self.main, bg="white", height=62, padx=28)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(
            top, text="Workspace  /  Static inspection", bg="white",
            fg=PALETTE["muted"], font=("TkDefaultFont", 9),
        ).pack(side="left", anchor="center")
        self.status_pill = tk.Label(
            top, text="●  NO WORKSPACE", bg=PALETTE["blue_soft"], fg=PALETTE["blue"],
            padx=12, pady=6, font=("TkDefaultFont", 8, "bold"),
        )
        self.status_pill.pack(side="right", pady=12)
        self.body = tk.Frame(self.main, bg=PALETTE["page"], padx=30, pady=25)
        self.body.pack(fill="both", expand=True)
        self._build_toast()

    def _build_toast(self) -> None:
        self.toast = self.tk.Label(
            self.main, text="", bg=PALETTE["teal"], fg="white",
            padx=14, pady=8, font=("TkDefaultFont", 9),
        )

    def _notify(self, message: str, tone: str = "teal") -> None:
        self.toast.configure(text=message, bg=PALETTE.get(tone, PALETTE["teal"]))
        self.toast.place(relx=1.0, x=-28, y=76, anchor="ne")
        self.root.after(2800, self.toast.place_forget)

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()

    def _card(self, parent: Any, padx: int = 18, pady: int = 16) -> Any:
        return self.tk.Frame(
            parent, bg=PALETTE["card"], highlightbackground=PALETTE["line"],
            highlightthickness=1, padx=padx, pady=pady,
        )

    def _label(self, parent: Any, text: str, *, size: int = 10, color: str | None = None,
               weight: str = "normal", bg: str = "white", **kwargs: Any) -> Any:
        font = ("TkDefaultFont", size, "bold") if weight == "bold" else ("TkDefaultFont", size)
        return self.tk.Label(parent, text=text, bg=bg, fg=color or PALETTE["ink"],
                             font=font, **kwargs)

    def _button(self, parent: Any, text: str, command: Any, *, primary: bool = False,
                compact: bool = False) -> Any:
        bg = PALETTE["teal"] if primary else "#FFFFFF"
        fg = "white" if primary else PALETTE["ink"]
        return self.tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground="#1C7069" if primary else "#EDF2F7",
            activeforeground="white" if primary else PALETTE["ink"],
            relief="flat", bd=0, padx=14 if not compact else 10,
            pady=9 if not compact else 6, font=("TkDefaultFont", 9),
            cursor="hand2", highlightthickness=0,
        )

    def _heading(self, title: str, subtitle: str) -> Any:
        row = self.tk.Frame(self.body, bg=PALETTE["page"])
        row.pack(fill="x", pady=(0, 20))
        left = self.tk.Frame(row, bg=PALETTE["page"])
        left.pack(side="left", fill="x", expand=True)
        self._label(left, title, size=22, weight="bold", bg=PALETTE["page"]).pack(anchor="w")
        self._label(left, subtitle, size=9, color=PALETTE["muted"],
                    bg=PALETTE["page"]).pack(anchor="w", pady=(5, 0))
        return row

    def _workspace_controls(self, parent: Any) -> None:
        row = self.tk.Frame(parent, bg=PALETTE["page"])
        row.pack(fill="x", pady=(0, 18))
        path = str(self.workspace) if self.workspace else "Choose a local Magento module folder"
        self._label(row, path, size=9, color=PALETTE["muted"], bg=PALETTE["page"]).pack(side="left", anchor="center")
        self._button(row, "Open folder", self.open_workspace, compact=True).pack(side="right", padx=(8, 0))
        self._button(row, "Run inspection", self.inspect_workspace, primary=True, compact=True).pack(side="right")

    def _metric_card(self, parent: Any, title: str, value: str, note: str, accent: str) -> None:
        card = self._card(parent, 16, 14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self._label(card, title.upper(), size=8, color=PALETTE["muted"], weight="bold").pack(anchor="w")
        self._label(card, value, size=24, weight="bold").pack(anchor="w", pady=(8, 2))
        self._label(card, note, size=8, color=accent).pack(anchor="w")

    def _show_overview(self) -> None:
        self.active_view = "overview"
        self._clear_body()
        self._heading("Project overview", "A quiet control room for local configuration, queues and dependencies.")
        self._workspace_controls(self.body)
        summary = summary_from_report(self.payload) if self.payload else Summary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        metrics = self.tk.Frame(self.body, bg=PALETTE["page"])
        metrics.pack(fill="x", pady=(0, 18))
        self._metric_card(metrics, "Files scanned", str(summary.files), "Selected XML files", PALETTE["blue"])
        self._metric_card(metrics, "DI preferences", str(summary.preferences), "Interface mappings", PALETTE["teal"])
        self._metric_card(metrics, "Plugins", str(summary.plugins), "Observed type hooks", PALETTE["blue"])
        self._metric_card(metrics, "Queue topics", str(summary.topics), "Message contracts", PALETTE["amber"])
        lower = self.tk.Frame(self.body, bg=PALETTE["page"])
        lower.pack(fill="both", expand=True)
        left = self._card(lower, 18, 17)
        left.pack(side="left", fill="both", expand=True, padx=(0, 15))
        self._label(left, "Configuration map", size=12, weight="bold").pack(anchor="w")
        self._label(left, "Read-only inventory of recognised Magento XML files", size=8,
                    color=PALETTE["muted"]).pack(anchor="w", pady=(4, 12))
        self._make_file_table(left, height=6)
        right = self._card(lower, 18, 17)
        right.pack(side="right", fill="y")
        self._label(right, "Workspace health", size=12, weight="bold").pack(anchor="w")
        state, tone = health_label(summary)
        color = PALETTE["green"] if tone == "green" else PALETTE["amber"] if tone == "amber" else PALETTE["red"]
        self._label(right, state, size=9, color=color, weight="bold").pack(anchor="w", pady=(16, 6))
        self._label(right, f"{summary.errors} errors  ·  {summary.warnings} warnings",
                    size=9, color=PALETTE["muted"]).pack(anchor="w")
        self.tk.Frame(right, bg=PALETTE["line"], height=1).pack(fill="x", pady=16)
        self._label(right, "Inspection boundaries", size=9, weight="bold").pack(anchor="w")
        for item in ["No Magento runtime required", "No network or broker calls", "No configuration writes"]:
            self._label(right, "✓  " + item, size=8, color=PALETTE["muted"]).pack(anchor="w", pady=(8, 0))
        self.tk.Frame(right, bg=PALETTE["line"], height=1).pack(fill="x", pady=16)
        self._button(right, "View diagnostics", lambda: self.show_view("reports")).pack(fill="x")

    def _make_file_table(self, parent: Any, height: int = 7) -> Any:
        table = self.ttk.Treeview(parent, columns=("file", "records", "status"),
                                  show="headings", height=height)
        for column, heading, width, anchor in [
            ("file", "CONFIGURATION FILE", 235, "w"),
            ("records", "RECORDS", 80, "center"),
            ("status", "STATUS", 100, "center"),
        ]:
            table.heading(column, text=heading)
            table.column(column, width=width, anchor=anchor)
        table.tag_configure("ok", foreground=PALETTE["green"])
        table.tag_configure("warn", foreground=PALETTE["amber"])
        table.tag_configure("error", foreground=PALETTE["red"])
        for row in self._file_rows():
            tag = "error" if row[2] == "ERROR" else "warn" if row[2] == "REVIEW" else "ok"
            table.insert("", "end", values=row, tags=(tag,))
        table.pack(fill="both", expand=True)
        return table

    def _file_rows(self) -> list[tuple[str, str, str]]:
        return file_rows_from_report(self.payload or {"files_scanned": []})

    def _show_inspector(self) -> None:
        self.active_view = "inspector"
        self._clear_body()
        self._heading("XML Inspector", "Inspect dependency injection and message-queue configuration without executing it.")
        self._workspace_controls(self.body)
        content = self.tk.Frame(self.body, bg=PALETTE["page"])
        content.pack(fill="both", expand=True)
        files = self._card(content, 18, 17)
        files.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self._label(files, "Recognised files", size=12, weight="bold").pack(anchor="w")
        self._label(files, "di.xml · communication.xml · queue contracts", size=8,
                    color=PALETTE["muted"]).pack(anchor="w", pady=(4, 14))
        self._make_file_table(files, height=11)
        detail = self._card(content, 18, 17)
        detail.pack(side="right", fill="both", expand=True)
        self._label(detail, "Inspection results", size=12, weight="bold").pack(anchor="w")
        if self.payload:
            summary = summary_from_report(self.payload)
            self._label(detail, f"{summary.files} files  ·  {summary.errors} errors  ·  {summary.warnings} warnings",
                        size=9, color=PALETTE["muted"]).pack(anchor="w", pady=(4, 12))
            diagnostics = self.payload.get("diagnostics", [])
        else:
            self._label(detail, "No inspection run yet", size=9, color=PALETTE["muted"]).pack(anchor="w", pady=(4, 12))
            diagnostics = []
        text = self.tk.Text(detail, height=14, bg="#F8FAFC", fg=PALETTE["ink"],
                            relief="flat", bd=0, wrap="word", padx=12, pady=10,
                            font=("TkFixedFont", 9))
        text.pack(fill="both", expand=True)
        if not diagnostics:
            text.insert("end", "Choose a local folder and run inspection to see findings.\n")
        for item in diagnostics:
            severity = str(item.get("severity", "info")).upper()
            text.insert("end", f"{severity:<7} {item.get('code', '')}\n", severity)
            text.insert("end", f"{item.get('path', '')}\n{item.get('message', '')}\n\n")
        text.tag_configure("ERROR", foreground=PALETTE["red"], font=("TkFixedFont", 9, "bold"))
        text.tag_configure("WARNING", foreground=PALETTE["amber"], font=("TkFixedFont", 9, "bold"))
        text.tag_configure("INFO", foreground=PALETTE["teal"], font=("TkFixedFont", 9, "bold"))
        text.configure(state="disabled")
        self._button(detail, "Export JSON report", self.export_report, primary=True).pack(anchor="e", pady=(12, 0))

    def _show_reports(self) -> None:
        self.active_view = "reports"
        self._clear_body()
        self._heading("Reports & findings", "Every finding keeps its original diagnostic code and source file.")
        self._workspace_controls(self.body)
        card = self._card(self.body, 18, 17)
        card.pack(fill="both", expand=True)
        summary = summary_from_report(self.payload or {"summary": {}})
        self._label(card, "Review summary", size=12, weight="bold").pack(anchor="w")
        self._label(card, f"{summary.errors} errors   ·   {summary.warnings} warnings",
                    size=9, color=PALETTE["muted"]).pack(anchor="w", pady=(4, 14))
        text = self.tk.Text(card, bg="#F8FAFC", fg=PALETTE["ink"], relief="flat", bd=0,
                            wrap="word", padx=14, pady=12, font=("TkFixedFont", 9))
        text.pack(fill="both", expand=True)
        diagnostics = self.payload.get("diagnostics", []) if self.payload else []
        if not diagnostics:
            text.insert("end", "No inspection has run yet.\n")
        for item in diagnostics:
            severity = str(item.get("severity", "info")).upper()
            text.insert("end", f"[{severity}] {item.get('code', '')}  {item.get('path', '')}\n", severity)
            text.insert("end", f"{item.get('message', '')}\n\n")
        text.tag_configure("ERROR", foreground=PALETTE["red"], font=("TkFixedFont", 9, "bold"))
        text.tag_configure("WARNING", foreground=PALETTE["amber"], font=("TkFixedFont", 9, "bold"))
        text.configure(state="disabled")
        self._button(card, "Export JSON report", self.export_report, primary=True).pack(anchor="e", pady=(12, 0))

    def show_view(self, view: str) -> None:
        if view not in {"overview", "inspector", "reports"}:
            return
        self.active_view = view
        for key, button in self.nav_buttons.items():
            button.configure(bg=PALETTE["sidebar_active"] if key == view else PALETTE["sidebar"],
                             fg="white" if key == view else "#CFD8E3")
        {"overview": self._show_overview, "inspector": self._show_inspector,
         "reports": self._show_reports}[view]()

    def open_workspace(self) -> None:
        from tkinter import filedialog
        selected = filedialog.askdirectory(title="Choose a local Magento module or project")
        if not selected:
            return
        self.workspace = Path(selected).resolve()
        self.payload = None
        self.report = None
        self.status_pill.configure(text="●  LOCAL WORKSPACE", bg=PALETTE["blue_soft"], fg=PALETTE["blue"])
        self.show_view(self.active_view)
        self.inspect_workspace()

    def inspect_workspace(self) -> None:
        if self.busy:
            return
        if not self.workspace:
            self._notify("Choose a local folder before running inspection.", "amber")
            return
        self.busy = True
        self._notify("Inspecting local XML files…", "blue")
        workspace = self.workspace

        def work() -> None:
            try:
                from .magento import inspect_module
                report = inspect_module(workspace)
                self.events.put(("success", report))
            except Exception as exc:
                self.events.put(("error", exc))

        threading.Thread(target=work, daemon=True, name="duck-studio-inspection").start()

    def _drain_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                self.busy = False
                if kind == "success":
                    self.report = value
                    self.payload = value.to_dict()
                    self.show_view(self.active_view)
                    summary = summary_from_report(value)
                    tone = "green" if not summary.errors and not summary.warnings else "amber" if not summary.errors else "red"
                    error_word = "error" if summary.errors == 1 else "errors"
                    warning_word = "warning" if summary.warnings == 1 else "warnings"
                    self._notify(
                        f"Inspection complete · {summary.files} files · "
                        f"{summary.errors} {error_word} · {summary.warnings} {warning_word}",
                        tone,
                    )
                else:
                    self._notify(f"Inspection failed: {value}", "red")
        except queue.Empty:
            pass
        self.root.after(100, self._drain_events)

    def export_report(self) -> None:
        if self.payload is None:
            self._notify("Run an inspection before exporting a report.", "amber")
            return
        from tkinter import filedialog
        target = filedialog.asksaveasfilename(
            title="Export SAMBU Studio report", defaultextension=".json",
            filetypes=[("JSON report", "*.json")], initialfile="sambu-studio-report.json",
        )
        if not target:
            return
        Path(target).write_text(json.dumps(self.payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._notify("JSON report exported.", "green")


def main(argv: list[str] | None = None) -> int:
    """Launch the optional Duck Studio desktop UI."""
    try:
        import tkinter as tk
    except ImportError as exc:
        raise SystemExit("SAMBU Duck Studio requires a Python build with Tk support") from exc
    root = tk.Tk()
    DuckStudioApp(root)
    root.mainloop()
    return 0


__all__ = [
    "DuckStudioApp", "Summary", "file_rows_from_report", "health_label",
    "main", "summary_from_report",
]

if __name__ == "__main__":
    raise SystemExit(main())
