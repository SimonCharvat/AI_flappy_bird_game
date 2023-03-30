
import tkinter as tk
import time


class App():
    
    def __init__(self):

        self.ROOT_WIDTH = 1000
        self.ROOT_HEIGHT = 600

        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 500


        self.COLOR_BACKGROUND = "#000000"  # Black
        self.COLOR_GRID = "#999999"  # Grey
        self.COLOR_SNAKE_BODY = "#077309"  # Dark green
        self.COLOR_APPLE = "#c20000"  # Dark red

        self.TIME_DRAW_INTERVAL_MS = 10
        self.TIME_ENGINE_INTERVAL_MS = 500



        self.root = tk.Tk()
        self.root.title("Flappy bird AI")
        self.root.resizable(False, False)
        self.root.geometry(f"{self.ROOT_WIDTH}x{self.ROOT_HEIGHT}")



        self.canvas = tk.Canvas(background=self.COLOR_BACKGROUND)
        self.canvas.config(width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canvas.pack()

    def engine_loop(self):
        self.root.after(self.TIME_ENGINE_INTERVAL_MS, self.engine_loop)

    def draw_loop(self):
        self.canvas.pack()
        self.root.after(self.TIME_DRAW_INTERVAL_MS, self.draw_loop)



class Game():
    
    def __init__(self, canvas_width, canvas_height):
        self.bird_instances = []
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def create_bird_instance(self):
        self.bird_instances.append(Bird(self.canvas_width, self.canvas_height))


class Bird():
        
    def __init__(self, canvas_width, canvas_height):
        
        # Constants
        self.time_between_jumps_sec = 0.5 # time before jump recharges (in seconds)
        self.bird_size = 5 # diameter
        self.bird_x = canvas_width / 2

        self.gravity = 10
        self.jump_speed = 100 # added vertical velocity when jump initiated
        self.velocity = 0 # vertical velocity of bird
        
        # Variables - assigned default values
        self.opaque = False # if bird should be displayed partialy opaque

        self.last_jump_timestamp = 0
        self.score = 0
        self.can_jump = True
        
        self.bird_y = canvas_height / 2


    def jump(self):
        if self.can_jump:
            print("Jump")
            self.can_jump = False
            self.velocity += self.jump_speed
        else:
            print("Can't jump")

    
    def physics_update(self):
        self.bird_y += self.velocity - self.gravity

        # Make jump avaliable again if enough time passed
        if not self.can_jump:
            if time.time() - self.time_between_jumps_sec > self.last_jump_timestamp:
                print("Jump avaliable")
                self.can_jump = True



if __name__ == "__main__":
    app = App()

    app.engine_loop()
    app.draw_loop()

    app.root.mainloop()
