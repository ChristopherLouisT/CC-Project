import threading
import sys
from tkinter import *
from tkinter import ttk

class FeetToMeters:

    def __init__(self, root):
        root.title("Feet to Meters")

        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.feet = StringVar()
        self.meters = StringVar()

        ttk.Entry(mainframe, width=7, textvariable=self.feet).grid(column=2, row=1)
        ttk.Label(mainframe, textvariable=self.meters).grid(column=2, row=2)
        ttk.Label(mainframe, text="feet").grid(column=3, row=1)
        ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2)
        ttk.Label(mainframe, text="meters").grid(column=3, row=2)
        ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3)

        # Start console listener in a background thread
        threading.Thread(target=self.console_listener, daemon=True).start()

    def calculate(self):
        try:
            value = float(self.feet.get())
            self.meters.set(round(value * 0.3048, 4))
        except ValueError:
            self.meters.set("ERR")

    def console_listener(self):
        while True:
            text = input("Enter feet value: ")
            try:
                value = float(text)
                # update GUI safely
                self.feet.set(text)
                self.meters.set(round(value * 0.3048, 4))
            except ValueError:
                print("Invalid input")

root = Tk()
FeetToMeters(root)
root.mainloop()
