"""
MEAP DEMO - Manufacturing Equipment and Analysis Platform (standalone demo)
MagMotion - Python GUI
"""

import csv
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk

import serial
import serial.tools.list_ports

APP_TITLE = "MEAP DEMO"
CSV_FILE = Path(__file__).parent / "sensor_assemblies.csv"
BAUD_RATE = 115200
POLL_MS = 50

# Status table columns
STATUS_COLUMNS = [
    "Sensor",
    "Comms",
    "Hall range",
    "IDOD",
    "Synced error",
    "Sequence error",
    "Noise",
    "Null center",
]


def load_sensor_assemblies(csv_path: Path):
    items = {}
    if not csv_path.exists():
        return items

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.lstrip("\ufeff").strip(): v for k, v in row.items() if k}
            item = (cleaned.get("Item Number") or "").strip()
            heads = (cleaned.get("Heads") or "").strip()
            per_head = (cleaned.get("Sensors per head") or "").strip()
            if not item or not heads or not per_head:
                continue
            if item in items:
                continue
            try:
                items[item] = (int(heads), int(per_head))
            except ValueError:
                continue
    return items


def list_serial_ports():
    return [p.device for p in serial.tools.list_ports.comports()]


class SerialReader:
    def __init__(self, port: str, baud: int = BAUD_RATE, timeout: float = 0.05):
        self.ser = serial.Serial(port, baud, timeout=timeout)

    def read_latest(self):
        newest_vals = None
        sensor_count = None
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
            except Exception:
                return None, None
            if not line:
                continue
            if line.startswith("NUMSENS:"):
                try:
                    sensor_count = int(line.split(":", 1)[1].strip())
                except ValueError:
                    sensor_count = None
                continue
            parts = [p.strip() for p in line.split(",") if p.strip()]
            try:
                nums = [int(p) for p in parts]
            except ValueError:
                continue
            if nums:
                newest_vals = nums
        return newest_vals, sensor_count

    def close(self):
        if self.ser.is_open:
            self.ser.close()


class BarChart(tk.Canvas):
    def __init__(self, parent, max_bars=32, max_value=65535, **kwargs):
        super().__init__(parent, **kwargs)
        self.max_bars = max_bars
        self.max_value = max_value
        self.values = [0] * max_bars
        self.labels = [""] * max_bars
        self.is_idod = [False] * max_bars
        self.bind("<Configure>", lambda _e: self.draw())

    def set_values(self, values):
        vals = list(values)[: self.max_bars]
        if len(vals) < self.max_bars:
            vals.extend([0] * (self.max_bars - len(vals)))
        self.values = vals
        self.draw()

    def set_labels(self, labels, idod_flags):
        labs = list(labels)[: self.max_bars]
        if len(labs) < self.max_bars:
            labs.extend([""] * (self.max_bars - len(labs)))
        flags = list(idod_flags)[: self.max_bars]
        if len(flags) < self.max_bars:
            flags.extend([False] * (self.max_bars - len(flags)))
        self.labels = labs
        self.is_idod = flags
        self.draw()

    def draw(self):
        self.delete("all")
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        padding = 10
        left_axis_w = 40
        bottom_axis_h = 22
        bar_area_w = w - 2 * padding
        bar_area_h = h - 2 * padding - bottom_axis_h
        if bar_area_w <= 0 or bar_area_h <= 0:
            return

        max_val = max(self.max_value, 1)
        bar_w = (bar_area_w - left_axis_w) / self.max_bars

        # Y-axis labels
        tick_count = 5
        for i in range(tick_count + 1):
            val = int((max_val / tick_count) * i)
            y = padding + bar_area_h - (bar_area_h * i / tick_count)
            self.create_text(
                padding + left_axis_w - 6,
                y,
                text=str(val),
                anchor="e",
                fill="#5A6B7A",
            )
            self.create_line(
                padding + left_axis_w,
                y,
                w - padding,
                y,
                fill="#E3E8EE",
            )

        for i, v in enumerate(self.values):
            x0 = padding + left_axis_w + i * bar_w + 1
            x1 = padding + left_axis_w + (i + 1) * bar_w - 1
            bar_h = (v / max_val) * bar_area_h
            y0 = padding + (bar_area_h - bar_h)
            y1 = padding + bar_area_h
            color = "#D88A2D" if self.is_idod[i] else "#3B6EA8"
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            if self.labels[i]:
                self.create_text(
                    (x0 + x1) / 2,
                    padding + bar_area_h + 12,
                    text=self.labels[i],
                    anchor="n",
                    fill="#5A6B7A",
                    font=("Segoe UI", 8),
                )


class MEAPDemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        base_w, base_h = 1500, 700
        default_w = int(base_w * 1.2)
        self.minsize(default_w, base_h)
        self.geometry(f"{default_w}x{base_h}")

        self.items = load_sensor_assemblies(CSV_FILE)
        self.item_numbers = sorted(self.items.keys())

        self.selected_item = tk.StringVar()
        self.heads_var = tk.StringVar(value="Heads: -")
        self.per_head_var = tk.StringVar(value="Sensors per head: -")
        self.total_sensors = 0
        self.heads = 0
        self.per_head = 0
        self.port_var = tk.StringVar()
        self.conn_status_var = tk.StringVar(value="Serial: disconnected")
        self.last_update_var = tk.StringVar(value="Last update: --")
        self.sensor_count_var = tk.StringVar(value="Detected sensors: --")
        self.reader = None
        self.include_sync_sequence = tk.BooleanVar(value=True)
        self.slow_scan_var = tk.BooleanVar(value=False)

        self._build_ui()
        if self.item_numbers:
            self.selected_item.set(self.item_numbers[0])
            self.on_item_change()

    def _build_ui(self):
        header = tk.Frame(self, bg="#1E2A36")
        header.pack(fill=tk.X)
        title = tk.Label(
            header,
            text="MEAP DEMO",
            fg="white",
            bg="#1E2A36",
            font=("Segoe UI", 20, "bold"),
            padx=16,
            pady=10,
        )
        title.pack(anchor="w")
        subtitle = tk.Label(
            header,
            text="Standalone GUI for sensor test data (MEAP integration pending)",
            fg="#C7D4E1",
            bg="#1E2A36",
            font=("Segoe UI", 10),
            padx=16,
            pady=2,
        )
        subtitle.pack(anchor="w")

        body = tk.Frame(self, bg="#F4F6F8")
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg="#F4F6F8", padx=16, pady=16)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = tk.Frame(body, bg="#F4F6F8", padx=16, pady=16)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Controls
        tk.Label(
            left, text="Sensor Item Number", font=("Segoe UI", 11, "bold"), bg="#F4F6F8"
        ).pack(anchor="w")
        combo = ttk.Combobox(
            left,
            textvariable=self.selected_item,
            values=self.item_numbers,
            state="normal",
            width=24,
        )
        combo.pack(anchor="w", pady=(4, 12))
        combo.bind("<<ComboboxSelected>>", lambda _e: self.on_item_change())

        tk.Label(left, textvariable=self.heads_var, bg="#F4F6F8").pack(anchor="w")
        tk.Label(left, textvariable=self.per_head_var, bg="#F4F6F8").pack(anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, pady=12)

        tk.Label(left, text="Serial Port", font=("Segoe UI", 11, "bold"), bg="#F4F6F8").pack(
            anchor="w"
        )
        ports = list_serial_ports()
        if ports:
            self.port_var.set(ports[0])
        self.port_combo = ttk.Combobox(
            left, textvariable=self.port_var, values=ports, state="readonly", width=24
        )
        self.port_combo.pack(anchor="w", pady=(4, 8))

        btn_row = tk.Frame(left, bg="#F4F6F8")
        btn_row.pack(anchor="w", pady=(0, 8))
        ttk.Button(btn_row, text="Refresh", command=self.refresh_ports).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        self.connect_btn = ttk.Button(btn_row, text="Connect", command=self.toggle_connect)
        self.connect_btn.pack(side=tk.LEFT)

        tk.Label(left, textvariable=self.conn_status_var, bg="#F4F6F8").pack(anchor="w")
        tk.Label(left, textvariable=self.last_update_var, bg="#F4F6F8").pack(anchor="w")
        tk.Label(left, textvariable=self.sensor_count_var, bg="#F4F6F8").pack(anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, pady=12)
        tk.Label(left, text="Tests", font=("Segoe UI", 11, "bold"), bg="#F4F6F8").pack(
            anchor="w"
        )
        ttk.Checkbutton(
            left,
            text="Hall range also checks synced/sequence",
            variable=self.include_sync_sequence,
        ).pack(anchor="w", pady=(4, 8))

        test_row1 = tk.Frame(left, bg="#F4F6F8")
        test_row1.pack(anchor="w", pady=(0, 6))
        ttk.Button(test_row1, text="Test COMMs", command=self.test_comms).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(test_row1, text="Test HALL Range", command=self.test_hall).pack(
            side=tk.LEFT
        )

        test_row2 = tk.Frame(left, bg="#F4F6F8")
        test_row2.pack(anchor="w", pady=(0, 6))
        ttk.Button(test_row2, text="Test IDOD", command=self.test_idod).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(test_row2, text="Test NULL Center", command=self.test_null_center).pack(
            side=tk.LEFT
        )

        test_row3 = tk.Frame(left, bg="#F4F6F8")
        test_row3.pack(anchor="w", pady=(0, 6))
        ttk.Button(test_row3, text="Test Noise", command=self.test_noise).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(test_row3, text="Test Synced Error", command=self.test_synced).pack(
            side=tk.LEFT
        )

        test_row4 = tk.Frame(left, bg="#F4F6F8")
        test_row4.pack(anchor="w")
        ttk.Button(
            test_row4, text="Test Sequence Error", command=self.test_sequence
        ).pack(side=tk.LEFT)

        test_row5 = tk.Frame(left, bg="#F4F6F8")
        test_row5.pack(anchor="w", pady=(8, 0))
        ttk.Button(test_row5, text="Start READ", command=self.start_read).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(test_row5, text="Start SCAN", command=self.start_scan).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(test_row5, text="STOP", command=self.stop_motion).pack(side=tk.LEFT)

        test_row6 = tk.Frame(left, bg="#F4F6F8")
        test_row6.pack(anchor="w", pady=(8, 0))
        ttk.Button(test_row6, text="Query Sensors", command=self.query_sensors).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(
            left,
            text="Slow scan (10x)",
            variable=self.slow_scan_var,
        ).pack(anchor="w", pady=(8, 0))

        # Chart area
        chart_frame = tk.LabelFrame(
            right, text="Sensor Bar Chart (Up to 32 channels)", padx=8, pady=8
        )
        chart_frame.pack(fill=tk.BOTH, expand=True)
        self.chart = BarChart(chart_frame, max_bars=32, bg="white", height=220)
        self.chart.pack(fill=tk.BOTH, expand=True)

        # Status table
        table_frame = tk.LabelFrame(right, text="Test Status", padx=8, pady=8)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        self.table = ttk.Treeview(
            table_frame, columns=STATUS_COLUMNS, show="headings", height=10
        )
        for col in STATUS_COLUMNS:
            self.table.heading(col, text=col)
            width = 110 if col != "Sensor" else 90
            self.table.column(col, width=width, anchor="center")
        self.table.pack(fill=tk.BOTH, expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_item_change(self):
        item = self.selected_item.get()
        if not item or item not in self.items:
            self.heads_var.set("Heads: -")
            self.per_head_var.set("Sensors per head: -")
            self.heads = 0
            self.per_head = 0
            self._load_table(0, 0)
            self.chart.set_values([])
            return

        heads, per_head = self.items[item]
        self.heads = heads
        self.per_head = per_head
        self.heads_var.set(f"Heads: {heads}")
        self.per_head_var.set(f"Sensors per head: {per_head}")
        self.total_sensors = heads * per_head
        self._load_table(heads, per_head)
        self.chart.set_values([0] * min(self.total_sensors, 32))
        _, labels, idod_flags = self._reorder_by_type(
            [0] * self.total_sensors, self.total_sensors
        )
        self.chart.set_labels(labels, idod_flags)

    def _load_table(self, heads, per_head):
        for row in self.table.get_children():
            self.table.delete(row)

        if heads <= 0 or per_head <= 0:
            return

        for h in range(1, heads + 1):
            for s in range(1, per_head + 1):
                sensor_label = f"H{h}-S{s}"
                row = [sensor_label] + ["PENDING"] * (len(STATUS_COLUMNS) - 1)
                self.table.insert("", "end", values=row)

    def refresh_ports(self):
        ports = list_serial_ports()
        self.port_var.set(ports[0] if ports else "")
        self.port_combo["values"] = ports

    def toggle_connect(self):
        if self.reader:
            self.reader.close()
            self.reader = None
            self.connect_btn.configure(text="Connect")
            self.conn_status_var.set("Serial: disconnected")
            return

        port = self.port_var.get().strip()
        if not port:
            self.conn_status_var.set("Serial: no port selected")
            return

        try:
            self.reader = SerialReader(port)
        except Exception:
            self.reader = None
            self.conn_status_var.set("Serial: failed to connect")
            return

        self.connect_btn.configure(text="Disconnect")
        self.conn_status_var.set(f"Serial: connected to {port}")
        self.after(POLL_MS, self.poll_serial)

    def poll_serial(self):
        if not self.reader:
            return
        data, sensor_count = self.reader.read_latest()
        if sensor_count is not None:
            self.sensor_count_var.set(f"Detected sensors: {sensor_count}")
        if data:
            self._apply_sensor_data(data)
        self.after(POLL_MS, self.poll_serial)

    def _apply_sensor_data(self, values):
        total = self.total_sensors if self.total_sensors > 0 else len(values)
        if self.total_sensors > 0:
            reordered, labels, idod_flags = self._reorder_by_type(
                values, self.total_sensors
            )
            self.chart.set_values(reordered[: min(self.total_sensors, 32)])
            self.chart.set_labels(labels, idod_flags)
        else:
            self.chart.set_values(values[: min(total, 32)])
            self.chart.set_labels([], [])

        timestamp = time.strftime("%H:%M:%S")
        self.last_update_var.set(f"Last update: {timestamp} ({len(values)} ch)")

        if total > 0:
            rows = self.table.get_children()
            for i, row_id in enumerate(rows):
                if i >= total:
                    break
                row_vals = list(self.table.item(row_id, "values"))
                if row_vals:
                    row_vals[1] = "OK"
                    self.table.item(row_id, values=row_vals)

    def _reorder_by_type(self, values, total):
        if self.total_sensors <= 0:
            return values, [], []
        heads = self.heads
        per_head = self.per_head
        if heads <= 0 or per_head <= 0:
            return values, [], []

        vals = list(values)[: total]
        reordered = []
        labels = []
        idod_flags = []

        # HALL first (first 3 per head), then IDOD (4th per head)
        for h in range(1, heads + 1):
            base = (h - 1) * per_head
            for s in range(1, min(per_head, 3) + 1):
                idx = base + (s - 1)
                if idx < len(vals):
                    reordered.append(vals[idx])
                    labels.append(f"H{h}-H{s}")
                    idod_flags.append(False)
        for h in range(1, heads + 1):
            base = (h - 1) * per_head
            if per_head >= 4:
                idx = base + 3
                if idx < len(vals):
                    reordered.append(vals[idx])
                    labels.append(f"H{h}-I")
                    idod_flags.append(True)

        return reordered, labels, idod_flags

    def on_close(self):
        if self.reader:
            self.reader.close()
            self.reader = None
        self.destroy()

    def send_command(self, cmd):
        if not self.reader:
            self.conn_status_var.set("Serial: not connected")
            return False
        try:
            self.reader.ser.write((cmd.strip() + "\n").encode())
            return True
        except Exception:
            self.conn_status_var.set("Serial: write failed")
            return False

    def start_read(self):
        if self.send_command("READ"):
            self.conn_status_var.set("Serial: READ sent")

    def start_scan(self):
        if self.slow_scan_var.get():
            if not self.send_command("SCANSPEED=SLOW"):
                return
        else:
            if not self.send_command("SCANSPEED=FAST"):
                return
        if not self.send_command("HOME"):
            return
        self.conn_status_var.set("Serial: HOME sent")
        if self.send_command("SCAN"):
            self.conn_status_var.set("Serial: HOME + SCAN sent")

    def stop_motion(self):
        if self.send_command("STOP"):
            self.conn_status_var.set("Serial: STOP sent")

    def query_sensors(self):
        if self.send_command("NUMSENS"):
            self.conn_status_var.set("Serial: NUMSENS sent")

    def _set_status_all(self, col_name, value):
        try:
            col_index = STATUS_COLUMNS.index(col_name)
        except ValueError:
            return
        for row_id in self.table.get_children():
            row_vals = list(self.table.item(row_id, "values"))
            if len(row_vals) > col_index:
                row_vals[col_index] = value
                self.table.item(row_id, values=row_vals)

    def test_comms(self):
        self._set_status_all("Comms", "RUN")
        self.after(300, lambda: self._set_status_all("Comms", "OK"))

    def test_hall(self):
        self._set_status_all("Hall range", "RUN")
        if self.include_sync_sequence.get():
            self._set_status_all("Synced error", "RUN")
            self._set_status_all("Sequence error", "RUN")
        self.after(400, lambda: self._set_status_all("Hall range", "OK"))
        if self.include_sync_sequence.get():
            self.after(400, lambda: self._set_status_all("Synced error", "OK"))
            self.after(400, lambda: self._set_status_all("Sequence error", "OK"))

    def test_idod(self):
        self._set_status_all("IDOD", "RUN")
        self.after(400, lambda: self._set_status_all("IDOD", "OK"))

    def test_null_center(self):
        self._set_status_all("Null center", "RUN")
        self.after(400, lambda: self._set_status_all("Null center", "OK"))

    def test_noise(self):
        self._set_status_all("Noise", "RUN")
        self.after(400, lambda: self._set_status_all("Noise", "OK"))

    def test_synced(self):
        self._set_status_all("Synced error", "RUN")
        self.after(400, lambda: self._set_status_all("Synced error", "OK"))

    def test_sequence(self):
        self._set_status_all("Sequence error", "RUN")
        self.after(400, lambda: self._set_status_all("Sequence error", "OK"))


def main():
    app = MEAPDemoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
