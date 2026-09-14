"""
state.py
--------
Representa un estado del tablero.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Piece:
    id: int
    x: int
    y: int
    w: int
    h: int
    is_target: bool = False

    def cells(self) -> List[Tuple[int, int]]:
        return [
            (self.x + dx, self.y + dy) for dx in range(self.w) for dy in range(self.h)
        ]

    def copy(self) -> "Piece":
        return Piece(self.id, self.x, self.y, self.w, self.h, self.is_target)


class State:
    DIRECTIONS = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
    }

    def __init__(
        self,
        rows: int,
        cols: int,
        pieces: List[Piece],
        exit_area: Tuple[int, int, int, int],
        move: Optional[str] = None,
        parent: Optional["State"] = None,
    ):
        self.rows = rows
        self.cols = cols
        self.pieces = pieces
        # exit_area = (x, y, ancho, alto) de la casilla JUSTO FUERA del tablero
        self.exit = tuple(exit_area)
        self.move = move
        self.parent = parent

    def target_piece(self) -> Optional[Piece]:
        for p in self.pieces:
            if p.is_target:
                return p
        return None  # Si ya escapó, devolvemos None

    def is_goal(self) -> bool:
        return not any(p.is_target for p in self.pieces)

    def slide(self, direction: str) -> Optional["State"]:
        if direction not in self.DIRECTIONS:
            return None

        dx, dy = self.DIRECTIONS[direction]
        new_pieces = [p.copy() for p in self.pieces]
        any_piece_moved_at_all = False

        while True:
            moved_in_this_iteration = False
            p_to_remove = None

            for p in new_pieces:
                can_move_1_step = True
                nx, ny = p.x + dx, p.y + dy

                # 1. Comprobar colisión con bordes o la salida
                is_out_of_bounds = (
                    nx < 0 or ny < 0 or nx + p.w > self.cols or ny + p.h > self.rows
                )
                if is_out_of_bounds:
                    can_move_1_step = False
                    if p.is_target:
                        ex, ey, ew, eh = self.exit
                        # Validamos que se está deslizando exactamente por la salida
                        if dx == 1 and ex == self.cols and ny == ey:
                            can_move_1_step = True
                        elif dx == -1 and ex == -1 and ny == ey:
                            can_move_1_step = True
                        elif dy == 1 and ey == self.rows and nx == ex:
                            can_move_1_step = True
                        elif dy == -1 and ey == -1 and nx == ex:
                            can_move_1_step = True
                else:
                    # 2. Comprobar colisión con otras piezas
                    for other in new_pieces:
                        if other.id == p.id:
                            continue
                        if (
                            nx < other.x + other.w
                            and nx + p.w > other.x
                            and ny < other.y + other.h
                            and ny + p.h > other.y
                        ):
                            can_move_1_step = False
                            break

                if can_move_1_step:
                    p.x = nx
                    p.y = ny
                    moved_in_this_iteration = True
                    any_piece_moved_at_all = True

                    # 3. Si la pieza roja sale COMPLETAMENTE, se marca para desaparecer
                    if p.is_target:
                        if (
                            (dx == 1 and p.x >= self.cols)
                            or (dx == -1 and p.x + p.w <= 0)
                            or (dy == 1 and p.y >= self.rows)
                            or (dy == -1 and p.y + p.h <= 0)
                        ):
                            p_to_remove = p

            if p_to_remove:
                new_pieces.remove(p_to_remove)

            if not moved_in_this_iteration:
                break

        if not any_piece_moved_at_all:
            return None

        return State(
            self.rows, self.cols, new_pieces, self.exit, move=direction, parent=self
        )

    def get_possible_moves(self) -> List["State"]:
        result = []
        for direction in self.DIRECTIONS:
            new_state = self.slide(direction)
            if new_state is not None:
                result.append(new_state)
        return result

    def signature(self) -> Tuple:
        return tuple(sorted((p.id, p.x, p.y) for p in self.pieces))

    def __eq__(self, other):
        return isinstance(other, State) and self.signature() == other.signature()

    def __hash__(self):
        return hash(self.signature())

    def path_to_root(self) -> List["State"]:
        path = []
        s = self
        while s is not None:
            path.append(s)
            s = s.parent
        return list(reversed(path))

    def moves_to_root(self) -> List[str]:
        moves = []
        s = self
        while s.parent is not None:
            moves.append(s.move)
            s = s.parent
        return list(reversed(moves))

    @staticmethod
    def from_dict(data: dict) -> "State":
        pieces = [Piece(**p) for p in data["pieces"]]
        exit_area = tuple(data["exit"])
        return State(data["rows"], data["cols"], pieces, exit_area)

    def to_dict(self) -> dict:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "exit": list(self.exit),
            "pieces": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "w": p.w,
                    "h": p.h,
                    "is_target": p.is_target,
                }
                for p in self.pieces
            ],
        }

    def clone(self) -> "State":
        return State(self.rows, self.cols, [p.copy() for p in self.pieces], self.exit)
