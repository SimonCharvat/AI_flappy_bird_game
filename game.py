
import tkinter as tk
import time
from PIL import Image, ImageTk
#import neat


class App():
    
    def __init__(self):

        self.ROOT_WIDTH = 1000
        self.ROOT_HEIGHT = 800

        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 600

        self.COLOR_BACKGROUND = "#000000"  # Black
        self.COLOR_GRID = "#999999"  # Grey
        self.COLOR_SNAKE_BODY = "#077309"  # Dark green
        self.COLOR_APPLE = "#c20000"  # Dark red

        self.TIME_DRAW_INTERVAL_MS = 17 # 17 ms ~ 60 fps
        self.TIME_ENGINE_INTERVAL_MS = 17

        # tkinter app root window
        self.root = tk.Tk()
        self.root.title("Flappy bird AI")
        self.root.resizable(False, False)
        self.root.geometry(f"{self.ROOT_WIDTH}x{self.ROOT_HEIGHT}")

        # button to start game
        self.button_start = tk.Button(self.root, text="Start", command=self.start_engine_loop)
        self.button_start.pack()

        # button to jump - controlls first instance of bird - for debugging purpouses
        self.button_jump = tk.Button(self.root, text="Jump", command=self.jump_first_bird_instance)
        self.button_jump.pack()

        # blank canvas widget
        self.canvas = tk.Canvas(background=self.COLOR_BACKGROUND)
        self.canvas.config(width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canvas.pack()

        # update root in order to fully create widgets before using them
        self.root.update()

    def start_engine_loop(self):
        self.button_start["state"] = "disabled"
        self.engine_loop()

    def jump_first_bird_instance(self):
        self.game.bird_instances[0].jump()

    def engine_loop(self):
        self.root.after(self.TIME_ENGINE_INTERVAL_MS, self.engine_loop)
        self.game.physics_update_all_birds()

    def draw_loop(self):
        self.game.graphics_update_all_birds()
        self.root.after(self.TIME_DRAW_INTERVAL_MS, self.draw_loop)

    def start_flappy_bird(self):
        self.game = Game(self.canvas, self.TIME_ENGINE_INTERVAL_MS)
        self.game.create_bird_instance()



class Game():
    
    def __init__(self, canvas, ENGINE_INTERVAL_MS):
        self.bird_instances = []
        self.ENGINE_INTERVAL_MS = ENGINE_INTERVAL_MS
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        self.bird_size = round(self.canvas_height * 0.07)

        self.images = {
            "bird": ImageTk.PhotoImage(Image.open("bird.png").resize((self.bird_size, self.bird_size), Image.ANTIALIAS))
        }
        
    def create_bird_instance(self):
        self.bird_instances.append(Bird(self.canvas_width, self.canvas_height, self.ENGINE_INTERVAL_MS, self.images["bird"]))

    def physics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.physics_update()
    
    def graphics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.graphics_update(self.canvas)



class Bird():
        
    def __init__(self, canvas_width, canvas_height, ENGINE_INTERVAL_MS, bird_image):
        
        # Constants
        self.engine_interval_ms = ENGINE_INTERVAL_MS
        self.updates_between_jumps = 1000 * 0.2 / ENGINE_INTERVAL_MS # 1/(time between updates in sec) * 0.2 = jump each 0.2 second
        self.bird_size = 5 # diameter
        self.bird_x = 0.5
        self.bird_image = bird_image

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.gravity = 0.1
        self.jump_velocity = 0.03 # added vertical acceleration when jump initiated
        self.velocity = 0 # vertical velocity of bird
        self.max_falling_speed = -0.03
        
        # Variables - assigned default values
        self.opaque = False # if bird should be displayed partialy opaque

        self.canvas_id = None
        self.updates_since_last_jump = 0
        self.score = 0
        self.can_jump = True
        
        self.bird_y = 0.5


    def jump(self):
        if self.can_jump:
            print("Jump")
            self.can_jump = False
            self.updates_since_last_jump = 0
            self.velocity = self.jump_velocity
        else:
            print("Can't jump")

    
    def physics_update(self):
        self.velocity -= self.gravity * (self.engine_interval_ms / 1000)
        self.velocity = max(self.velocity, self.max_falling_speed)
        
        self.bird_y += self.velocity
        self.updates_since_last_jump += 1
        
        print(f"Bird {self.canvas_id}: ({round(self.bird_x, 4)}, {round(self.bird_y, 4)}), velocity: {round(self.velocity, 4)}")

        # Make jump avaliable again if enough time passed
        if not self.can_jump:
            if self.updates_since_last_jump > self.updates_between_jumps:
                print("Jump avaliable")
                self.can_jump = True
    
    
    def graphics_update(self, canvas):
        if self.canvas_id == None:
            self.canvas_id = canvas.create_image(self.canvas_width - self.bird_x * self.canvas_width,
                                                 self.canvas_height - self.bird_y * self.canvas_height,
                                                 anchor="center",
                                                 image=self.bird_image)
        canvas.moveto(self.canvas_id,
                      self.canvas_width - self.bird_x * self.canvas_width,
                      self.canvas_height - self.bird_y * self.canvas_height)



if __name__ == "__main__":
    app = App()
    app.start_flappy_bird()

    #app.engine_loop()
    app.draw_loop()

    app.root.mainloop()
