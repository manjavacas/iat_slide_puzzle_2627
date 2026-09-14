"""
main.py
-------
Punto de entrada del juego.
"""

import argparse
import json
import sys
import time

from slide_puzzle.state import State
from slide_puzzle.algorithms import ALGORITHMS


def load_levels(path: str = "data/levels.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["levels"]


def build_initial_state(level: dict) -> State:
    return State.from_dict(level)


def solve(state: State, algorithm_name: str):
    if algorithm_name not in ALGORITHMS:
        raise ValueError(
            f"Algoritmo '{algorithm_name}' no encontrado. "
            f"Disponibles: {list(ALGORITHMS.keys())}"
        )
    algorithm_fn = ALGORITHMS[algorithm_name]
    start = time.time()
    moves = algorithm_fn(state)
    elapsed = time.time() - start
    return moves, elapsed


def run_headless(state: State, algorithm_name: str):
    print(f"Resolviendo con {algorithm_name}...")
    moves, elapsed = solve(state, algorithm_name)
    if moves is None:
        print("No se ha encontrado solución.")
        return
    print(f"Solución encontrada en {elapsed:.3f}s con {len(moves)} deslizamientos:")
    for i, direction in enumerate(moves, 1):
        print(f"  {i}. Deslizar hacia -> {direction}")


def run_gui(state: State, level_name: str, initial_algorithm: str = None):
    from slide_puzzle.gui import GUI

    gui = GUI(state, level_name=level_name, algorithm_names=list(ALGORITHMS.keys()))
    original_state = state.clone()

    def on_algorithm_selected(name):
        gui.solving = True
        gui.status_message = f"Resolviendo con {name}..."
        gui.draw()

        moves, elapsed = solve(gui.state, name)

        if moves is None:
            gui.status_message = (
                f"{name}: no se encontró solución desde el estado actual"
            )
            gui.solving = False
            gui.draw()
            return

        gui.draw()

        current = gui.state
        for direction in moves:
            current = current.slide(direction)
            gui.make_move(current, delay_ms=300)

        gui.solving = False
        if current.is_goal():
            gui.status_message = f"{name}: ¡resuelto en {len(moves)} deslizamientos!"
        gui.draw()

    def on_reset():
        gui.status_message = "Usa las flechas para deslizar."
        gui.make_move(original_state.clone())

    gui.on_algorithm_selected = on_algorithm_selected
    gui.on_reset = on_reset

    if initial_algorithm:
        on_algorithm_selected(initial_algorithm)

    gui.run()


def main():
    parser = argparse.ArgumentParser(description="Puzzle deslizante")
    parser.add_argument("--level", type=int, default=1, help="Número de nivel a cargar")
    parser.add_argument(
        "--algorithm",
        type=str,
        default=None,
        choices=list(ALGORITHMS.keys()),
        help="Algoritmo a ejecutar automáticamente al iniciar",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Ejecuta el algoritmo sin abrir la ventana gráfica",
    )
    parser.add_argument("--levels-file", type=str, default="data/levels.json")
    args = parser.parse_args()

    levels = load_levels(args.levels_file)
    if not (1 <= args.level <= len(levels)):
        print(f"Nivel fuera de rango. Debe estar entre 1 y {len(levels)}.")
        sys.exit(1)

    level = levels[args.level - 1]
    state = build_initial_state(level)
    level_name = level.get("name", f"Nivel {args.level}")

    if args.no_gui:
        algorithm_name = args.algorithm or list(ALGORITHMS.keys())[0]
        run_headless(state, algorithm_name)
    else:
        run_gui(state, level_name, initial_algorithm=args.algorithm)


if __name__ == "__main__":
    main()
