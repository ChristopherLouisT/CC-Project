import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json

class AnimatedMapPin:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle GPS Simulation")

        # ======================================================
        # CANVAS + BACKGROUND
        # ======================================================
        self.canvas = tk.Canvas(root, width=900, height=600, bg='lightgray')
        self.canvas.pack()

        # Load initial image
        img = Image.open("./Python/img/map1.jpeg").resize((900, 600), Image.LANCZOS)
        self.map_image = ImageTk.PhotoImage(img)
        self.map_bg = self.canvas.create_image(0, 0, anchor='nw', image=self.map_image)

        self.canvas.bind("<Button-1>", self.get_click_position)

        # ======================================================
        # ROUTES WITH GPS DATA
        # ======================================================
        self.routes = {
            "Route 1": {
                "points": [
                    (133, 230), (122, 310), (140, 314),
                    (129, 377), (309, 403), (313, 390),
                    (396, 403), (406, 419), (632, 449), (672, 407),
                ],
                "gps": [
                    ("38°53'01\" N", "77°00'23\" W"),
                    ("38°53'10\" N", "77°00'18\" W"),
                    ("38°53'20\" N", "77°00'10\" W"),
                    ("38°53'40\" N", "77°00'03\" W"),
                    ("38°53'55\" N", "76°59'55\" W"),
                    ("38°54'10\" N", "76°59'40\" W"),
                    ("38°54'25\" N", "76°59'20\" W"),
                    ("38°54'33\" N", "76°59'12\" W"),
                    ("38°54'40\" N", "76°59'05\" W"),
                    ("38°54'50\" N", "76°59'00\" W"),
                ],
                "image": "./Python/img/map1.jpeg"
            },

            "Route 2": {
                "points": [
                    (505, 543), (325, 390), (358, 148),
                    (477, 147), (484, 110),
                ],
                "gps": [
                    ("40°00'00\" N", "74°30'00\" W"),
                    ("40°00'20\" N", "74°29'45\" W"),
                    ("40°00'40\" N", "74°29'10\" W"),
                    ("40°01'00\" N", "74°28'40\" W"),
                    ("40°01'10\" N", "74°28'20\" W"),
                ],
                "image": "./Python/img/map2.jpeg"
            },

            "Route 3": {
                "points": [
                    (259, 561), (240, 540), (268, 520),
                    (111, 397), (390, 269), (479, 257),
                    (578, 231), (687, 166), (613, 124)
                ],
                "gps": [
                    ("22°40'10\" N", "55°00'10\" E"),
                    ("22°40'25\" N", "55°00'20\" E"),
                    ("22°40'40\" N", "55°00'35\" E"),
                    ("22°40'55\" N", "55°00'50\" E"),
                    ("22°41'10\" N", "55°01'05\" E"),
                    ("22°41'25\" N", "55°01'20\" E"),
                    ("22°41'40\" N", "55°01'35\" E"),
                    ("22°41'55\" N", "55°01'50\" E"),
                    ("22°42'10\" N", "55°02'05\" E"),
                ],
                "image": "./Python/img/map3.jpeg"
            },
        }

        # DEFAULT ROUTE
        self.current_route = "Route 1"
        self.path_points = self.routes[self.current_route]["points"]
        self.gps_points = self.routes[self.current_route]["gps"]

        # Draw initial path
        self.path_line = self.canvas.create_line(self.path_points, fill='blue', width=3)

        # ======================================================
        # PIN (vehicle)
        # ======================================================
        self.pin = self.canvas.create_polygon(0, 0, -10, -20, 10, -20,
                                              fill='red', outline='black')

        # Animation vars
        self.current_index = 0
        self.progress = 0
        self.speed = 0.02
        self.animating = False
        self.last_gps_index = -1

        # ======================================================
        # UI Controls
        # ======================================================
        controls = tk.Frame(root)
        controls.pack(pady=10)

        self.route_var = tk.StringVar(value=self.current_route)

        route_dropdown = ttk.Combobox(
            controls,
            textvariable=self.route_var,
            values=list(self.routes.keys()),
            width=25,
            state="readonly"
        )
        route_dropdown.pack(side=tk.LEFT, padx=5)
        route_dropdown.bind("<<ComboboxSelected>>", self.change_route)

        self.play_btn = tk.Button(controls, text="Play", command=self.toggle_animation)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(controls, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)

        # PIN START POSITION
        self.move_pin_to(self.path_points[0])

        # Create GPS panel
        self.create_info_panel()
        self.canvas.bind("<Configure>", self.position_info_panel)

        # Initialize GPS values
        self.update_gps_labels(0)

    # ==========================================================
    #   GPS PANEL
    # ==========================================================
    def create_info_panel(self):
        self.info_panel = tk.Frame(self.canvas, bg="#3c3c3c", padx=10, pady=10)
        self.info_window = self.canvas.create_window(20, 480, anchor="nw", window=self.info_panel)

        tk.Label(self.info_panel, text="Vehicle GPS", fg="white",
                 bg="#3c3c3c", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.lbl_name = tk.Label(self.info_panel, text="Name: M 1972 AD", fg="white", bg="#3c3c3c")
        self.lbl_battery = tk.Label(self.info_panel, text="Battery: 100%", fg="white", bg="#3c3c3c")
        self.lbl_long = tk.Label(self.info_panel, text="Longitude:", fg="white", bg="#3c3c3c")
        self.lbl_lat = tk.Label(self.info_panel, text="Latitude:", fg="white", bg="#3c3c3c")

        self.lbl_name.pack(anchor="w")
        self.lbl_battery.pack(anchor="w")
        self.lbl_long.pack(anchor="w")
        self.lbl_lat.pack(anchor="w")

    def position_info_panel(self, event=None):
        self.canvas.coords(self.info_window, 20, self.canvas.winfo_height() - 150)

    # Update GPS text
    def update_gps_labels(self, index):
        lon, lat = self.gps_points[index]
        self.lbl_long.config(text=f"Longitude: {lon}")
        self.lbl_lat.config(text=f"Latitude:  {lat}")

    # ==========================================================
    #   ROUTE SWITCHING
    # ==========================================================
    def change_route(self, event=None):
        chosen = self.route_var.get()
        route = self.routes[chosen]
        self.current_route = chosen

        self.path_points = route["points"]
        self.gps_points = route["gps"]

        # Load background
        img = Image.open(route["image"]).resize((900, 600), Image.LANCZOS)
        self.map_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.map_bg, image=self.map_image)

        # Refresh line
        self.canvas.delete(self.path_line)
        self.path_line = self.canvas.create_line(self.path_points, fill="blue", width=3)

        # Reset everything
        self.reset()

        # Update GPS at starting position
        self.update_gps_labels(0)

    # ==========================================================
    #   MOVEMENT + ANIMATION
    # ==========================================================
    def move_pin_to(self, position):
        x, y = position
        self.canvas.coords(self.pin, x, y, x - 10, y - 20, x + 10, y - 20)

    def animate(self):
        if not self.animating:
            return
        
        # Update GPS normally
        gps_index = min(self.current_index, len(self.gps_points) - 1)

        # Only print JSON when the GPS index changes
        if gps_index != self.last_gps_index:
            print(self.get_current_gps_json())
            self.last_gps_index = gps_index

        self.update_gps_labels(gps_index)

        # If animation finished, show final GPS point
        if self.current_index >= len(self.path_points) - 1:
            final_x, final_y = self.path_points[-1]
            self.move_pin_to((final_x, final_y))
            self.update_gps_labels(len(self.gps_points) - 1)
            self.animating = False
            self.play_btn.config(text="Play")
            return

        start = self.path_points[self.current_index]
        end = self.path_points[self.current_index + 1]

        x = start[0] + (end[0] - start[0]) * self.progress
        y = start[1] + (end[1] - start[1]) * self.progress

        self.move_pin_to((x, y))

        self.progress += self.speed

        if self.progress >= 1:
            self.progress = 0
            self.current_index += 1

        self.root.after(20, self.animate)

    # ==========================================================
    #   PLAY / PAUSE / RESET
    # ==========================================================
    def toggle_animation(self):
        self.animating = not self.animating
        self.play_btn.config(text="Pause" if self.animating else "Play")

        if self.animating:
            self.animate()

    def reset(self):
        self.animating = False
        self.current_index = 0
        self.progress = 0
        self.play_btn.config(text="Play")

        self.move_pin_to(self.path_points[0])
        self.update_gps_labels(0)

    # ==========================================================
    #   DEBUG
    # ==========================================================
    def get_click_position(self, event):
        print(f"Clicked at: ({event.x}, {event.y})")

    def get_current_gps_json(self):
        gps_index = min(self.current_index, len(self.gps_points) - 1)
        lon, lat = self.gps_points[gps_index]
        
        gps_data = {
            "longitude": lon,
            "latitude": lat
        }
        
        return json.dumps(gps_data, indent=4)

# ==============================================================
# RUN APP
# ==============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AnimatedMapPin(root)
    root.mainloop()
