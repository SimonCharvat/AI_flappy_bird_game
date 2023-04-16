import game
import neat










if __name__ == "__main__":
    app = game.App()
    app.start_flappy_bird()

    #app.engine_loop()
    app.draw_loop()

    app.root.mainloop()