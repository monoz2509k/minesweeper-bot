import random
from bot_dfs import DFSAgent


class GameLogic:
    """Game logic tách ra khỏi GUI để test"""

    def __init__(self, rows=9, cols=9, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.agent = DFSAgent(rows, cols)

        self.mine_positions = set()
        self.flags = set()
        self.revealed = set()
        self.game_over = False
        self.win = False
        self.first_click = True
        self.clicks = 0

        self._place_mines()

    def _place_mines(self):
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

    def left_click(self, r, c):
        if self.game_over or (r, c) in self.revealed or (r, c) in self.flags:
            return
        self.clicks += 1

        # First click safety
        if self.first_click:
            self.first_click = False
            if (r, c) in self.mine_positions:
                self.mine_positions.remove((r, c))
                empty = [(nr, nc) for nr in range(self.rows) for nc in range(self.cols)
                         if (nr, nc) not in self.mine_positions and (nr, nc) != (r, c)]
                self.mine_positions.add(random.choice(empty))

        self.revealed.add((r, c))

        if (r, c) in self.mine_positions:
            self.game_over = True
            self.win = False
            return

        mine_count = sum(1 for n in self.agent.get_neighbors(r, c) if n in self.mine_positions)

        if mine_count == 0:
            for nr, nc in self.agent.get_neighbors(r, c):
                if (nr, nc) not in self.revealed:
                    self.left_click(nr, nc)

        self._check_win()

    def right_click(self, r, c):
        if self.game_over or (r, c) in self.revealed:
            return
        if (r, c) not in self.flags:
            self.flags.add((r, c))
        else:
            self.flags.remove((r, c))

    def _check_win(self):
        if len(self.revealed) == (self.rows * self.cols) - self.mines:
            self.game_over = True
            self.win = True

    def get_knowledge_base(self):
        state = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.flags:
                    state[(r, c)] = 'F'
                elif (r, c) in self.revealed:
                    state[(r, c)] = sum(1 for n in self.agent.get_neighbors(r, c) if n in self.mine_positions)
                else:
                    state[(r, c)] = 'U'
        return state


def run_simulation(n_games=100, rows=9, cols=9, mines=10):
    wins = 0
    total_clicks = 0

    for i in range(n_games):
        game = GameLogic(rows, cols, mines)

        # First click random
        r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
        game.left_click(r, c)

        # Bot plays until game over
        while not game.game_over:
            kb = game.get_knowledge_base()
            action, cell = game.agent.get_best_move(kb)

            if action == "SAFE" and cell:
                game.left_click(*cell)
            elif action == "MINE" and cell:
                game.right_click(*cell)
            else:
                # Random guess
                unrevealed = [(r, c) for r in range(rows) for c in range(cols)
                              if (r, c) not in game.revealed and (r, c) not in game.flags]
                if unrevealed:
                    game.left_click(*random.choice(unrevealed))
                else:
                    break

        result = "PASS ✅" if game.win else "FAIL ❌"
        print(f"Game {i+1:>3}: {result} | Clicks: {game.clicks}")

        if game.win:
            wins += 1
        total_clicks += game.clicks

    print(f"\n{'='*40}")
    print(f"Win rate  : {wins}/{n_games} ({wins/n_games*100:.1f}%)")
    print(f"Avg clicks: {total_clicks/n_games:.1f}")
    print(f"{'='*40}")


if __name__ == "__main__":
    run_simulation(n_games=1000, rows=9, cols=9, mines=10)