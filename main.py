### main.py
import tkinter as tk
from game_gui import MinesweeperGUI

def main():
    root = tk.Tk()
    root.title("Minesweeper")
    root.resizable(False, False)
    
    app = MinesweeperGUI(root, rows=9, cols=9, mines=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()