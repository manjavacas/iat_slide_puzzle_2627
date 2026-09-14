"""
gui.py
------
Interfaz gráfica del puzzle.
"""

import tkinter as tk
from slide_puzzle.state import State

CELL_SIZE = 90
MARGIN = 4
BOARD_PAD = 70

COLOR_BG = "#1e1e23"
COLOR_BOARD = "#32323c"
COLOR_GRID = "#46464f"
COLOR_TEXT = "#e6e6e6"
COLOR_TARGET = "#dc3c3c"
COLOR_PIECE_PALETTE = [
    "#5a96dc",
    "#5ac896",
    "#e6be5a",
    "#aa78dc",
    "#78c8dc",
    "#dc8c5a",
    "#96965a",
    "#c864a0",
]
COLOR_EXIT = "#ffd700"
COLOR_LABEL = "#141414"


class GUI:
    def __init__(
        self, initial_state: State, level_name: str = "", algorithm_names=None
    ):
        self.state = initial_state
        self.level_name = level_name
        self.algorithm_names = algorithm_names or []

        self.status_message = "Usa las flechas para deslizar."
        self.solving = False
        self.on_algorithm_selected = None
        self.on_reset = None

        self._build_window()
        self.draw()

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Fuga")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        canvas_w = self.state.cols * CELL_SIZE + BOARD_PAD * 2
        canvas_h = self.state.rows * CELL_SIZE + BOARD_PAD * 2

        self.title_label = tk.Label(
            self.root,
            text=f"Fuga — {self.level_name}",
            font=("Arial", 16, "bold"),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=BOARD_PAD, pady=(12, 0))

        self.status_label = tk.Label(
            self.root,
            text=self.status_message,
            font=("Arial", 10),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=BOARD_PAD, pady=(2, 8))

        self.canvas = tk.Canvas(
            self.root,
            width=canvas_w,
            height=canvas_h,
            bg=COLOR_BOARD,
            highlightthickness=0,
        )
        self.canvas.pack(padx=BOARD_PAD, pady=4)

        self.button_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.button_frame.pack(fill="x", padx=BOARD_PAD, pady=(4, 4))

        self.buttons = {}
        for name in self.algorithm_names:
            btn = tk.Button(
                self.button_frame,
                text=name,
                width=8,
                command=lambda n=name: self._trigger_algorithm(n),
            )
            btn.pack(side="left", padx=(0, 6))
            self.buttons[name] = btn

        reset_btn = tk.Button(
            self.button_frame, text="Reiniciar", width=10, command=self._trigger_reset
        )
        reset_btn.pack(side="left", padx=(6, 0))
        self.buttons["__reset__"] = reset_btn

        self.root.bind("<Up>", lambda e: self._handle_key("UP"))
        self.root.bind("<Down>", lambda e: self._handle_key("DOWN"))
        self.root.bind("<Left>", lambda e: self._handle_key("LEFT"))
        self.root.bind("<Right>", lambda e: self._handle_key("RIGHT"))

    def _trigger_algorithm(self, name):
        if self.on_algorithm_selected and not self.solving:
            self.on_algorithm_selected(name)

    def _trigger_reset(self):
        if self.on_reset:
            self.on_reset()

    def make_move(self, state: State, delay_ms: int = 0):
        self.state = state
        self.draw()
        if delay_ms:
            self._wait(delay_ms)
        if self.state.is_goal():
            self.status_message = "¡Puzzle resuelto!"
            self.draw()

    def _wait(self, ms: int):
        done = tk.BooleanVar(value=False)
        self.root.after(ms, lambda: done.set(True))
        self.root.wait_variable(done)

    def run(self):
        self.root.mainloop()

    def _handle_key(self, direction):
        if self.solving:
            return
        new_state = self.state.slide(direction)
        if new_state is not None:
            self.make_move(new_state)
        else:
            self.draw()

    def draw(self):
        self.title_label.config(text=f"Fuga — {self.level_name}")
        self.status_label.config(text=self.status_message)

        for btn in self.buttons.values():
            btn.config(state="disabled" if self.solving else "normal")

        self.canvas.delete("all")
        self._draw_board()
        self._draw_pieces()

        self.root.update_idletasks()
        self.root.update()

    def _draw_board(self):
        rows, cols = self.state.rows, self.state.cols

        # Dibuja la cuadrícula
        for r in range(rows):
            for c in range(cols):
                x0 = BOARD_PAD + c * CELL_SIZE
                y0 = BOARD_PAD + r * CELL_SIZE
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + CELL_SIZE,
                    y0 + CELL_SIZE,
                    outline=COLOR_GRID,
                    fill=COLOR_BOARD,
                )

        # Dibuja la salida al exterior
        ex, ey, ew, eh = self.state.exit
        ex0 = BOARD_PAD + ex * CELL_SIZE
        ey0 = BOARD_PAD + ey * CELL_SIZE
        ex1 = ex0 + ew * CELL_SIZE
        ey1 = ey0 + eh * CELL_SIZE
        self.canvas.create_rectangle(ex0, ey0, ex1, ey1, outline=COLOR_EXIT, width=4)

    def _draw_pieces(self):
        # Cuando la pieza sale completamente, desaparece de self.state.pieces
        for p in self.state.pieces:
            x0 = BOARD_PAD + p.x * CELL_SIZE + MARGIN
            y0 = BOARD_PAD + p.y * CELL_SIZE + MARGIN
            x1 = BOARD_PAD + (p.x + p.w) * CELL_SIZE - MARGIN
            y1 = BOARD_PAD + (p.y + p.h) * CELL_SIZE - MARGIN

            color = (
                COLOR_TARGET
                if p.is_target
                else COLOR_PIECE_PALETTE[p.id % len(COLOR_PIECE_PALETTE)]
            )

            self.canvas.create_rectangle(
                x0, y0, x1, y1, fill=color, outline=color, width=0
            )
            self.canvas.create_text(
                (x0 + x1) / 2,
                (y0 + y1) / 2,
                text=str(p.id),
                fill=COLOR_LABEL,
                font=("Arial", 14, "bold"),
            )
