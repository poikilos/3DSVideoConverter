#!/usr/bin/env python
"""
Show a custom dialog box (with custom inputs, tied to a window).

Thanks to (version with one hard-coded input):
ashwinjv. Correct way to implement a custom popup tkinter dialog box
[Answer]. <https://stackoverflow.com/questions/10057672/
correct-way-to-implement-a-custom-popup-tkinter-dialog-box>
answered Jul 30 '14 at 22:44
ashwinjv
"""
try:
    import Tkinter as tk
    import tkFont
    import ttk
    # import tkMessageBox as messagebox
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
    # from tkinter import messageboximport tkinter


class MyDialog:

    def __init__(self, parent, text, title="info", btnNames=["OK"],
                 args=None, handlers=None):
        """
        Sequential arguments:
        parent -- Set the parent window to block

        Keyword arguments:
        btnNames -- Set the buttons (upon click, self.results will get
                    that value as a key with the value true, but only for
                    the clicked button).
        args -- Set inputs (and optionally defaults) using this
                dict (transferred to self.results dict). If
                it is None, then there will be no entries.
        handlers -- Set the click handlers where the key in this dict
                    matches a name in btnNames.
        """
        top = self.top = tk.Toplevel(parent)
        self.top.winfo_toplevel().title(title)
        self._labels = {}
        self._entries = {}
        self.results = {}
        self.mainL = tk.Label(top, text=text)
        self.mainL.pack()
        self._buttons = {}
        self.results = {}
        if handlers is None:
            handlers = {}
        if args is not None:
            for init_s, v in args.items():
                k = init_s
                if k.startswith("Progressbar "):
                    k = k[12:]
                self._labels[k] = tk.Label(top, text=k)
                self._labels[k].pack()
                self._entries[k] = tk.Entry(top)
                self._entries[k].pack()
        for btnName in btnNames:
            command = handlers.get(btnName)
            if command is None:
                command = self.send
            self._buttons[btnName] = tk.Button(top, text=btnName,
                                               command=self.send)
            self._buttons[btnName].pack()

    def send(self):
        for k, v in self._entries.items():
            self.results[k] = v.get()
        self.top.destroy()
