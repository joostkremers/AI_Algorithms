import math
import tkinter as tk


class DataPoint:
    # The data_string parameter is a string holding the digit, 0s, and 1s
    # in the format '6: 011110110000100000111111110001110001010001001111'
    def __init__(self, data_string):
        # Initialize the name and os and 1s.
        fields = data_string.split(" ")
        self.name = fields[0][0]
        self.zeros_and_ones = fields[1].strip()

        # Add the 0s and 1s to a list of ints.
        self.properties = []
        for ch in self.zeros_and_ones:
            self.properties.append(int(ch))

    # Calculate the distance from this point to the other point.
    def distance(self, other): ...

    # Use K nearest neighbors to set the data point's name.
    def knn(self, data_points, k):
        # Sort the data points by distance this one.
        sorted_data_points = sorted(data_points, key=lambda other: self.distance(other))

        # Count the first k votes.
        votes = {}
        num_votes = 0
        for point in sorted_data_points:
            # Add 1 to this name's vote count.
            if point.name in votes:
                votes[point.name] += 1
            else:
                votes[point.name] = 1

            # Count up to k votes.
            num_votes += 1
            if num_votes >= k:
                break

        # See which name had the most votes.
        self.name = max(votes, key=lambda name: votes[name])


# The main App class.

# Geometry constants.
NUM_ROWS = 8
NUM_COLS = 6
CELL_WID = 20
CELL_HGT = CELL_WID
MARGIN = 5
WINDOW_WID = NUM_COLS * CELL_WID + 100
WINDOW_HGT = NUM_ROWS * CELL_HGT + 40


class App:
    # Create and manage the tkinter interface.
    def __init__(self):
        self.network = None

        # Make the main interface.
        self.window = tk.Tk()
        self.window.title("knn_digits")
        self.window.protocol("WM_DELETE_WINDOW", self.kill_callback)
        self.window.geometry(f"{WINDOW_WID}x{WINDOW_HGT}")

        # Build the rest of the UI.
        self.build_ui()

        # Load the data.
        self.load_data()

        # Test K values between 3 and 20.
        self.test_ks(3, 20)

        # Test one more time with the best K to display the result.
        self.test_data(self.k)
        print(f"Final K: {self.k}\n")

        # Initially we have nothing to draw.
        self.polyline = None
        self.points = []

        # Display the window.
        self.window.focus_force()
        self.window.mainloop()

    # Build the tkinter user interface.
    def build_ui(self):
        # Make the drawing canvas.
        canvas_wid = NUM_COLS * CELL_WID + 1
        canvas_hgt = NUM_ROWS * CELL_HGT + 1
        self.canvas = tk.Canvas(
            self.window,
            bg="white",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.SUNKEN,
            width=canvas_wid,
            height=canvas_hgt,
        )
        self.canvas.place(x=MARGIN, y=MARGIN)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Make grid lines.
        for r in range(NUM_ROWS + 1):
            self.canvas.create_line(
                0, r * CELL_HGT, canvas_wid, r * CELL_HGT, fill="lime"
            )
        for c in range(NUM_COLS + 1):
            self.canvas.create_line(
                c * CELL_WID, 0, c * CELL_WID, canvas_hgt, fill="lime"
            )

        # Make a label to display success percentage.
        self.success_rate_value = tk.StringVar()
        self.success_rate_label = tk.Label(
            self.window,
            font=("Calibri 10 normal"),
            textvariable=self.success_rate_value,
        )
        self.success_rate_label.place(x=MARGIN, y=canvas_hgt + 2 * MARGIN)

        # Make a big label to display results from the user drawing.
        self.user_result_value = tk.StringVar()
        self.user_result_label = tk.Label(
            self.window,
            font=("Calibri 100 normal"),
            textvariable=self.user_result_value,
        )
        self.user_result_label.place(x=canvas_wid + 2 * MARGIN, y=MARGIN)

    # Load the data points.
    def load_data(self):
        with open("digit_data.txt", "r") as f:
            lines = f.readlines()
            self.data_points = []
            for line in lines:
                self.data_points.append(DataPoint(line))

    # Test different values for K.
    def test_ks(self, min_k, max_k): ...

    # Test each of the data points with this value for K.
    # Return the success rate.
    def test_data(self, k): ...

    # The user has moved the mouse while drawing.
    # Remove the existing polyline and draw a new one.
    def redraw(self):
        # Remove old polyline.
        self.canvas.delete(self.polyline)
        self.polyline = None

        # Draw current points.
        if len(self.points) > 1:
            self.polyline = self.canvas.create_line(self.points, fill="black")

    # The user has pressed the mouse down over the canvas.
    # Start drawing.
    def start_draw(self, event):
        # Remove any previous drawing.
        self.points = []
        self.redraw()

        self.canvas.bind("<B1-Motion>", self.save_point)

    # The user has released the mouse.
    # Finsish drawing.
    def end_draw(self, event):
        self.canvas.unbind("<B1-Motion>")

        # Evaluate the polyline.
        self.evaluate_polyline()

    # The user has moved the mouse while drawing.
    # Save the current mouse position and redraw the polyline.
    def save_point(self, event):
        self.points.append((event.x, event.y))
        self.redraw()

    # Use KNN to see which digit this may be.
    def evaluate_polyline(self):
        # Convert the polyline into a DataPoint.
        data_point = self.polyline_to_data_point()

        # Use KNN to give it a new name.
        data_point.knn(self.data_points, self.k)

        # Display the result.
        self.user_result_value.set(data_point.name)
        print(f"Digit: {data_point.name}")

    # Convert the polyline into a DataPoint.
    def polyline_to_data_point(self):
        # Convert the points into the cells that were touched.
        touched = self.get_touched()

        # Convert the touched cells to a string.
        touched_string = self.touched_to_string(touched)

        # Compose the DataPoint data string.
        data_string = f"?: {touched_string}"

        # Create the DataPoint.
        return DataPoint(data_string)

    # Convert the points in the polyline into the cells that were touched.
    def get_touched(self):
        # Make a touched array holding 0s.
        touched = []
        for r in range(NUM_ROWS):
            touched.append([0 for i in range(NUM_COLS)])

        # Mark the touched cells.
        for point in self.points:
            r = int(point[1] / CELL_HGT)
            c = int(point[0] / CELL_WID)
            if r >= 0 and r < NUM_ROWS and c >= 0 and c < NUM_COLS:
                touched[r][c] = 1

        # Return the touched list.
        return touched

    # Return a string holding the touch values so
    # we can use it to initialize a DataPoint object.
    def touched_to_string(self, touched):
        result = ""
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                result += str(touched[r][c])
        return result

    def kill_callback(self):
        self.window.destroy()


def main():
    App()


if __name__ == "__main__":
    main()
