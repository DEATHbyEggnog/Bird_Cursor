import os
import tkinter as tk
from PIL import Image, ImageTk
import math

class BirdTrackerApp:
    def __init__(self, master, directory, nest_image_path):
        self.master = master
        self.directory = directory
        self.bird_frames = self.load_bird_frames()
        self.label = tk.Label(master, bg="black", bd=0, relief='flat')
        self.label.pack()
        self.target_position = (0, 0)
        self.current_position = (0, 0)
        self.follow_speed = 0.05  # Adjust the following speed
        self.hover_distance = 10  # Adjust the distance above the cursor
        self.in_idle_state = False  # Initialize the variable
        self.nest_image = Image.open(nest_image_path).convert("RGBA")
        self.nest_image = self.nest_image.resize((self.nest_image.width // 4, self.nest_image.height // 4))
        self.last_cursor_position = (0, 0)  # Variable to store the last cursor position
        self.idle_timer = 0  # Variable to store the idle time
        self.update_image()

    def enter_idle_state(self):
        self.in_idle_state = True
    
        # Set the target position to the top right corner
        nest_x = self.master.winfo_screenwidth() - self.nest_image.width
        nest_y = 0
        self.target_position = (nest_x, nest_y)
    
    def load_bird_frames(self):
        bird_frames = []
        for i in range(1, 21):
            image_path = os.path.join(self.directory, f"bird{i}.png")
            bird_frame = Image.open(image_path).convert("RGBA")
            bird_frame = bird_frame.resize((bird_frame.width // 16, bird_frame.height // 16))
            bird_frames.append(bird_frame)
        return bird_frames

    def check_idle_state(self):
        # Check if the cursor position has changed
        current_cursor_position = (self.master.winfo_pointerx(), self.master.winfo_pointery())
        if current_cursor_position != self.last_cursor_position:
            # Cursor moved, reset the idle timer
            self.idle_timer = 0
        else:
            # Cursor idle, increment the idle timer
            self.idle_timer += 100  # Increment by the update interval (100 milliseconds)
            if self.idle_timer >= 8000:  # Check if idle for 8 seconds
                self.enter_idle_state()  # Enter idle state
        # Update the last cursor position
        self.last_cursor_position = current_cursor_position
        # Call the check_idle_state method after 100 milliseconds
        self.master.after(100, self.check_idle_state)

    def update_image(self):
        x, y = self.master.winfo_pointerxy()

        # Gradually move towards the cursor position both horizontally and vertically
        self.current_position = (
            (1 - self.follow_speed) * self.current_position[0] + self.follow_speed * x,
            (1 - self.follow_speed) * self.current_position[1] + self.follow_speed * y
        )

        # Calculate the smoother sine wave motion
        sine_offset = math.sin(self.current_position[0] / 100) * 50
        sine_offset_smoothed = math.sin(self.current_position[0] / 50) * 20

        bird_y = self.current_position[1] - self.hover_distance + sine_offset_smoothed

        # Calculate the index based on the x-coordinate
        index = self.calculate_index()

        bird_frame = self.bird_frames[index]

        # Adjust the inversion for photos 1-20 when going west (left)
        if self.current_position[0] > x:
            bird_frame = bird_frame.transpose(Image.FLIP_LEFT_RIGHT)

        photo = ImageTk.PhotoImage(bird_frame)
        self.label.config(image=photo)
        self.label.image = photo

        self.master.geometry(f"{bird_frame.width}x{bird_frame.height}+{int(self.current_position[0])}+{int(bird_y)}")

        # If in idle state, check if the idle timer has reached 8 seconds
        if self.in_idle_state and self.idle_timer >= 8000:
            # Move towards the target position when in idle state
            self.current_position = (
                (1 - self.follow_speed) * self.current_position[0] + self.follow_speed * self.target_position[0],
                (1 - self.follow_speed) * self.current_position[1] + self.follow_speed * self.target_position[1]
            )

            bird_frame = self.bird_frames[0]  # You may want to use a specific frame for the idle state
            photo = ImageTk.PhotoImage(bird_frame)
            self.label.config(image=photo)
            self.label.image = photo

            self.master.geometry(f"{bird_frame.width}x{bird_frame.height}+{int(self.current_position[0])}+{int(self.current_position[1])}")

            # Check if the bird has reached the target position
            if abs(self.current_position[0] - self.target_position[0]) > 5 or abs(self.current_position[1] - self.target_position[1]) > 5:
                # Continue updating frames if not reached
                self.master.after(100, self.update_image)
            else:
                self.in_idle_state = False  # Exit idle state once the bird reaches the target
        else:
            # Continue updating frames if not in idle state
            self.master.after(100, self.update_image)

    def calculate_index(self):
        screen_width = self.master.winfo_screenwidth()
        direction_multiplier = 1 if self.current_position[0] < screen_width / 2 else -1
        index = (int(self.current_position[0]) // (screen_width // len(self.bird_frames))) % len(self.bird_frames)
        return index if direction_multiplier == 1 else len(self.bird_frames) - index - 1


def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.wm_attributes('-transparentcolor', 'black')
    root.attributes("-topmost", True)

    # Specify the path to your nest image
    nest_image_path = r"C:\Users\100615979\Downloads\Screen buddy\Screen buddy\bird buddy\tree_nest.png"

    # Specify the path to your bird images directory
    bird_directory = r"C:\Users\100615979\Downloads\Screen buddy\Screen buddy\bird buddy"

    bird_tracker_app = BirdTrackerApp(root, bird_directory, nest_image_path)

    # Call the check_idle_state method after 100 milliseconds
    root.after(100, bird_tracker_app.check_idle_state)

    root.mainloop()

if __name__ == "__main__":
    main()
