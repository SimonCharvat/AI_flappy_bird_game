# Flappy Bird with NEAT

This repository contains a simple Flappy Bird game made using Python's `tkinter` GUI and the [NEAT](https://neat-python.readthedocs.io/en/latest/) (NeuroEvolution of Augmenting Topologies) package. 

## Features

- **AI-Powered Gameplay**: The NEAT algorithm controls the bird's movements and learns over time how to improve its performance in the game.
- **Dynamic Scaling**: Game logic is computed using abstract measurements and projected onto a `tkinter` canvas. This enables dynamic resizing of the game window without affecting the trained model at the cost of not being pixel-perfect.

## How It Works

1. **Game Logic**: 
   - The game computes logic using abstract scale, ensuring compatibility regardless of the canvas size.
   - All elements (bird, pipes, etc.) are dynamically scaled to fit the current window size.

2. **AI Training**:
   - The NEAT algorithm evolves the bird's neural network over generations, optimizing its ability to navigate through the pipes.
   - Each bird's fitness is determined based on its performance in avoiding obstacles and staying alive longer.

## Libraries Used

- **Core Libraries**:
  - `os`
  - `tkinter`
  - `math` (`ceil`, `sqrt`)
  - `random` (`uniform`)
  - `numpy`
- **Third-Party Libraries**:
  - `PIL` (`Image`, `ImageTk`)
  - `neat`

