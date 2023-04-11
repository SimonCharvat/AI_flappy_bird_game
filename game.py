
import tkinter as tk
from PIL import Image, ImageTk
from math import ceil
#import neat


class App():
    
    def __init__(self):

        self.ROOT_WIDTH = 800
        self.ROOT_HEIGHT = 700

        self.CANVAS_WIDTH = 600
        self.CANVAS_HEIGHT = 500

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
        self.game.check_for_collisions()
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
        self.pillar_instances = []
        
        self.ENGINE_INTERVAL_MS = ENGINE_INTERVAL_MS
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        
        self.bird_size_px = 40 # pixels

        self.pillar_width = 90 # pixels
        self.pillar_distance = 3 * self.pillar_width
        self.number_of_pillars = 1 + ceil(self.canvas_width / (self.pillar_distance + self.pillar_width))
        self.pillar_gap_size = 0.2 # vertical distance between pillars (as coeficient between 0 and 1)
        
        self.images = {
            "bird": ImageTk.PhotoImage(Image.open("bird.png").resize((self.bird_size_px, self.bird_size_px), Image.Resampling.LANCZOS)),
            "pillar_body_bottom": ImageTk.PhotoImage(Image.open("pillar_body.png").resize((self.pillar_width, round(self.canvas_height / 2)), Image.Resampling.LANCZOS)),
            "pillar_body_top": ImageTk.PhotoImage(Image.open("pillar_body.png").resize((self.pillar_width, round(self.canvas_height / 2)), Image.Resampling.LANCZOS).rotate(180)),
            "pillar_head_bottom": ImageTk.PhotoImage(Image.open("pillar_head.png").resize((self.pillar_width, self.pillar_width), Image.Resampling.LANCZOS)),
            "pillar_head_top": ImageTk.PhotoImage(Image.open("pillar_head.png").resize((self.pillar_width, self.pillar_width), Image.Resampling.LANCZOS).rotate(180))
        }

        for i in range(self.number_of_pillars):
            self.create_pillar_instance()
        
    def create_bird_instance(self):
        self.bird_instances.append(Bird(self.canvas_width, self.canvas_height, self.ENGINE_INTERVAL_MS, self.images["bird"], self.bird_size_px))

    def create_pillar_instance(self):
        self.pillar_instances.append(Pillar(self.images["pillar_head_top"],
                                            self.images["pillar_head_bottom"],
                                            self.images["pillar_body_bottom"],
                                            self.images["pillar_body_top"],
                                            self.canvas,
                                            self.pillar_width,
                                            self.images["pillar_body_top"].height(),
                                            self.pillar_gap_size))

    def physics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.physics_update()
    
    def graphics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.graphics_update(self.canvas)

    def check_for_collisions(self):
        for bird_instance in self.bird_instances:
            # Check for collision with ground (bottom)
            if bird_instance.bird_y - bird_instance.bird_diameter_rel <= 0:
                print("Bird hit the ground")
                bird_instance.death()
            # Check fir collision with pillars
            for pillar_instance in self.pillar_instances:
                if pillar_instance.check_for_bird_collision(bird_instance.bird_y, bird_instance.bird_diameter_rel): # returns bool
                    bird_instance.death()


class Pillar():
    def __init__(self, image_head_top, image_head_bottom, image_body_bottom, image_body_top, canvas, pillar_width, pillar_body_height, gap_size):
        
        self.pillar_body_height = pillar_body_height
        self.pillar_head_size_px = pillar_width
        self.pillar_head_size_rel = self.pillar_head_size_px / canvas.winfo_height()

        self.canvas = canvas
        
        # creating canvas objects to get IDs, but are placed out of screen
        self.canvas_id_bottom_head = canvas.create_image(-10*pillar_width, 0, anchor="n",image=image_head_bottom)
        self.canvas_id_bottom_body = canvas.create_image(-10*pillar_width, 0, anchor="n",image=image_body_bottom)
        self.canvas_id_top_head = canvas.create_image(-10*pillar_width, 0, anchor="s",image=image_head_top)
        self.canvas_id_top_body = canvas.create_image(-10*pillar_width, 0, anchor="s",image=image_body_top)

        self.bottom_head_inner_y = None
        self.top_head_inner_y = None

        self.gap_size = gap_size # vertical distance between pillars (as coeficient between 0 and 1)
        
        
        # TODO delete, for debugging only
        self.center_position = [0.8, 0.7]
        self.allign_by_center_position()

        

    def allign_by_center_position(self):
        _canvas_width = self.canvas.winfo_width()
        _canvas_height = self.canvas.winfo_height()
        
        # Calculating the inner y-coordinate (hitbox) as value between 0 and 1 (0 = bottom side, 1 = top side)
        self.bottom_head_inner_y = self.center_position[1] - self.gap_size / 2
        self.top_head_inner_y = self.center_position[1] + self.gap_size / 2

        print((self.bottom_head_inner_y, self.top_head_inner_y))
        print((self.bottom_head_inner_y * _canvas_height, self.top_head_inner_y * _canvas_height))

        print((_canvas_width, _canvas_height))

        # top pillar
        self.canvas.moveto(self.canvas_id_top_head,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.top_head_inner_y * _canvas_height - self.pillar_head_size_px)

        self.canvas.moveto(self.canvas_id_top_body,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.top_head_inner_y * _canvas_height - self.pillar_head_size_px - self.pillar_body_height)
        
        # bottom pillar
        self.canvas.moveto(self.canvas_id_bottom_head,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.bottom_head_inner_y * _canvas_height)

        self.canvas.moveto(self.canvas_id_bottom_body,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.bottom_head_inner_y * _canvas_height + self.pillar_head_size_px)
        
    def check_for_bird_collision(self, bird_y, bird_diameter):     
        # 0.5 = middle of screen
        # TODO: bird left and right could be calculated only once for all pillars (pass it as argument of this function)
        pillar_left_x = self.center_position[0] - self.pillar_head_size_rel / 2
        pillar_right_x = self.center_position[0] + self.pillar_head_size_rel / 2
        bird_left_x = 0.5 - bird_diameter
        bird_right_x = 0.5 + bird_diameter
        
        # if it is even possible to collide on x-axis - optimalizead as it does not have to check collision with every bird
        if bird_right_x >= pillar_left_x or bird_left_x <= pillar_right_x:
            # if bird fully inside pillar -> only check y-axis collision
            if bird_left_x >= pillar_left_x and bird_right_x <= pillar_right_x:
                print("fully between pillars")
                # top side collision check
                if bird_y + bird_diameter >= self.top_head_inner_y:
                    print("Pillar - top hit")
                    return True
                # bottom side collision check
                if bird_y - bird_diameter <= self.bottom_head_inner_y:
                    print("Pillar - bottom hit")
                    return True
            else: # if can collide, but must check distance between objects on both axis TODO
                pass
        else:
            return False
        
        #raise ValueError("Collision detection failed - no return")
        
        #print(f"Collision detected with pillar {(self.canvas_id_bottom_head, self.canvas_id_top_head)}")
        
        
            



class Bird():
    def __init__(self, canvas_width, canvas_height, ENGINE_INTERVAL_MS, bird_image, bird_size_px):
        
        # Constants
        self.engine_interval_ms = ENGINE_INTERVAL_MS
        self.updates_between_jumps = 1000 * 0.2 / ENGINE_INTERVAL_MS # 1/(time between updates in sec) * 0.2 = jump each 0.2 second
        self.bird_x = 0.5
        self.bird_image = bird_image

        self.bird_width_px = bird_size_px
        self.bird_width_rel = bird_size_px / canvas_height # relative (as coeficient between 0 and 1)
        self.bird_diameter_rel = self.bird_width_rel / 2

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
        
        self.bird_y = 0.7

    def death(self):
        print(f"Bird {self.canvas_id} had died!")

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
        
        #print(f"Bird {self.canvas_id}: ({round(self.bird_x, 4)}, {round(self.bird_y, 4)}), velocity: {round(self.velocity, 4)}")

        # Make jump avaliable again if enough time passed
        if not self.can_jump:
            if self.updates_since_last_jump > self.updates_between_jumps:
                print("Jump avaliable")
                self.can_jump = True
    
    
    def graphics_update(self, canvas):
        if self.canvas_id == None:
            self.canvas_id = canvas.create_image(self.canvas_width - self.bird_x * self.canvas_width - self.bird_width_px / 2,
                                                 self.canvas_height - self.bird_y * self.canvas_height - self.bird_width_px / 2,
                                                 anchor="center",
                                                 image=self.bird_image)
        canvas.moveto(self.canvas_id,
                      self.canvas_width - self.bird_x * self.canvas_width - self.bird_width_px / 2,
                      self.canvas_height - self.bird_y * self.canvas_height - self.bird_width_px / 2)


def get_distance_between_circle_rectangle(object1, object2):
    """
    Arguments:
    object1, object2: list
        list with 2D coordinates [x, y]
    Returns:
        distance between 2 objects
    """
    
    return ((object1[0] - object2[0]) ** 2 + (object1[1] - object2[1]) ** 2) ** (0.5)


if __name__ == "__main__":
    app = App()
    app.start_flappy_bird()

    #app.engine_loop()
    app.draw_loop()

    app.root.mainloop()
