import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from source.common_utilities.log_manager import log_manager


class LoggingTab:

    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="Logs")
        self.output_box = scrolledtext.ScrolledText(
            self.tab,
            width=120,
            height=40
        )
        self.output_box.pack(fill="both", expand=True)
        self.output_box.config(state="disabled")
        self.poll_logs()

    def poll_logs(self):
        while True:
            msg = log_manager.get_log()
            if msg is None:
                break
            self.output_box.config(state="normal")
            self.output_box.insert("end", msg + "\n")
            self.output_box.see("end")
            self.output_box.config(state="disabled")
        self.tab.after(100, self.poll_logs)