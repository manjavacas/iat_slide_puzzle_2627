"""
algorithm.py
------------
Aquí es donde se deben implementar los algoritmos de resolución del
puzzle.

Cada algoritmo recibe un `State` inicial (ver state.py) y debe devolver:
    - una lista de direcciones ["UP", "DOWN", "LEFT", "RIGHT"] que resuelven
      el puzzle deslizando el tablero, o
    - None si no encuentra solución.

`State` proporciona las siguientes funcionalidades:
    - state.is_goal()                -> bool indicando si es un estado final
    - state.get_possible_moves()     -> lista de nuevos States (un deslizamiento) a partir del actual
    - state.slide(dir)               -> nuevo State obtenido al deslizar o None si no es válido
    - state.moves_to_root()          -> reconstruye la lista de deslizamientos aplicados
    - state == otro_state            -> compara estados

Para que `main.py` y `gui.py` puedan encontrar tu algoritmo automáticamente,
regístralo en el diccionario `ALGORITHMS` al final de este archivo.
"""

from collections import deque
from slide_puzzle.state import State

# ---------------------------------------------------------------------- #
# Búsqueda primero en anchura (BFS)
# ---------------------------------------------------------------------- #
def bfs(initial_state: State):
    raise NotImplementedError


# ---------------------------------------------------------------------- #
# Búsqueda primero en profundidad (DFS)
# ---------------------------------------------------------------------- #
def dfs(initial_state: State):
    raise NotImplementedError


# ---------------------------------------------------------------------- #
# Búsqueda A*
# ---------------------------------------------------------------------- #
def astar(initial_state: State):
    raise NotImplementedError


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "A*": astar
}
