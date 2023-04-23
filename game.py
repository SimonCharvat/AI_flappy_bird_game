import os
import tkinter as tk
from PIL import Image, ImageTk
from math import ceil, sqrt
from random import uniform
import neat
import numpy as np


class App():
    
    def __init__(self):
        
        self.game_exists = False

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

        # label showing current score of top 3 birds
        self.label_score = tk.Label(self.root, text="aaaaaaaa")
        self.label_score.pack()

        # blank canvas widget
        self.canvas = tk.Canvas(background=self.COLOR_BACKGROUND)
        self.canvas.config(width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canvas.pack()

        # update root in order to fully create widgets before using them
        self.root.update()

        
        #sleep(1)

        #self.start_engine_loop()

    def start_engine_loop(self):
        self.button_start["state"] = "disabled"
        self.engine_loop()
        self.low_frequency_loop()

    def jump_first_bird_instance(self):
        self.game.bird_instances[0].jump()

    def engine_loop(self):
        self.game.check_for_collisions()
        self.game.physics_update_all_birds()
        self.game.physics_move_all_pillars()
        self.game.order_pillars()
        self.game.make_AI_decision()
        self.game.remove_dead_birds()
        self.root.after(self.TIME_ENGINE_INTERVAL_MS, self.engine_loop)
    
    def low_frequency_loop(self):
        if self.game_exists:
            self.game.update_score_label()
        time_interval = int(self.TIME_ENGINE_INTERVAL_MS / 3)
        self.root.after(time_interval, self.low_frequency_loop)

    def draw_loop(self):
        self.game.graphics_update_all_birds()
        self.game.graphics_update_all_pillars()
        self.root.after(self.TIME_DRAW_INTERVAL_MS, self.draw_loop)

    def start_flappy_bird(self, genomes, config):
        self.game = Game(self.canvas, self.TIME_ENGINE_INTERVAL_MS, genomes, config, self.label_score)
        self.start_engine_loop()
        self.game_exists = True
        #self.game.create_bird_instance()



class Game():
    
    def __init__(self, canvas, ENGINE_INTERVAL_MS, genomes, config, label_score_widget = None):
        
        
        self.bird_instances = []
        self.network_instances = []
        self.genome_instances = []

        self.label_score_widget = label_score_widget
        
        self.pillar_instances = []

        self.scroll_speed_per_sec = 0.2
        self.scroll_speed_per_tick = self.scroll_speed_per_sec / (1000 / ENGINE_INTERVAL_MS)
        
        self.ENGINE_INTERVAL_MS = ENGINE_INTERVAL_MS
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        
        self.bird_size_px = 40 # pixels

        self.pillar_width = 90 # pixels
        self.pillar_distance_px = 3 * self.pillar_width
        self.pillar_distance_rel = self.pillar_distance_px / self.canvas_width
        self.number_of_pillars = 1 + ceil(self.canvas_width / (self.pillar_distance_px + self.pillar_width))
        self.pillar_gap_size = 0.25 # vertical distance between pillars (as coeficient between 0 and 1)
        
        self.images = {
            "bird": ImageTk.PhotoImage(Image.open("bird.png").resize((self.bird_size_px, self.bird_size_px), Image.Resampling.LANCZOS)),
            "pillar_body_bottom": ImageTk.PhotoImage(Image.open("pillar_body.png").resize((self.pillar_width, round(self.canvas_height / 2)), Image.Resampling.LANCZOS)),
            "pillar_body_top": ImageTk.PhotoImage(Image.open("pillar_body.png").resize((self.pillar_width, round(self.canvas_height / 2)), Image.Resampling.LANCZOS).rotate(180)),
            "pillar_head_bottom": ImageTk.PhotoImage(Image.open("pillar_head.png").resize((self.pillar_width, self.pillar_width), Image.Resampling.LANCZOS)),
            "pillar_head_top": ImageTk.PhotoImage(Image.open("pillar_head.png").resize((self.pillar_width, self.pillar_width), Image.Resampling.LANCZOS).rotate(180))
        }

        for i in range(self.number_of_pillars):
            self.create_pillar_instance(i)
            self.pillar_instances[i].update_active_pillar_status()
        

        for i, (genome_id, genome) in enumerate(genomes):
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.network_instances.append(net)
            self.genome_instances.append(genome)
            self.create_bird_instance()
        
    
    def update_score_label(self):
        if self.label_score_widget != None:
            scores = []
            for bird in self.bird_instances:
                scores.append(bird.score)
            
            top_scores = np.array(sorted(scores, reverse=True)[:min(3, len(scores))])
            top_scores = np.round(top_scores, 3)
            self.label_score_widget.config(text = f"{top_scores}")
            #self.label_score_widget.pack()

    def make_AI_decision(self):
        active_pillar_index = None
        for i, pillar in enumerate(self.pillar_instances):
            if pillar.active_pillar:
                active_pillar_index = i
                break
        
        if active_pillar_index == None:
            raise ValueError("No active pillar!")
        
        top_pillar_inner_y = self.pillar_instances[active_pillar_index].top_head_inner_y
        bot_pillar_inner_y = self.pillar_instances[active_pillar_index].bottom_head_inner_y

        for i in range(len(self.bird_instances)):
            
            bird_y = self.bird_instances[i].bird_y
            top_distance = abs(top_pillar_inner_y - bird_y)
            bot_distance = abs(bot_pillar_inner_y - bird_y)
            
            neuron_output = self.network_instances[i].activate([bird_y, top_distance, bot_distance])[0]
            
            if neuron_output > 0.5:
                self.bird_instances[i].jump()

    def create_bird_instance(self):
        self.bird_instances.append(Bird(self.canvas_width, self.canvas_height, self.ENGINE_INTERVAL_MS, self.images["bird"], self.bird_size_px))

    def create_pillar_instance(self, pillar_rank):
        self.pillar_instances.append(Pillar(self.images["pillar_head_top"],
                                            self.images["pillar_head_bottom"],
                                            self.images["pillar_body_bottom"],
                                            self.images["pillar_body_top"],
                                            self.canvas,
                                            self.pillar_width,
                                            self.images["pillar_body_top"].height(),
                                            self.pillar_gap_size,
                                            pillar_rank,
                                            self.pillar_distance_rel))

    def physics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.physics_update()
            instance.increse_bird_score(0.01)
    
    def physics_move_all_pillars(self):
        for pillar_instance in self.pillar_instances:
            pillar_instance.center_position[0] -= self.scroll_speed_per_tick
            #print(pillar_instance.center_position)
    
    def graphics_update_all_birds(self):
        for instance in self.bird_instances:
            instance.graphics_update(self.canvas)

    def graphics_update_all_pillars(self):
        for instance in self.pillar_instances:
            instance.allign_by_center_position()

    def check_for_collisions(self):
        for bird_instance in self.bird_instances:
            # Check for collision with ground (bottom)
            if bird_instance.bird_y - bird_instance.bird_diameter_rel <= 0:
                bird_instance.death(self.canvas, "ground")
            # Check for collision with sky (top)
            if bird_instance.bird_y + bird_instance.bird_diameter_rel >= 1:
                bird_instance.death(self.canvas, "ground")
            # Check for collision with pillars
            for pillar_instance in self.pillar_instances:
                if pillar_instance.check_for_bird_collision(bird_instance.bird_y, bird_instance.bird_diameter_rel): # returns bool
                    bird_instance.death(self.canvas, "pillar")
    
    def remove_dead_birds(self):
        to_be_removed = []
        for i, bird in enumerate(self.bird_instances):
            if not bird.alive:
                to_be_removed.append(i)
        
        if len(to_be_removed) > 0:
            for i, index in enumerate(to_be_removed):
                self.bird_instances.pop(index - i)
                self.network_instances.pop(index - i)
                self.genome_instances.pop(index - i)

                
        
    def order_pillars(self):
        for pillar_instance in self.pillar_instances:
            if pillar_instance.center_position[0] + pillar_instance.pillar_dimensions[0] < 0:
                print("Pillar out of bounds - moved to the end")
                pillar_instance.center_position[0] = self.pillar_instances[-1].center_position[0] + self.pillar_distance_rel
                pillar_instance.randomize_height()
                
                self.pillar_instances.append(self.pillar_instances.pop(0))
                self.add_score_to_birds()
                break
    
    def add_score_to_birds(self):
        for bird in self.bird_instances:
            if bird.alive:
                bird.score += 1


class Pillar():
    def __init__(self, image_head_top, image_head_bottom, image_body_bottom, image_body_top, canvas, pillar_width, pillar_body_height, gap_size, x_pos_rank, pillar_x_distance):
        
        self.pillar_x_distance = pillar_x_distance

        self.pillar_body_height_px = pillar_body_height
        self.pillar_body_height_rel = self.pillar_body_height_px / canvas.winfo_height()
        
        self.pillar_head_size_px = pillar_width
        self.pillar_head_size_rel = self.pillar_head_size_px / canvas.winfo_height()

        # If this pipe is the closest to the bird (middle of screen)
        self.active_pillar = False

        self.canvas = canvas
        
        # creating canvas objects to get IDs, but are placed out of screen
        self.canvas_id_bottom_head = canvas.create_image(-10*pillar_width, 0, anchor="n",image=image_head_bottom)
        self.canvas_id_bottom_body = canvas.create_image(-10*pillar_width, 0, anchor="n",image=image_body_bottom)
        self.canvas_id_top_head = canvas.create_image(-10*pillar_width, 0, anchor="s",image=image_head_top)
        self.canvas_id_top_body = canvas.create_image(-10*pillar_width, 0, anchor="s",image=image_body_top)

        self.bottom_head_inner_y = None
        self.top_head_inner_y = None

        self.gap_size = gap_size # vertical distance between pillars (as coeficient between 0 and 1)
        
        self.pillar_dimensions = [self.pillar_head_size_rel,
                                  self.pillar_body_height_rel + self.pillar_head_size_rel]
        
        self.center_position = [1 + x_pos_rank * pillar_x_distance, None]
        self.randomize_height()
        self.allign_by_center_position()

        

    def allign_by_center_position(self):
        _canvas_width = self.canvas.winfo_width()
        _canvas_height = self.canvas.winfo_height()
        
        # Calculating the inner y-coordinate (hitbox) as value between 0 and 1 (0 = bottom side, 1 = top side)
        self.bottom_head_inner_y = self.center_position[1] - self.gap_size / 2
        self.top_head_inner_y = self.center_position[1] + self.gap_size / 2

        #print((self.bottom_head_inner_y, self.top_head_inner_y))
        #print((self.bottom_head_inner_y * _canvas_height, self.top_head_inner_y * _canvas_height))

        #print((_canvas_width, _canvas_height))

        # top pillar
        self.canvas.moveto(self.canvas_id_top_head,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.top_head_inner_y * _canvas_height - self.pillar_head_size_px)

        self.canvas.moveto(self.canvas_id_top_body,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.top_head_inner_y * _canvas_height - self.pillar_head_size_px - self.pillar_body_height_px)
        
        # bottom pillar
        self.canvas.moveto(self.canvas_id_bottom_head,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.bottom_head_inner_y * _canvas_height)

        self.canvas.moveto(self.canvas_id_bottom_body,
                            self.center_position[0] * _canvas_width - self.pillar_head_size_px / 2,
                            _canvas_height - self.bottom_head_inner_y * _canvas_height + self.pillar_head_size_px)
    
    def randomize_height(self):
        self.center_position[1] = uniform(0.2, 0.8)
    
    def update_active_pillar_status(self):
        if self.center_position[0] > (0.5 - self.pillar_head_size_rel) and self.center_position[0] <= (0.5 + self.pillar_x_distance + self.pillar_head_size_rel):
            self.active_pillar = True
        else:
            self.active_pillar = False

    def check_for_bird_collision(self, bird_y, bird_diameter):     
        # 0.5 = middle of screen
        # TODO: bird left and right could be calculated only once for all pillars (pass it as argument of this function)

        # calculating top left corner position of top pillar head
        top_pillar_pos = [self.center_position[0] - self.pillar_dimensions[0] / 2,
                          self.top_head_inner_y + self.pillar_dimensions[1]]
        
        # calculating top left corner position of bottom pillar head
        bot_pillar_pos = [self.center_position[0] - self.pillar_dimensions[0] / 2,
                          self.bottom_head_inner_y]


        bird_left_x = 0.5 - bird_diameter
        bird_right_x = 0.5 + bird_diameter
        
        pillar_left_x = self.center_position[0] - self.pillar_head_size_rel / 2
        pillar_right_x = self.center_position[0] + self.pillar_head_size_rel / 2

        # if it is even possible to collide on x-axis - optimalizead as it does not have to check collision with every bird
        if bird_right_x >= pillar_left_x and bird_left_x <= pillar_right_x:
            
            if bird_y < self.bottom_head_inner_y: # check bottom body pillar collision
                print("bottom")
                return True
            if bird_y > self.top_head_inner_y: # check bottom body pillar collision
                print("top")
                return True
            
            top_rectangle_collision = check_collision_circle_rectangle([0.5, bird_y], bird_diameter / 2, top_pillar_pos, self.pillar_dimensions)
            bot_rectangle_collision = check_collision_circle_rectangle([0.5, bird_y], bird_diameter / 2, bot_pillar_pos, self.pillar_dimensions)
            
            if (top_rectangle_collision or bot_rectangle_collision):
                return True
        
        else: # if bird is completely outside of pillars hitbox
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

        self.alive = True

    def death(self, canvas, reason = "unknown"):
        self.alive = False
        self.score -= 1
        print(f"Bird {self.canvas_id} died - reason: {reason}")
        canvas.delete(self.canvas_id)

    def jump(self):
        if self.can_jump:
            self.can_jump = False
            self.updates_since_last_jump = 0
            self.velocity = self.jump_velocity

    def increse_bird_score(self, increment):
        self.score += increment
    
    def physics_update(self):
        self.velocity -= self.gravity * (self.engine_interval_ms / 1000)
        self.velocity = max(self.velocity, self.max_falling_speed)
        
        self.bird_y += self.velocity
        self.updates_since_last_jump += 1
        
        #print(f"Bird {self.canvas_id}: ({round(self.bird_x, 4)}, {round(self.bird_y, 4)}), velocity: {round(self.velocity, 4)}")

        # Make jump avaliable again if enough time passed
        if not self.can_jump:
            if self.updates_since_last_jump > self.updates_between_jumps:
                #print("Jump avaliable")
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



def check_collision_circle_rectangle(circle_center, circle_radius, rectangle_top_left, rectangle_dim):
    """
    Check for collision between a circle and a rectangle in 2D space.

    Arguments:
    circle_center: list
        X,Y-coordinates of the circle center [x, y]
    circle_radius: float
        Radius of the circle
    rectangle_top_left: list
        X,Y-coordinates of the rectangle top-left corner [x, y]
    rectangle_dim: list
        Dimensions of rectangle [widht, height]

    Returns:
        bool: True if the circle and rectangle collide, False otherwise
    """

    # Find the closest point to the circle within the rectangle
    closest_x = max(rectangle_top_left[0], min(circle_center[0], rectangle_top_left[0] + rectangle_dim[0]))
    closest_y = max(rectangle_top_left[1], min(circle_center[1], rectangle_top_left[1] + rectangle_dim[1]))

    # Calculate the distance between the closest point and the circle's center
    distance = sqrt((closest_x - circle_center[0]) ** 2 + (closest_y - circle_center[1]) ** 2)

    # If the distance is less than the circle's radius, they collide
    if distance < circle_radius:
        return True
    else:
        return False



def run_neat():
    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)

    p = neat.Population(config)

    # In case I want to restart from checkpoint
    #p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-1")

    p.add_reporter(neat.StdOutReporter(True))
    stast = neat.StatisticsReporter()
    p.add_reporter(stast)
    p.add_reporter(neat.Checkpointer(generation_interval=1)) # after how many generations is checkpoint created

    # Returns best genome after 'n' generations or when fitness hits treshold (default 400?)
    winner = p.run(eval_genomes, n=50)


def eval_genomes(genomes, config):
    app = App()
    app.start_flappy_bird(genomes, config)

    #app.engine_loop()
    app.draw_loop()

    app.root.mainloop()


if __name__ == "__main__":
    
    run_neat()
    #app = App()
    #app.start_flappy_bird()

    #app.engine_loop()
    #app.draw_loop()

    #app.root.mainloop()
