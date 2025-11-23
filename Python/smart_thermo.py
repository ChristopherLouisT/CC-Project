from tkinter import *
from PIL import Image, ImageTk
import ctypes
import os
import threading

class SmartThermometer:

    def __init__(self, root):
        self.root = root

        # Load local font
        self.load_font("./font/DS-DIGI.TTF")

        # Canvas setup
        WIDTH, HEIGHT = 400, 260
        self.canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Background
        self.rounded_rect(10, 10, WIDTH-10, HEIGHT-10, radius=30,
                          fill="white", outline="black", width=2)

        # Icons
        thermo_img = Image.open("./img/thermostat.png").resize((60, 60))
        self.thermo_icon = ImageTk.PhotoImage(thermo_img)

        drop_img = Image.open("./img/droplet.png").resize((60, 60))
        self.drop_icon = ImageTk.PhotoImage(drop_img)

        self.canvas.create_image(60, 80, image=self.thermo_icon)
        self.canvas.create_image(60, 160, image=self.drop_icon)

        # Digital displays
        self.temp_text = self.canvas.create_text(220, 80, text="28.6",
                                font=("DS-Digital", 70), fill="#ff0000")

        self.canvas.create_text(330, 80, text="°C",
                                font=("Arial", 20), fill="#ff0000")

        self.humid_text = self.canvas.create_text(220, 160, text="54.7",
                                font=("DS-Digital", 70), fill="#ff0000")

        self.canvas.create_text(340, 160, text="%",
                                font=("Arial", 20), fill="#ff0000")

        # Blink
        self.blink_state = True
        self.blink()

        # Start console listener in background thread
        threading.Thread(target=self.listen_console, daemon=True).start()


    # Load custom font
    def load_font(self, path):
        FR_PRIVATE  = 0x10
        path = os.path.abspath(path)
        ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)

    # Rounded rectangle drawer
    def rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius,
            x2, y2, x2-radius, y2,
            x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    # Blink temp & humidity
    def blink(self):
        self.blink_state = not self.blink_state

        self.canvas.itemconfigure(self.temp_text, fill="#ff0000" if self.blink_state else "")
        self.canvas.itemconfigure(self.humid_text, fill="#ff0000" if self.blink_state else "")

        delay = 500 if self.blink_state else 120
        self.root.after(delay, self.blink)

    # Console listener (runs in background)
    def listen_console(self):
        while True:
            try:
                print("\nType: temp humidity  (example: 30.2 65)")
                raw = input(">>> ")

                parts = raw.split()
                if len(parts) != 2:
                    print("Invalid format.")
                    continue

                temp, humid = parts

                # Update UI from thread
                self.root.after(0, lambda: self.canvas.itemconfigure(self.temp_text, text=temp))
                self.root.after(0, lambda: self.canvas.itemconfigure(self.humid_text, text=humid))

            except Exception as e:
                print("Error:", e)


root = Tk()
root.title("Digital Temp & Humidity Display")

SmartThermometer(root)

root.mainloop()
