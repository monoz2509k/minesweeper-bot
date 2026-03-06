### game_gui.py
import tkinter as tk
import random
from tkinter import messagebox
from bot_dfs import DFSAgent  

class MinesweeperGUI:
    def __init__(self, master, rows=9, cols=9, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        
        self.board = []
        self.mine_positions = set()
        self.flags = set()
        self.revealed = set()
        self.game_over = False
        self.first_click = True
        
        self.agent = DFSAgent(rows, cols)

        self.setup_gui()
        self.place_mines()

    def restart_game(self, new_rows, new_cols, new_mines):
        self.rows = new_rows
        self.cols = new_cols
        self.mines = new_mines
        self.board_frame.destroy()
        
        self.board = []
        self.mine_positions = set()
        self.flags = set()
        self.revealed = set()
        self.game_over = False
        self.first_click = True
        
        self.bot_btn.config(state="normal")
        self.bot_all_btn.config(state="normal")
        
        self.agent = DFSAgent(new_rows, new_cols)
        
        self.create_board()
        self.place_mines()

    def setup_gui(self):
        size_frame = tk.Frame(self.master)
        size_frame.pack(pady=5)
        
        tk.Label(size_frame, text="Size:").pack(side=tk.LEFT)
        
        tk.Button(size_frame, text="🔄 Reset", bg="#ffcccb", font=('Arial', 9, 'bold'),
                  command=lambda: self.restart_game(self.rows, self.cols, self.mines)).pack(side=tk.LEFT, padx=5)

        tk.Button(size_frame, text="5x5 (Easy)", command=lambda: self.restart_game(5, 5, 5)).pack(side=tk.LEFT, padx=2)
        tk.Button(size_frame, text="9x9 (Medium)", command=lambda: self.restart_game(9, 9, 10)).pack(side=tk.LEFT, padx=2)
        tk.Button(size_frame, text="16x16 (Hard)", command=lambda: self.restart_game(16, 16, 40)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(size_frame, text="Custom...", command=self.open_custom_dialog, bg="#ffeb99").pack(side=tk.LEFT, padx=5)

        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=5)
        self.bot_btn = tk.Button(control_frame, text="One step Auto-Play", 
                                 font=('Arial', 10, 'bold'), bg="#d4f1f9", 
                                 command=self.bot_play_step)
        self.bot_btn.pack(side=tk.LEFT, padx=5)
        
        self.bot_all_btn = tk.Button(control_frame, text="Fully Auto-Play", 
                                     font=('Arial', 10, 'bold'), bg="#a8d5ba", 
                                     command=self.bot_play_all)
        self.bot_all_btn.pack(side=tk.LEFT, padx=5)

        self.create_board()

    def open_custom_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Custom")
        dialog.geometry("250x150")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        tk.Label(dialog, text="Rows:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        row_var = tk.IntVar(value=self.rows)
        tk.Entry(dialog, textvariable=row_var, width=8).grid(row=0, column=1)

        tk.Label(dialog, text="Cols:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        col_var = tk.IntVar(value=self.cols)
        tk.Entry(dialog, textvariable=col_var, width=8).grid(row=1, column=1)

        tk.Label(dialog, text="Mines:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        mine_var = tk.IntVar(value=self.mines)
        tk.Entry(dialog, textvariable=mine_var, width=8).grid(row=2, column=1)

        def apply_custom():
            try:
                r = row_var.get()
                c = col_var.get()
                m = mine_var.get()
                
                if r <= 0 or c <= 0 or m <= 0:
                    messagebox.showerror("Error", "Values must be greater than 0!", parent=dialog)
                    return
                if m >= r * c:
                    messagebox.showerror("Error", "Number of mines must be less than total cells!", parent=dialog)
                    return
                if r > 30 or c > 30:
                    messagebox.showwarning("Warning", "Too large size may cause UI lag!", parent=dialog)
                
                self.restart_game(r, c, m)
                dialog.destroy() 
            except tk.TclError:
                messagebox.showerror("Error", "Please enter valid integers!", parent=dialog)

        tk.Button(dialog, text="Confirm", command=apply_custom, font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, pady=10)
    
    def create_board(self):
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(padx=10, pady=10)

        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, font=('Arial', 10, 'bold'))
                btn.bind('<Button-1>', lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind('<Button-3>', lambda e, r=r, c=c: self.right_click(r, c))
                btn.grid(row=r, column=c)
                row_buttons.append(btn)
            self.board.append(row_buttons)

    def place_mines(self):
        self.mine_positions.clear()
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

    def left_click(self, r, c):
        if self.game_over or (r, c) in self.revealed or (r, c) in self.flags: return

        if self.first_click:
            self.first_click = False
            if (r, c) in self.mine_positions:
                self.mine_positions.remove((r, c))
                empty_cells = [(nr, nc) for nr in range(self.rows) for nc in range(self.cols) 
                               if (nr, nc) not in self.mine_positions and (nr, nc) != (r, c)]
                self.mine_positions.add(random.choice(empty_cells))

        self.revealed.add((r, c))
        btn = self.board[r][c]

        if (r, c) in self.mine_positions:
            btn.config(text="💥", bg="#ff4a4a")
            self.end_game(win=False, clicked_mine=(r, c))
            return

        mine_count = sum(1 for nr, nc in self.agent.get_neighbors(r, c) if (nr, nc) in self.mine_positions)
        btn.config(state="disabled", relief=tk.SUNKEN, bg="#e0e0e0")
        
        if mine_count > 0:
            colors = {1: "blue", 2: "green", 3: "red", 4: "purple", 5: "maroon"}
            btn.config(text=str(mine_count), disabledforeground=colors.get(mine_count, "black"))
        else:
            for nr, nc in self.agent.get_neighbors(r, c):
                self.left_click(nr, nc)

        self.check_win()

    def right_click(self, r, c):
        if self.game_over or (r, c) in self.revealed: return
        btn = self.board[r][c]
        if (r, c) not in self.flags:
            self.flags.add((r, c))
            btn.config(text="🚩", fg="red")
        else:
            self.flags.remove((r, c))
            btn.config(text="")

    def check_win(self):
        if len(self.revealed) == (self.rows * self.cols) - self.mines:
            self.end_game(win=True)

    def end_game(self, win, clicked_mine=None):
        self.game_over = True
        self.bot_btn.config(state="disabled")
        self.bot_all_btn.config(state="disabled")
        
        for r in range(self.rows):
            for c in range(self.cols):
                btn = self.board[r][c]
                is_mine = (r, c) in self.mine_positions
                is_flag = (r, c) in self.flags

                if is_flag and not is_mine:
                    btn.config(text="❌", bg="#ffb3ba", fg="black")
                elif is_mine and not is_flag:
                    if clicked_mine == (r, c):
                        btn.config(text="💥", bg="#ff4a4a")
                    else:
                        btn.config(text="💣", bg="#e0e0e0")
                elif is_mine and is_flag:
                    btn.config(bg="#baffc9")
                    
        if win: 
            messagebox.showinfo("Result", "You won! 🎉")
        else: 
            messagebox.showinfo("Result", "You hit a mine! 💥")

    def get_knowledge_base(self):
        """ Convert board state to KB format for Bot to read """
        state = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.flags: 
                    state[(r, c)] = 'F'
                elif (r, c) in self.revealed:
                    state[(r, c)] = sum(1 for nr, nc in self.agent.get_neighbors(r, c) if (nr, nc) in self.mine_positions)
                else: 
                    state[(r, c)] = 'U'
        return state

    def bot_play_step(self):
        if self.game_over: return

        if self.first_click:
            r, c = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            self.left_click(r, c)
            return

        kb = self.get_knowledge_base()
        action_type, target_cell = self.agent.get_best_move(kb)

        if action_type == "SAFE" and target_cell:
            print(f"Bot opens safe cell: {target_cell}")
            self.left_click(*target_cell)
        elif action_type == "MINE" and target_cell:
            print(f"Bot flags mine: {target_cell}")
            self.right_click(*target_cell)
        else:
            
            unrevealed = [(r, c) for r in range(self.rows) for c in range(self.cols) 
                         if (r, c) not in self.revealed and (r, c) not in self.flags]
            if unrevealed:
                r, c = random.choice(unrevealed)
                print(f"Bot guesses random cell: ({r}, {c})")
                self.left_click(r, c)

    def bot_play_all(self):
        if self.game_over:
            messagebox.showinfo("Notice", "Game is over!")
            return
        
        self.bot_btn.config(state="disabled")
        self.bot_all_btn.config(state="disabled")
        self._auto_play_step()

    def _auto_play_step(self):
        if self.game_over:
            self.bot_btn.config(state="normal")
            self.bot_all_btn.config(state="normal")
            return
            
        self.bot_play_step()
        #delay 10ms
        self.master.after(10, self._auto_play_step)