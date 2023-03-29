import tkinter as tk


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




if __name__ == "__main__":
    app = App()

    app.engine_loop()
    app.draw_loop()

    app.root.mainloop()
