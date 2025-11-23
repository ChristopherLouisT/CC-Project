from tkinter import *
from PIL import Image, ImageTk, ImageEnhance
import threading

class SmartLamp:
    def __init__(self, root, lamp_image, room_image):
        self.root = root
        self.root.title("Smart Lamp Simulation")

        # Load images
        self.room = Image.open(room_image).convert("RGBA")
        self.lamp = Image.open(lamp_image).convert("RGBA")

        # Resize lamp
        self.lamp = self.lamp.resize((80, 80), Image.LANCZOS)

        # Copies for editing
        self.lamp_original = self.lamp.copy()
        self.room_original = self.room.copy()

        # ---- CREATE CANVAS FIRST ----
        self.canvas = Canvas(root, width=self.room.width, height=self.room.height)
        self.canvas.pack()

        # ---- LOAD IMAGES AFTER CANVAS EXISTS ----
        self.room_tk = ImageTk.PhotoImage(self.room)
        self.room_id = self.canvas.create_image(0, 0, anchor="nw", image=self.room_tk)

        self.lamp_tk = ImageTk.PhotoImage(self.lamp)
        self.lamp_id = self.canvas.create_image(
            self.room.width // 2,
            self.lamp.height // 2,
            image=self.lamp_tk
        )

        # Status text
        self.status_text = self.canvas.create_text(
            10, self.room.height - 90,
            anchor="nw",
            fill="white",
            font=("Arial", 14),
            text="Smart Lamp Simulation\nColor: [255, 255, 255]\nBrightness: 100%"
        )

        # State
        self.color = [255, 255, 255]
        self.brightness = 1.0
        self.on = True

        # Start input thread
        threading.Thread(target=self.console_listener, daemon=True).start()

    # --------------------------------------------------------------------
    def update_lamp(self):

        # Lamp OFF
        if not self.on:
            lamp_img = ImageEnhance.Brightness(self.lamp_original).enhance(0)
            room_img = ImageEnhance.Brightness(self.room_original).enhance(0.25)

        else:
            # Lamp brightness
            lamp_img = ImageEnhance.Brightness(self.lamp_original).enhance(self.brightness)

            # Room brightness follows lamp
            room_img = ImageEnhance.Brightness(self.room_original).enhance(0.4 + self.brightness * 0.6)

            # Tint color (RGB only)
            if self.color != [255, 255, 255]:
                r, g, b = self.color
                room_tint = Image.new("RGBA", room_img.size, (r, g, b, 30))   # 50 alpha = very soft
            else:
                room_tint = Image.new("RGBA", room_img.size, (255, 255, 255, 0))

            room_img = Image.alpha_composite(room_img, room_tint)

        # Convert
        self.lamp_tk = ImageTk.PhotoImage(lamp_img)
        self.room_tk = ImageTk.PhotoImage(room_img)

        # Update canvas
        self.canvas.itemconfig(self.room_id, image=self.room_tk)
        self.canvas.itemconfig(self.lamp_id, image=self.lamp_tk)

        # Update status
        self.canvas.itemconfig(
            self.status_text,
            text=f"Smart Lamp Simulation\nColor: {self.color}\nBrightness: {int(self.brightness*100)}%"
        )

    # --------------------------------------------------------------------
    def console_listener(self):
        while True:
            cmd = input("SmartLamp> ").strip().lower()

            parts = cmd.split()

            # --- brightness ---
            if parts[0] == "brightness" and len(parts) == 2:
                try:
                    value = int(parts[1])
                    self.brightness = max(0, min(1, value / 100))
                    self.update_lamp()
                except:
                    print("Usage: brightness 0-100")

            # --- color ---
            elif parts[0] == "color" and len(parts) == 4:
                try:
                    r, g, b = map(int, parts[1:4])
                    self.color = [r, g, b]
                    self.update_lamp()
                except:
                    print("Usage: color R G B")

            # --- on/off ---
            elif cmd == "on":
                self.on = True
                self.update_lamp()

            elif cmd == "off":
                self.on = False
                self.update_lamp()

            else:
                print("Commands:\n  brightness 0-100\n  color R G B\n  on/off\n")

# RUN APP
root = Tk()
app = SmartLamp(root, lamp_image="./img/lamp.png", room_image="./img/room.jpg")
root.mainloop()
