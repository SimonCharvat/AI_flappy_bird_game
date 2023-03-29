import tkinter as tk



ROOT_WIDTH = 1000
ROOT_HEIGHT = 600

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 500


COLOR_BACKGROUND = "#000000"  # Black
COLOR_GRID = "#999999"  # Grey
COLOR_SNAKE_BODY = "#077309"  # Dark green
COLOR_APPLE = "#c20000"  # Dark red

TIME_DRAW_INTERVAL_MS = 10
TIME_ENGINE_INTERVAL_MS = 500



root = tk.Tk()
root.title("Snake")
root.resizable(False, False)
root.geometry(f"{ROOT_WIDTH}x{ROOT_HEIGHT}")



canvas = tk.Canvas(background=COLOR_BACKGROUND)
canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack()

def engine_loop():
    root.after(TIME_ENGINE_INTERVAL_MS, engine_loop)

def draw_loop():
    canvas.pack()
    root.after(TIME_DRAW_INTERVAL_MS, draw_loop)


if __name__ == "__main__":
    engine_loop()
    draw_loop()

    root.mainloop()
