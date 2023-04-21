
import neat
import os


class AI():

    def __init__(self):
        pass




def run_AI():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
    
    run_neat(config)


def eval_genomes(genomes, config):
    pass


def run_neat(config):
    
    p = neat.Population(config)

    # In case I want to restart from checkpoint
    #p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-1")

    p.add_reporter(neat.StdOutReporter(True))
    stast = neat.StatisticsReporter()
    p.add_reporter(stast)
    p.add_reporter(neat.Checkpointer(generation_interval=1)) # after how many generations is checkpoint created

    # Returns best genome after 'n' generations or when fitness hits treshold (default 400?)
    winner = p.run(eval_genomes, n=50)





if __name__ == "__main__":
    app = game.App()
    app.start_flappy_bird()

    #app.engine_loop()
    app.draw_loop()

    app.root.mainloop()