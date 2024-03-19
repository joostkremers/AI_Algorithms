import math
import tkinter as tk
from tkinter import messagebox
import random
from statistics import mean


# Get the text in an Entry widget and
# convert it to an int.
def get_int(entry):
    return int(entry.get())


# Make Label and Entry widgets for a field.
# Return the Entry widget.
def make_field(parent, label_width, label_text, entry_width, entry_default):
    frame = tk.Frame(parent)
    frame.pack(side=tk.TOP)

    label = tk.Label(frame, text=label_text, width=label_width, anchor=tk.W)
    label.pack(side=tk.LEFT)

    entry = tk.Entry(frame, width=entry_width, justify="right")
    entry.insert(tk.END, entry_default)
    entry.pack(side=tk.LEFT)

    return entry


class DataPoint:
    POINT_RADIUS = 2
    POINT_COLOR = "black"

    def __init__(self, canvas, x, y, radius=POINT_RADIUS, color=POINT_COLOR):
        # Save parameters.
        self.x = x
        self.y = y
        self.radius = radius
        self.canvas = canvas
        self.color = color
        self.seed = None

        # Make the DataPoint's oval. If `canvas`` is None, we have a dummy
        # DataPoint that should not be drawn.
        if self.canvas:
            self.oval = self.canvas.create_oval(
                x - self.radius,
                y - self.radius,
                x + self.radius,
                y + self.radius,
                fill=self.color,
                outline=self.color,
            )

    # Set the DataPoint's color.
    def set_color(self, color):
        self.color = color
        self.canvas.itemconfig(self.oval, fill=self.color, outline=self.color)

    # Return the distance between this point and another one.
    def distance(self, other):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    # Assign this data point to the closest seed.
    def assign_seed(self, seeds):
        self.seed = min(seeds, key=self.distance)
        self.set_color(self.seed.color)

    # Reposition this seed given its currently assigned data points.
    # Return the distance moved.
    def reposition_seed(self, points):
        old_x, old_y = self.x, self.y
        self.x = mean(point.x for point in points)
        self.y = mean(point.y for point in points)
        self.move()
        return self.distance(DataPoint(self.canvas, old_x, old_y))

    # Move the seed's oval to its current location.
    def move(self):
        x = self.x - self.radius
        y = self.y - self.radius
        self.canvas.moveto(self.oval, x, y)


# Geometry constants.
WINDOW_WID = 500
WINDOW_HGT = 300
MARGIN = 5
CANVAS_WID = WINDOW_WID - 200
CANVAS_HGT = WINDOW_HGT - 2 * MARGIN
SEED_RADIUS = 5

# Stop running when the seeds are not moving more than this distance.
STOP_DISTANCE = 1

# Define some seed colors.
colors = [
    "red",
    "lightgreen",
    "blue",
    "pink",
    "green",
    "lightblue",
    "cyan",
    "magenta",
    "yellow",
    "orange",
    "gray",
]


class App:
    # Create and manage the tkinter interface.
    def __init__(self):
        self.running = False
        self.data_points = []
        self.seeds = []

        # Make the main interface.
        self.window = tk.Tk()
        self.window.title("k-means_2d")
        self.window.protocol("WM_DELETE_WINDOW", self.kill_callback)
        self.window.geometry(f"{WINDOW_WID}x{WINDOW_HGT}")

        # Build the rest of the UI.
        self.build_ui()

        # Display the window.
        self.window.focus_force()
        self.window.mainloop()

    def build_ui(self):
        # Drawing canvas.
        self.canvas = tk.Canvas(
            self.window,
            bg="white",
            borderwidth=1,
            highlightthickness=0,
            width=CANVAS_WID,
            height=CANVAS_HGT,
        )
        self.canvas.pack(side=tk.LEFT, padx=MARGIN, pady=MARGIN)
        self.canvas.bind("<Button-1>", self.left_click)

        # Right frame.
        right_frame = tk.Frame(self.window, pady=MARGIN)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Clusters.
        self.num_clusters_entry = make_field(right_frame, 11, "# Clusters:", 5, "2")

        # Delay (ms).
        self.delay_entry = make_field(right_frame, 11, "Delay (ms):", 5, "500")

        # Test data set buttons.
        button_frame = tk.Frame(right_frame, pady=MARGIN)
        button_frame.pack(side=tk.TOP)
        test1_button = tk.Button(
            button_frame, text="Dataset 1", width=8, command=self.load_dataset_1
        )
        test1_button.pack(side=tk.LEFT)
        test2_button = tk.Button(
            button_frame, text="Dataset 2", width=8, command=self.load_dataset_2
        )
        test2_button.pack(side=tk.LEFT, padx=(MARGIN, 0))

        # Test data set buttons.
        button_frame = tk.Frame(right_frame, pady=MARGIN)
        button_frame.pack(side=tk.TOP)
        test3_button = tk.Button(
            button_frame, text="Dataset 3", width=8, command=self.load_dataset_3
        )
        test3_button.pack(side=tk.LEFT)
        test4_button = tk.Button(
            button_frame, text="Dataset 4", width=8, command=self.load_dataset_4
        )
        test4_button.pack(side=tk.LEFT, padx=(MARGIN, 0))

        # Run button.
        self.run_button = tk.Button(
            right_frame, text="Run", width=7, command=self.run, state=tk.DISABLED
        )
        self.run_button.pack(side=tk.TOP, pady=(20, 0))

        # Reset button.
        self.reset_button = tk.Button(
            right_frame, text="Reset", width=7, command=self.reset, state=tk.DISABLED
        )
        self.reset_button.pack(side=tk.TOP, pady=(MARGIN, 0))

        # Clear button.
        self.clear_button = tk.Button(
            right_frame, text="Clear", width=7, command=self.clear, state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.TOP, pady=(MARGIN, 0))

    def left_click(self, event):
        self.data_points.append(DataPoint(self.canvas, event.x, event.y))
        self.set_button_states()

    def set_button_states(self):
        if len(self.data_points) > 0 and not self.running:
            self.reset_button["state"] = tk.NORMAL
            self.clear_button["state"] = tk.NORMAL
        else:
            self.reset_button["state"] = tk.DISABLED
            self.clear_button["state"] = tk.DISABLED

        if len(self.data_points) > 0:
            self.run_button["state"] = tk.NORMAL
        else:
            self.run_button["state"] = tk.DISABLED

    # Stop running.
    def stop_running(self):
        self.running = False
        self.run_button.config(text="Run")
        self.set_button_states()

    # Start running.
    def start_running(self):
        if len(self.data_points) < 1:
            messagebox.showinfo(
                "Data Points Error", "You must define at least one data point."
            )
            return

        # Get parameters.
        num_clusters = get_int(self.num_clusters_entry)
        if num_clusters < 1:
            messagebox.showinfo("seeds Error", "You must create at least one seed.")
            return

        self.running = True
        self.run_button.config(text="Stop")
        self.set_button_states()

        # If we don't already have seeds, make some.
        if len(self.seeds) == 0:
            ...

        # Go!
        print()
        self.num_ticks = 0
        self.tick()

    def run(self):
        # See if we are currently running.
        if self.running:
            self.stop_running()
        else:
            self.start_running()

    # Perform one k-means round.
    # If the maximum distance that any seed moved is
    # less than STOP_DISTANCE, then stop.
    def tick(self):
        self.num_ticks += 1
        print(f"Tick {self.num_ticks}")

        # Assign points to their nearest seeds.
        self.assign_points_to_seeds()

        # Reposition the seeds.
        if self.reposition_seeds() < STOP_DISTANCE:
            # Stop running.
            self.stop_running()

        # If we're still running, schedule another tick.
        if self.running:
            self.window.after(get_int(self.delay_entry), self.tick)

    # Assign points to their nearest seeds.
    def assign_points_to_seeds(self): ...

    # Reposition the seeds.
    # Return the largest distance that any seed moves.
    def reposition_seeds(self): ...

    # Remove the seeds so we can try again with the same points.
    def reset(self):
        # Reset the data points.
        for point in self.data_points:
            point.set_color("black")
            point.seed = None

        # Remove the seeds.
        for seed in self.seeds:
            self.canvas.delete(seed.oval)
        self.seeds = []

        # Reset the button states.
        self.set_button_states()

    # Destroy all seeds, DataPoints, and ovals.
    def clear(self):
        self.canvas.delete("all")
        self.data_points = []
        self.seeds = []
        self.set_button_states()

    def kill_callback(self):
        self.window.destroy()

    def load_dataset_1(self):
        self.stop_running()
        self.canvas.delete("all")
        self.seeds = []
        self.data_points = [
            DataPoint(self.canvas, 62, 80),
            DataPoint(self.canvas, 82, 58),
            DataPoint(self.canvas, 95, 91),
            DataPoint(self.canvas, 111, 54),
            DataPoint(self.canvas, 80, 82),
            DataPoint(self.canvas, 136, 86),
            DataPoint(self.canvas, 121, 108),
            DataPoint(self.canvas, 106, 75),
            DataPoint(self.canvas, 96, 105),
            DataPoint(self.canvas, 67, 124),
            DataPoint(self.canvas, 165, 217),
            DataPoint(self.canvas, 166, 198),
            DataPoint(self.canvas, 193, 219),
            DataPoint(self.canvas, 225, 237),
            DataPoint(self.canvas, 207, 248),
            DataPoint(self.canvas, 171, 260),
            DataPoint(self.canvas, 150, 234),
            DataPoint(self.canvas, 184, 240),
            DataPoint(self.canvas, 184, 264),
            DataPoint(self.canvas, 176, 222),
            DataPoint(self.canvas, 194, 199),
            DataPoint(self.canvas, 212, 216),
            DataPoint(self.canvas, 240, 98),
            DataPoint(self.canvas, 215, 101),
            DataPoint(self.canvas, 220, 129),
            DataPoint(self.canvas, 223, 113),
            DataPoint(self.canvas, 242, 122),
            DataPoint(self.canvas, 253, 113),
            DataPoint(self.canvas, 244, 85),
            DataPoint(self.canvas, 219, 72),
            DataPoint(self.canvas, 235, 144),
            DataPoint(self.canvas, 266, 131),
            DataPoint(self.canvas, 259, 92),
            DataPoint(self.canvas, 205, 119),
            DataPoint(self.canvas, 63, 100),
        ]
        self.set_button_states()

    def load_dataset_2(self):
        self.stop_running()
        self.canvas.delete("all")
        self.seeds = []
        self.data_points = [
            DataPoint(self.canvas, 198, 69),
            DataPoint(self.canvas, 215, 75),
            DataPoint(self.canvas, 213, 99),
            DataPoint(self.canvas, 220, 127),
            DataPoint(self.canvas, 211, 149),
            DataPoint(self.canvas, 63, 192),
            DataPoint(self.canvas, 92, 208),
            DataPoint(self.canvas, 164, 209),
            DataPoint(self.canvas, 91, 68),
            DataPoint(self.canvas, 54, 107),
            DataPoint(self.canvas, 50, 134),
            DataPoint(self.canvas, 136, 59),
            DataPoint(self.canvas, 174, 58),
            DataPoint(self.canvas, 212, 191),
            DataPoint(self.canvas, 202, 170),
            DataPoint(self.canvas, 192, 194),
            DataPoint(self.canvas, 167, 192),
            DataPoint(self.canvas, 143, 192),
            DataPoint(self.canvas, 129, 209),
            DataPoint(self.canvas, 142, 225),
            DataPoint(self.canvas, 101, 228),
            DataPoint(self.canvas, 99, 189),
            DataPoint(self.canvas, 72, 220),
            DataPoint(self.canvas, 45, 181),
            DataPoint(self.canvas, 70, 179),
            DataPoint(self.canvas, 55, 160),
            DataPoint(self.canvas, 36, 160),
            DataPoint(self.canvas, 36, 140),
            DataPoint(self.canvas, 45, 150),
            DataPoint(self.canvas, 42, 113),
            DataPoint(self.canvas, 60, 68),
            DataPoint(self.canvas, 59, 88),
            DataPoint(self.canvas, 99, 56),
            DataPoint(self.canvas, 82, 93),
            DataPoint(self.canvas, 127, 36),
            DataPoint(self.canvas, 151, 53),
            DataPoint(self.canvas, 150, 20),
            DataPoint(self.canvas, 124, 48),
            DataPoint(self.canvas, 200, 48),
            DataPoint(self.canvas, 180, 40),
            DataPoint(self.canvas, 166, 35),
            DataPoint(self.canvas, 224, 96),
            DataPoint(self.canvas, 240, 136),
            DataPoint(self.canvas, 238, 115),
            DataPoint(self.canvas, 230, 114),
            DataPoint(self.canvas, 223, 133),
            DataPoint(self.canvas, 231, 158),
            DataPoint(self.canvas, 216, 177),
            DataPoint(self.canvas, 206, 176),
            DataPoint(self.canvas, 183, 179),
            DataPoint(self.canvas, 195, 212),
            DataPoint(self.canvas, 138, 127),
            DataPoint(self.canvas, 133, 114),
            DataPoint(self.canvas, 155, 114),
            DataPoint(self.canvas, 151, 131),
            DataPoint(self.canvas, 145, 120),
            DataPoint(self.canvas, 142, 142),
            DataPoint(self.canvas, 131, 133),
            DataPoint(self.canvas, 125, 123),
            DataPoint(self.canvas, 124, 144),
        ]
        self.set_button_states()

    def load_dataset_3(self):
        self.stop_running()
        self.canvas.delete("all")
        self.seeds = []
        self.data_points = [
            DataPoint(self.canvas, 100, 87),
            DataPoint(self.canvas, 92, 62),
            DataPoint(self.canvas, 74, 84),
            DataPoint(self.canvas, 123, 75),
            DataPoint(self.canvas, 140, 76),
            DataPoint(self.canvas, 174, 76),
            DataPoint(self.canvas, 202, 77),
            DataPoint(self.canvas, 190, 60),
            DataPoint(self.canvas, 155, 67),
            DataPoint(self.canvas, 189, 83),
            DataPoint(self.canvas, 218, 113),
            DataPoint(self.canvas, 207, 97),
            DataPoint(self.canvas, 233, 85),
            DataPoint(self.canvas, 230, 100),
            DataPoint(self.canvas, 193, 116),
            DataPoint(self.canvas, 187, 128),
            DataPoint(self.canvas, 179, 114),
            DataPoint(self.canvas, 199, 123),
            DataPoint(self.canvas, 173, 142),
            DataPoint(self.canvas, 167, 133),
            DataPoint(self.canvas, 167, 160),
            DataPoint(self.canvas, 156, 161),
            DataPoint(self.canvas, 157, 145),
            DataPoint(self.canvas, 113, 172),
            DataPoint(self.canvas, 135, 153),
            DataPoint(self.canvas, 140, 169),
            DataPoint(self.canvas, 126, 164),
            DataPoint(self.canvas, 90, 188),
            DataPoint(self.canvas, 103, 191),
            DataPoint(self.canvas, 115, 187),
            DataPoint(self.canvas, 129, 195),
            DataPoint(self.canvas, 129, 176),
            DataPoint(self.canvas, 103, 195),
            DataPoint(self.canvas, 86, 221),
            DataPoint(self.canvas, 69, 212),
            DataPoint(self.canvas, 67, 228),
            DataPoint(self.canvas, 83, 238),
            DataPoint(self.canvas, 107, 212),
            DataPoint(self.canvas, 106, 235),
            DataPoint(self.canvas, 139, 259),
            DataPoint(self.canvas, 124, 253),
            DataPoint(self.canvas, 117, 253),
            DataPoint(self.canvas, 125, 240),
            DataPoint(self.canvas, 183, 253),
            DataPoint(self.canvas, 207, 228),
            DataPoint(self.canvas, 207, 231),
            DataPoint(self.canvas, 209, 244),
            DataPoint(self.canvas, 202, 240),
            DataPoint(self.canvas, 199, 256),
            DataPoint(self.canvas, 182, 238),
            DataPoint(self.canvas, 169, 248),
            DataPoint(self.canvas, 147, 241),
            DataPoint(self.canvas, 151, 258),
            DataPoint(self.canvas, 170, 260),
            DataPoint(self.canvas, 64, 130),
            DataPoint(self.canvas, 64, 143),
            DataPoint(self.canvas, 50, 137),
            DataPoint(self.canvas, 51, 123),
            DataPoint(self.canvas, 48, 157),
            DataPoint(self.canvas, 43, 152),
            DataPoint(self.canvas, 59, 152),
            DataPoint(self.canvas, 37, 135),
            DataPoint(self.canvas, 218, 163),
            DataPoint(self.canvas, 220, 169),
            DataPoint(self.canvas, 235, 173),
            DataPoint(self.canvas, 223, 152),
            DataPoint(self.canvas, 248, 152),
            DataPoint(self.canvas, 227, 164),
            DataPoint(self.canvas, 247, 176),
            DataPoint(self.canvas, 239, 155),
            DataPoint(self.canvas, 239, 189),
            DataPoint(self.canvas, 227, 179),
            DataPoint(self.canvas, 211, 180),
            DataPoint(self.canvas, 95, 76),
            DataPoint(self.canvas, 114, 74),
            DataPoint(self.canvas, 114, 74),
            DataPoint(self.canvas, 114, 74),
            DataPoint(self.canvas, 118, 57),
            DataPoint(self.canvas, 145, 57),
        ]
        self.set_button_states()

    def load_dataset_4(self):
        self.stop_running()
        self.canvas.delete("all")
        self.seeds = []
        self.data_points = [
            DataPoint(self.canvas, 139, 31),
            DataPoint(self.canvas, 127, 60),
            DataPoint(self.canvas, 137, 117),
            DataPoint(self.canvas, 137, 160),
            DataPoint(self.canvas, 147, 120),
            DataPoint(self.canvas, 115, 96),
            DataPoint(self.canvas, 141, 90),
            DataPoint(self.canvas, 152, 60),
            DataPoint(self.canvas, 156, 112),
            DataPoint(self.canvas, 123, 74),
            DataPoint(self.canvas, 68, 241),
            DataPoint(self.canvas, 80, 228),
            DataPoint(self.canvas, 115, 249),
            DataPoint(self.canvas, 135, 240),
            DataPoint(self.canvas, 155, 219),
            DataPoint(self.canvas, 169, 242),
            DataPoint(self.canvas, 193, 248),
            DataPoint(self.canvas, 120, 219),
            DataPoint(self.canvas, 155, 255),
            DataPoint(self.canvas, 211, 229),
            DataPoint(self.canvas, 190, 221),
            DataPoint(self.canvas, 245, 232),
        ]
        self.set_button_states()


def main():
    App()


if __name__ == "__main__":
    main()
