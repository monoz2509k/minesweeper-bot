import sys
import os
import random
from simulation import GameLogic, run_simulation

class _NullIO:
    def write(self, *a): pass
    def flush(self): pass

def _progress(current, total, label, width=35):
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    pct = current / total * 100
    sys.stdout.write(f'\r  {label}  [{bar}] {current}/{total} ({pct:.0f}%)')
    sys.stdout.flush()
    if current == total:
        sys.stdout.write('\n')

def run_benchmark():
    difficulties = [
        ("Easy",   5,  5,  5, 100),
        ("Medium", 9,  9, 10, 100),
        ("Hard",  16, 16, 40,  50),
    ]
    
    results_name = []
    results_win_rate = []
    results_avg_clicks = []

    with open("BENCHMARK_RESULTS.md", "w", encoding="utf-8") as f:
        f.write("# Minesweeper Bot DFS - Benchmark Results\n\n")
        f.write("| Difficulty | Grid | Mines | Rounds | Win Rate (%) | Avg Clicks |\n")
        f.write("|---|---|---|---|---|---|\n")

        total_difficulties = len(difficulties)
        print("Running benchmark...")
        for diff_idx, (name, rows, cols, mines, n_games) in enumerate(difficulties, 1):
            label = f"[{diff_idx}/{total_difficulties}] {name} ({rows}x{cols})"
            
            wins = 0
            total_clicks = 0

            for i in range(n_games):
                _progress(i + 1, n_games, label)
                game = GameLogic(rows, cols, mines)
                r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
                
                _real_stdout = sys.stdout
                sys.stdout = _NullIO()
                try:
                    game.left_click(r, c)
                    while not game.game_over:
                        kb = game.get_knowledge_base()
                        unrevealed = [(rr, cc) for rr in range(rows) for cc in range(cols)
                                      if (rr, cc) not in game.revealed and (rr, cc) not in game.flags]
                        flagged = list(game.flags)
                        action, cell = game.agent.get_best_move(kb, unrevealed=unrevealed, flagged=flagged)
                        if action == "SAFE" and cell:
                            game.left_click(*cell)
                        elif action == "MINE" and cell:
                            game.right_click(*cell)
                        else:
                            if unrevealed:
                                game.left_click(*random.choice(unrevealed))
                            else:
                                break
                finally:
                    sys.stdout = _real_stdout

                if game.win:
                    wins += 1
                total_clicks += game.clicks
            
            win_rate = (wins / n_games) * 100
            avg_clicks = total_clicks / n_games
            
            results_name.append(name)
            results_win_rate.append(win_rate)
            results_avg_clicks.append(avg_clicks)
            
            f.write(f"| {name} | {rows}x{cols} | {mines} | {n_games} | {win_rate:.1f}% | {avg_clicks:.1f} |\n")
            print(f"  -> Done! Win Rate: {win_rate:.1f}%")

    print(f"\n✅ Benchmark complete! Results saved to BENCHMARK_RESULTS.md")

    results_meta = [(name, rows, cols, mines, n_games) for name, rows, cols, mines, n_games in difficulties]
    _generate_chart(results_meta, results_win_rate, results_avg_clicks)


def _generate_chart(meta, win_rates, avg_clicks):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        import numpy as np

        names       = [m[0] for m in meta]
        grids       = [f"{m[1]}x{m[2]}" for m in meta]
        mines_list  = [m[3] for m in meta]
        rounds_list = [m[4] for m in meta]
        densities   = [m[3] / (m[1] * m[2]) * 100 for m in meta]   # mine density %
        total_cells = [m[1] * m[2] for m in meta]

        colors = ['#00d4aa', '#f5a623', '#e74c3c']
        x = np.arange(len(names))

        fig = plt.figure(figsize=(14, 8), facecolor='#1a1a2e')
        fig.suptitle('Minesweeper DFS Bot — Performance Benchmark',
                     fontsize=16, fontweight='bold', color='white', y=0.97)

        gs = gridspec.GridSpec(2, 2, figure=fig, wspace=0.38, hspace=0.55,
                               height_ratios=[3, 1])

        # ── helper to style axes ──────────────────────────────────────────────
        def style_ax(ax, title, ylabel):
            ax.set_facecolor('#16213e')
            ax.set_title(title, color='white', fontsize=12, pad=8)
            ax.set_ylabel(ylabel, color='white', fontsize=10)
            ax.tick_params(axis='both', colors='white')
            ax.spines[['top', 'right']].set_visible(False)
            ax.spines[['left', 'bottom']].set_color('#444')
            ax.yaxis.grid(True, color='#333', linestyle='--', linewidth=0.6, zorder=0)
            ax.set_axisbelow(True)

        # ── x-tick labels: Name + grid + mines ───────────────────────────────
        xtick_labels = [f"{n}\n{g}  |  {m} mines" for n, g, m in zip(names, grids, mines_list)]

        # ── LEFT TOP: Win Rate ────────────────────────────────────────────────
        ax1 = fig.add_subplot(gs[0, 0])
        style_ax(ax1, 'Win Rate by Difficulty', 'Win Rate (%)')
        bars1 = ax1.bar(x, win_rates, color=colors, width=0.5, edgecolor='white', linewidth=0.5, zorder=3)
        for bar, val in zip(bars1, win_rates):
            ax1.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                     f'{val:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')
        ax1.set_xticks(x)
        ax1.set_xticklabels(xtick_labels, color='white', fontsize=9)
        ax1.set_yticks(range(0, 110, 10))
        ax1.set_ylim(0, 112)

        # ── RIGHT TOP: Avg Clicks ─────────────────────────────────────────────
        ax2 = fig.add_subplot(gs[0, 1])
        style_ax(ax2, 'Avg Clicks per Game', 'Clicks')
        bars2 = ax2.bar(x, avg_clicks, color=colors, width=0.5, edgecolor='white', linewidth=0.5, zorder=3)
        for bar, val in zip(bars2, avg_clicks):
            ax2.text(bar.get_x() + bar.get_width() / 2, val + 1,
                     f'{val:.0f}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')
        ax2.set_xticks(x)
        ax2.set_xticklabels(xtick_labels, color='white', fontsize=9)
        ax2.set_ylim(0, max(avg_clicks) * 1.3)

        # ── BOTTOM: Summary table ─────────────────────────────────────────────
        ax3 = fig.add_subplot(gs[1, :])
        ax3.set_facecolor('#0f3460')
        ax3.axis('off')

        col_labels = ['Difficulty', 'Grid', 'Mines', 'Mine Density', 'Rounds Tested', 'Win Rate', 'Avg Clicks']
        table_data = [
            [names[i], grids[i], str(mines_list[i]),
             f'{densities[i]:.1f}%', str(rounds_list[i]),
             f'{win_rates[i]:.1f}%', f'{avg_clicks[i]:.0f}']
            for i in range(len(names))
        ]

        tbl = ax3.table(
            cellText=table_data,
            colLabels=col_labels,
            cellLoc='center',
            loc='center'
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9.5)
        tbl.scale(1, 1.6)

        for (row, col), cell in tbl.get_celld().items():
            cell.set_edgecolor('#444')
            if row == 0:
                cell.set_facecolor('#0d7377')
                cell.set_text_props(color='white', fontweight='bold')
            else:
                cell.set_facecolor('#16213e')
                cell.set_text_props(color='white')

        ax3.set_title('Summary', color='white', fontsize=11, pad=6, loc='left')

        plt.savefig('win_rates_chart.png', dpi=200, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        print("✅ Chart saved as 'win_rates_chart.png'")
    except Exception as e:
        print(f"Could not generate chart: {e}")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')
    run_benchmark()
