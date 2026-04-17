# Minesweeper Bot

An intelligent Minesweeper bot implemented in Python using Depth-First Search (DFS) for constraint satisfaction and probability-based decision making.

## Features

- **DFS-Based Solver**: Uses constraint propagation and DFS to find all valid mine configurations for frontier cells.
- **Probability Estimation**: Calculates safe/mine probabilities for each cell based on valid models.
- **Smart Guessing**: Compares frontier probabilities with outside cells to make optimal guesses.
- **GUI Interface**: Interactive Tkinter-based Minesweeper game with bot controls.
- **Benchmarking**: Automated performance testing across different difficulty levels.
- **Simulation Mode**: Headless simulation for testing and analysis.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/monoz2509k/minesweeper-bot.git
   cd minesweeper-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode
Run the interactive GUI:
```bash
python main.py
```
- Click cells to play manually
- Use "One step Auto-Play" for single bot moves
- Use "Fully Auto-Play" for complete automation

### Simulation Mode
Run headless simulations:
```bash
python simulation.py
```

### Benchmarking
Run performance benchmarks:
```bash
python run_benchmark.py
```
Results are saved to `BENCHMARK_RESULTS.md` and `win_rates_chart.png`.

## Project Structure

- `bot_dfs.py`: DFS agent implementation
- `game_gui.py`: Tkinter GUI interface
- `simulation.py`: Headless game logic and simulation
- `run_benchmark.py`: Benchmarking script
- `main.py`: Entry point for GUI
- `requirements.txt`: Python dependencies

## Algorithm Overview

The bot uses a constraint satisfaction approach:

1. **Frontier Detection**: Identifies unrevealed cells adjacent to revealed numbers.
2. **Component Splitting**: Groups frontier cells into connected components.
3. **DFS Exploration**: Finds all valid mine assignments for each component.
4. **Probability Calculation**: Computes safe/mine probabilities from valid models.
5. **Decision Making**: Chooses the safest move, preferring outside cells when beneficial.

## Benchmark Results

See `BENCHMARK_RESULTS.md` for detailed performance metrics across different difficulty levels.

## License

MIT License
