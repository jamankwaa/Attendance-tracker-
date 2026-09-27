from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

from database import AttendanceDatabase, Student, validate_date


class AttendanceTracker(tk.Tk):
    COLORS = {
        "ink": "#17202A",
        "muted": "#667085",
        "line": "#D9E0E7",
        "paper": "#F7F9FB",
        "white": "#FFFFFF",
        "navy": "#153B50",
        "teal": "#157A78",
        "teal_light": "#DDF4F0",
        "gold": "#B7791F",
        "gold_light": "#FFF2D5",
        "red": "#B42318",
        "red_light": "#FEE4E2",
        "blue_light": "#E7F0FA",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Attendance Tracker")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg=self.COLORS["paper"])
        self.database = AttendanceDatabase()
        self.attendance_widgets: list[tuple[Student, ttk.Combobox, ttk.Entry]] = []
        self.student_selection: int | None = None
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._configure_styles()
        self._build_layout()
        self.refresh_all()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.COLORS["paper"])
        style.configure("Card.TFrame", background=self.COLORS["white"])
        style.configure("TLabel", background=self.COLORS["paper"], foreground=self.COLORS["ink"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=self.COLORS["paper"], foreground=self.COLORS["muted"], font=("Segoe UI", 9))
        style.configure("CardLabel.TLabel", background=self.COLORS["white"], foreground=self.COLORS["ink"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.COLORS["paper"], foreground=self.COLORS["navy"], font=("Segoe UI", 26, "bold"))
        style.configure("Subtitle.TLabel", background=self.COLORS["paper"], foreground=self.COLORS["muted"], font=("Segoe UI", 11))
        style.configure("Section.TLabel", background=self.COLORS["paper"], foreground=self.COLORS["navy"], font=("Segoe UI", 15, "bold"))
        style.configure("CardTitle.TLabel", background=self.COLORS["white"], foreground=self.COLORS["navy"], font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 7))
        style.configure("Primary.TButton", background=self.COLORS["teal"], foreground="white", borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#0F6260")])
        style.configure("Danger.TButton", background=self.COLORS["red"], foreground="white", borderwidth=0)
        style.configure("TNotebook", background=self.COLORS["paper"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 9), font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", self.COLORS["white"])], foreground=[("selected", self.COLORS["teal"])])
        style.configure("Treeview", background=self.COLORS["white"], fieldbackground=self.COLORS["white"], foreground=self.COLORS["ink"], rowheight=31, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#EEF2F6", foreground=self.COLORS["navy"], font=("Segoe UI", 9, "bold"), padding=7)
        style.map("Treeview", background=[("selected", "#CFEDEA")], foreground=[("selected", self.COLORS["ink"])])
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=6)

    def _build_layout(self) -> None:
        header = ttk.Frame(self, padding=(30, 24, 30, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Attendance Tracker", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="A calm, local workspace for knowing who showed up.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self.dashboard_tab = ttk.Frame(self.notebook, padding=18)
        self.attendance_tab = ttk.Frame(self.notebook, padding=18)
        self.students_tab = ttk.Frame(self.notebook, padding=18)
        self.reports_tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.attendance_tab, text="Take Attendance")
        self.notebook.add(self.students_tab, text="Students")
        self.notebook.add(self.reports_tab, text="Reports")
        self._build_dashboard()
        self._build_attendance()
        self._build_students()
        self._build_reports()

    def _card(self, parent: tk.Widget) -> ttk.Frame:
        return ttk.Frame(parent, style="Card.TFrame", padding=18)

    def _build_dashboard(self) -> None:
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(3, weight=1)
        ttk.Label(self.dashboard_tab, text="Today at a glance", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.dashboard_date_label = ttk.Label(self.dashboard_tab, style="Muted.TLabel")
        self.dashboard_date_label.grid(row=1, column=0, sticky="w", pady=(3, 15))
        cards = ttk.Frame(self.dashboard_tab)
        cards.grid(row=2, column=0, sticky="new")
        for index in range(5):
            cards.columnconfigure(index, weight=1)
        self.summary_labels: dict[str, ttk.Label] = {}
        card_specs = [("Total marked", "Total", self.COLORS["navy"]), ("Present", "Present", self.COLORS["teal"]), ("Late", "Late", self.COLORS["gold"]), ("Absent", "Absent", self.COLORS["red"]), ("Excused", "Excused", "#4B64A3")]
        for index, (caption, key, color) in enumerate(card_specs):
            card = self._card(cards)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 0 if index == 4 else 6))
            ttk.Label(card, text=caption, style="CardLabel.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="CardTitle.TLabel", font=("Segoe UI", 25, "bold"), foreground=color)
            value.pack(anchor="w", pady=(10, 0))
            self.summary_labels[key] = value
        recent = self._card(self.dashboard_tab)
        recent.grid(row=3, column=0, sticky="nsew", pady=(18, 0))
        recent.columnconfigure(0, weight=1)
        recent.rowconfigure(1, weight=1)
        ttk.Label(recent, text="Recent activity", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.recent_tree = self._tree(recent, [("date", "Date", 120), ("student", "Student", 220), ("status", "Status", 120), ("note", "Note", 420)])
        self.recent_tree.grid(row=1, column=0, sticky="nsew")

    def _build_attendance(self) -> None:
        self.attendance_tab.columnconfigure(0, weight=1)
        self.attendance_tab.rowconfigure(2, weight=1)
        toolbar = ttk.Frame(self.attendance_tab)
        toolbar.grid(row=0, column=0, sticky="ew")
        ttk.Label(toolbar, text="Date", style="Section.TLabel").pack(side="left")
        self.attendance_date = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(toolbar, textvariable=self.attendance_date, width=15)
        date_entry.pack(side="left", padx=(12, 8))
        date_entry.bind("<Return>", lambda _: self.load_attendance())
        ttk.Button(toolbar, text="Load", command=self.load_attendance).pack(side="left")
        ttk.Button(toolbar, text="Today", command=lambda: self._set_today()).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Mark everyone present", command=self.mark_everyone_present).pack(side="right")
        ttk.Label(self.attendance_tab, text="Choose a status and add an optional note for each student.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 13))
        self.attendance_canvas = tk.Canvas(self.attendance_tab, background=self.COLORS["paper"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.attendance_tab, orient="vertical", command=self.attendance_canvas.yview)
        self.attendance_canvas.configure(yscrollcommand=scrollbar.set)
        self.attendance_canvas.grid(row=2, column=0, sticky="nsew")
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.attendance_inner = ttk.Frame(self.attendance_canvas)
        self.attendance_window = self.attendance_canvas.create_window((0, 0), window=self.attendance_inner, anchor="nw")
        self.attendance_inner.bind("<Configure>", lambda _: self.attendance_canvas.configure(scrollregion=self.attendance_canvas.bbox("all")))
        self.attendance_canvas.bind("<Configure>", lambda event: self.attendance_canvas.itemconfigure(self.attendance_window, width=event.width))
        self.attendance_canvas.bind("<Enter>", lambda _: self.bind_all("<MouseWheel>", self._scroll_attendance))
        self.attendance_canvas.bind("<Leave>", lambda _: self.unbind_all("<MouseWheel>"))
        ttk.Button(self.attendance_tab, text="Save attendance", style="Primary.TButton", command=self.save_attendance).grid(row=3, column=0, sticky="e", pady=(14, 0))

    def _build_students(self) -> None:
        self.students_tab.columnconfigure(0, weight=1)
        self.students_tab.rowconfigure(1, weight=1)
        controls = ttk.Frame(self.students_tab)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        ttk.Label(controls, text="Student directory", style="Section.TLabel").pack(side="left")
        ttk.Button(controls, text="Add student", style="Primary.TButton", command=self.open_student_dialog).pack(side="right")
        ttk.Button(controls, text="Archive selected", style="Danger.TButton", command=self.archive_selected).pack(side="right", padx=8)
        self.student_tree = self._tree(self.students_tab, [("id", "ID", 130), ("name", "Name", 280), ("group", "Group", 220), ("active", "Status", 110)])
        self.student_tree.grid(row=1, column=0, sticky="nsew")
        self.student_tree.bind("<Double-1>", lambda _: self.edit_selected())
        self.student_tree.bind("<<TreeviewSelect>>", self._remember_student_selection)
        ttk.Button(self.students_tab, text="Edit selected", command=self.edit_selected).grid(row=2, column=0, sticky="e", pady=(12, 0))

    def _build_reports(self) -> None:
        self.reports_tab.columnconfigure(0, weight=1)
        self.reports_tab.rowconfigure(3, weight=1)
        self.reports_tab.rowconfigure(5, weight=2)
        filters = ttk.Frame(self.reports_tab)
        filters.grid(row=0, column=0, sticky="ew")
        ttk.Label(filters, text="Reports", style="Section.TLabel").pack(side="left")
        ttk.Label(filters, text="From").pack(side="left", padx=(28, 6))
        self.report_start = tk.StringVar()
        ttk.Entry(filters, textvariable=self.report_start, width=13).pack(side="left")
        ttk.Label(filters, text="To").pack(side="left", padx=(12, 6))
        self.report_end = tk.StringVar()
        ttk.Entry(filters, textvariable=self.report_end, width=13).pack(side="left")
        ttk.Label(filters, text="Group").pack(side="left", padx=(12, 6))
        self.report_group = ttk.Combobox(filters, width=17, state="readonly")
        self.report_group.pack(side="left")
        ttk.Button(filters, text="Apply filters", command=self.refresh_reports).pack(side="left", padx=10)
        ttk.Button(filters, text="Export CSV", style="Primary.TButton", command=self.export_report).pack(side="right")
        ttk.Label(self.reports_tab, text="Dates use YYYY-MM-DD. Leave a filter blank to include all values.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 13))
        ttk.Label(self.reports_tab, text="Per-student attendance rate (Present + Late, excused sessions not counted)", style="CardTitle.TLabel", background=self.COLORS["paper"]).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.stats_tree = self._tree(self.reports_tab, [("id", "Student ID", 120), ("student", "Student", 220), ("group", "Group", 140), ("present", "Present", 80), ("late", "Late", 70), ("absent", "Absent", 80), ("excused", "Excused", 80), ("rate", "Rate", 90)])
        self.stats_tree.configure(height=6)
        self.stats_tree.tag_configure("low", foreground=self.COLORS["red"])
        self.stats_tree.grid(row=3, column=0, sticky="nsew")
        ttk.Label(self.reports_tab, text="All records", style="CardTitle.TLabel", background=self.COLORS["paper"]).grid(row=4, column=0, sticky="w", pady=(16, 6))
        self.report_tree = self._tree(self.reports_tab, [("date", "Date", 115), ("id", "Student ID", 130), ("student", "Student", 220), ("group", "Group", 150), ("status", "Status", 120), ("note", "Note", 300)])
        self.report_tree.grid(row=5, column=0, sticky="nsew")

    def _tree(self, parent: tk.Widget, columns: list[tuple[str, str, int]]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=[item[0] for item in columns], show="headings", selectmode="browse")
        for identifier, heading, width in columns:
            tree.heading(identifier, text=heading)
            tree.column(identifier, width=width, anchor="w")
        return tree

    def refresh_all(self) -> None:
        self.refresh_dashboard()
        self.load_attendance()
        self.refresh_students()
        self.refresh_group_filter()
        self.refresh_reports()

    def refresh_dashboard(self) -> None:
        today = date.today().isoformat()
        summary = self.database.summary(today, today)
        self.dashboard_date_label.configure(text=f"{date.today().strftime('%A, %B %d, %Y')}  |  {len(self.database.students())} active students")
        for key, label in self.summary_labels.items():
            label.configure(text=str(summary[key]))
        self.recent_tree.delete(*self.recent_tree.get_children())
        for record in self.database.records()[:12]:
            self.recent_tree.insert("", "end", values=(record.attendance_date, record.student_name, record.status, record.note))

    def load_attendance(self) -> None:
        for child in self.attendance_inner.winfo_children():
            child.destroy()
        self.attendance_widgets.clear()
        try:
            attendance_date = validate_date(self.attendance_date.get()) or date.today().isoformat()
        except ValueError as exc:
            messagebox.showerror("Invalid date", str(exc))
            return
        self.attendance_date.set(attendance_date)
        students = self.database.students()
        existing = self.database.attendance_for_date(attendance_date) if students else {}
        if not students:
            ttk.Label(self.attendance_inner, text="No active students yet. Add students in the Students tab to begin.", style="Muted.TLabel").pack(anchor="w", pady=25)
            return
        header = ttk.Frame(self.attendance_inner)
        header.pack(fill="x", pady=(0, 6))
        ttk.Label(header, text="Student", style="Muted.TLabel", width=35).pack(side="left")
        ttk.Label(header, text="Status", style="Muted.TLabel", width=16).pack(side="left")
        ttk.Label(header, text="Note", style="Muted.TLabel").pack(side="left")
        for student in students:
            row = self._card(self.attendance_inner)
            row.pack(fill="x", pady=4)
            row.columnconfigure(2, weight=1)
            ttk.Label(row, text=f"{student.name}\n{student.student_id}  |  {student.group_name or 'No group'}", style="CardLabel.TLabel", width=35).grid(row=0, column=0, sticky="w")
            status = ttk.Combobox(row, values=AttendanceDatabase.STATUSES, state="readonly", width=13)
            status.set(existing.get(student.id, ("Present", ""))[0])
            status.grid(row=0, column=1, padx=(10, 18))
            note = ttk.Entry(row)
            note.insert(0, existing.get(student.id, ("Present", ""))[1])
            note.grid(row=0, column=2, sticky="ew")
            self.attendance_widgets.append((student, status, note))

    def save_attendance(self) -> None:
        if not self.attendance_widgets:
            messagebox.showinfo("Nothing to save", "Add at least one active student first.")
            return
        try:
            self.database.save_attendance(self.attendance_date.get().strip(), [(student.id, status.get(), note.get()) for student, status, note in self.attendance_widgets])
        except ValueError as exc:
            messagebox.showerror("Could not save attendance", str(exc))
            return
        self.refresh_dashboard()
        self.refresh_reports()
        messagebox.showinfo("Saved", f"Attendance saved for {self.attendance_date.get().strip()}.")

    def _scroll_attendance(self, event: tk.Event) -> None:
        self.attendance_canvas.yview_scroll(int(-event.delta / 120), "units")

    def mark_everyone_present(self) -> None:
        for _, status, _ in self.attendance_widgets:
            status.set("Present")

    def _set_today(self) -> None:
        self.attendance_date.set(date.today().isoformat())
        self.load_attendance()

    def refresh_students(self) -> None:
        self.student_tree.delete(*self.student_tree.get_children())
        for student in self.database.students():
            self.student_tree.insert("", "end", iid=str(student.id), values=(student.student_id, student.name, student.group_name or "-", "Active"))

    def _remember_student_selection(self, _event=None) -> None:
        selected = self.student_tree.selection()
        self.student_selection = int(selected[0]) if selected else None

    def open_student_dialog(self, student: Student | None = None) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Edit student" if student else "Add student")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=self.COLORS["paper"])
        body = ttk.Frame(dialog, padding=22)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Edit student" if student else "Add student", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        fields = [("Name", student.name if student else ""), ("Student ID", student.student_id if student else ""), ("Group", student.group_name if student else "")]
        variables: list[tk.StringVar] = []
        for row, (label, value) in enumerate(fields, start=1):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 15))
            variable = tk.StringVar(value=value)
            variables.append(variable)
            ttk.Entry(body, textvariable=variable, width=32).grid(row=row, column=1, pady=6)
        def submit() -> None:
            try:
                if student:
                    self.database.update_student(student.id, *(variable.get() for variable in variables))
                else:
                    self.database.add_student(*(variable.get() for variable in variables))
            except ValueError as exc:
                messagebox.showerror("Could not save student", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh_all()
        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="left", padx=6)
        ttk.Button(buttons, text="Save student", style="Primary.TButton", command=submit).pack(side="left")

    def edit_selected(self) -> None:
        if self.student_selection is None:
            messagebox.showinfo("Select a student", "Choose a student first.")
            return
        student = self.database.get_student(self.student_selection)
        if student:
            self.open_student_dialog(student)

    def archive_selected(self) -> None:
        if self.student_selection is None:
            messagebox.showinfo("Select a student", "Choose a student first.")
            return
        student = self.database.get_student(self.student_selection)
        if student and messagebox.askyesno("Archive student", f"Archive {student.name}? Existing attendance will be kept."):
            self.database.deactivate_student(student.id)
            self.student_selection = None
            self.refresh_all()

    def refresh_group_filter(self) -> None:
        groups = sorted({student.group_name for student in self.database.students() if student.group_name})
        self.report_group["values"] = ["All groups", *groups]
        if not self.report_group.get():
            self.report_group.set("All groups")

    def _report_filters(self) -> tuple[str | None, str | None, str | None]:
        group = self.report_group.get()
        return self.report_start.get().strip() or None, self.report_end.get().strip() or None, None if group in ("", "All groups") else group

    def refresh_reports(self) -> None:
        start_date, end_date, group = self._report_filters()
        self.report_tree.delete(*self.report_tree.get_children())
        self.stats_tree.delete(*self.stats_tree.get_children())
        try:
            rows = self.database.records(start_date, end_date, group)
            stats = self.database.student_stats(start_date, end_date, group)
        except ValueError as exc:
            messagebox.showerror("Could not load report", str(exc))
            return
        for item in stats:
            self.stats_tree.insert("", "end", values=(item.student_code, item.student_name, item.group_name or "-", item.present, item.late, item.absent, item.excused, f"{item.rate:.0f}%"), tags=("low",) if item.rate < 75 else ())
        for record in rows:
            self.report_tree.insert("", "end", values=(record.attendance_date, record.student_code, record.student_name, record.group_name or "-", record.status, record.note))

    def export_report(self) -> None:
        destination = filedialog.asksaveasfilename(title="Export attendance report", defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not destination:
            return
        try:
            count = self.database.export_csv(destination, *self._report_filters())
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        messagebox.showinfo("Export complete", f"Exported {count} attendance records.")

    def _close(self) -> None:
        self.database.close()
        self.destroy()


if __name__ == "__main__":
    AttendanceTracker().mainloop()
