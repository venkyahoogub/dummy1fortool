import tkinter as tk

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, msg):
        self.widget.insert(tk.END, msg)
        self.widget.see(tk.END)

    def flush(self):
        pass