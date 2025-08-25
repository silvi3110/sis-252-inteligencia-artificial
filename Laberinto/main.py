import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from collections import deque
import heapq
import math

class MazeSolver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Resolvedor de Laberintos - BFS y A*")
        self.root.geometry("800x650")
        
        # Configuración del laberinto
        self.rows = 15
        self.cols = 15
        self.cell_size = 30
        
        # Estados de las celdas
        self.WALL = 1
        self.PATH = 0
        self.START = 2
        self.END = 3
        self.VISITED = 4
        self.CURRENT = 5
        self.SOLUTION = 6
        
        # Colores para cada estado
        self.colors = {
            self.WALL: '#2C3E50',      # Azul oscuro para paredes
            self.PATH: '#ECF0F1',      # Gris claro para caminos
            self.START: '#27AE60',     # Verde para inicio
            self.END: '#E74C3C',       # Rojo para final
            self.VISITED: '#F39C12',   # Naranja para visitados
            self.CURRENT: '#9B59B6',   # Púrpura para actual
            self.SOLUTION: '#3498DB'   # Azul para solución
        }
        
        self.maze = []
        self.start_pos = (1, 1)
        self.end_pos = (13, 13)
        self.is_solving = False
        
        self.setup_ui()
        self.generate_maze()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones
        ttk.Button(control_frame, text="Generar Nuevo Laberinto", 
                  command=self.generate_maze).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Resolver con BFS", 
                  command=lambda: self.solve_maze('bfs')).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Resolver con A*", 
                  command=lambda: self.solve_maze('astar')).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Limpiar", 
                  command=self.clear_solution).pack(side=tk.LEFT, padx=(0, 5))
        
        # Canvas para el laberinto
        self.canvas = tk.Canvas(main_frame, 
                               width=self.cols * self.cell_size,
                               height=self.rows * self.cell_size,
                               bg='white')
        self.canvas.pack()
        
        # Label de información
        self.info_label = ttk.Label(main_frame, text="Listo para resolver laberintos")
        self.info_label.pack(pady=(10, 0))
        
    def generate_maze(self):
        """Genera un laberinto usando algoritmo de backtracking"""
        # Inicializar con todas las paredes
        self.maze = [[self.WALL for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Empezar desde una posición aleatoria impar
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = self.PATH
        
        # Stack para el algoritmo de backtracking
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack[-1]
            
            # Encontrar vecinos no visitados
            neighbors = []
            for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                nx, ny = x + dx, y + dy
                if (0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and 
                    self.maze[ny][nx] == self.WALL):
                    neighbors.append((nx, ny))
            
            if neighbors:
                # Elegir un vecino aleatorio
                nx, ny = random.choice(neighbors)
                
                # Abrir el camino entre la celda actual y el vecino
                self.maze[y + (ny - y) // 2][x + (nx - x) // 2] = self.PATH
                self.maze[ny][nx] = self.PATH
                
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Asegurar que hay un camino entre inicio y final
        self.maze[self.start_pos[0]][self.start_pos[1]] = self.START
        self.maze[self.end_pos[0]][self.end_pos[1]] = self.END
        
        self.draw_maze()
        self.info_label.config(text="Nuevo laberinto generado")
        
    def draw_maze(self):
        """Dibuja el laberinto en el canvas"""
        self.canvas.delete("all")
        
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = self.colors[self.maze[row][col]]
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=color, outline='#34495E', width=1)
                
    def get_neighbors(self, pos):
        """Obtiene los vecinos válidos de una posición"""
        row, col = pos
        neighbors = []
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            
            if (0 <= new_row < self.rows and 0 <= new_col < self.cols and
                self.maze[new_row][new_col] != self.WALL):
                neighbors.append((new_row, new_col))
                
        return neighbors
    
    def heuristic(self, pos1, pos2):
        """Distancia Manhattan para A*"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def solve_bfs(self):
        """Resuelve el laberinto usando Búsqueda en Anchura (BFS)"""
        queue = deque([(self.start_pos, [self.start_pos])])
        visited = {self.start_pos}
        
        while queue:
            current_pos, path = queue.popleft()
            
            # Marcar como visitado (excepto inicio y final)
            if (current_pos != self.start_pos and current_pos != self.end_pos and
                self.maze[current_pos[0]][current_pos[1]] != self.END):
                self.maze[current_pos[0]][current_pos[1]] = self.VISITED
            
            # Actualizar interfaz
            self.draw_maze()
            self.root.update()
            time.sleep(0.05)  # Pausa para visualización
            
            # ¿Llegamos al final?
            if current_pos == self.end_pos:
                return path
            
            # Explorar vecinos
            for neighbor in self.get_neighbors(current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        
        return None  # No se encontró solución
    
    def solve_astar(self):
        """Resuelve el laberinto usando A*"""
        # Cola de prioridad: (f_score, g_score, posición, camino)
        open_set = [(0, 0, self.start_pos, [self.start_pos])]
        g_scores = {self.start_pos: 0}
        visited = set()
        
        while open_set:
            f_score, g_score, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in visited:
                continue
                
            visited.add(current_pos)
            
            # Marcar como visitado (excepto inicio y final)
            if (current_pos != self.start_pos and current_pos != self.end_pos and
                self.maze[current_pos[0]][current_pos[1]] != self.END):
                self.maze[current_pos[0]][current_pos[1]] = self.VISITED
            
            # Actualizar interfaz
            self.draw_maze()
            self.root.update()
            time.sleep(0.05)  # Pausa para visualización
            
            # ¿Llegamos al final?
            if current_pos == self.end_pos:
                return path
            
            # Explorar vecinos
            for neighbor in self.get_neighbors(current_pos):
                if neighbor in visited:
                    continue
                
                tentative_g = g_score + 1
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h_score = self.heuristic(neighbor, self.end_pos)
                    f_score = tentative_g + h_score
                    new_path = path + [neighbor]
                    
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor, new_path))
        
        return None  # No se encontró solución
    
    def draw_solution(self, path):
        """Dibuja la solución encontrada"""
        if not path:
            return
            
        for pos in path:
            if pos != self.start_pos and pos != self.end_pos:
                self.maze[pos[0]][pos[1]] = self.SOLUTION
                
        self.draw_maze()
        
    def solve_maze(self, algorithm):
        """Resuelve el laberinto con el algoritmo especificado"""
        if self.is_solving:
            return
            
        self.is_solving = True
        self.clear_solution()
        
        start_time = time.time()
        
        try:
            if algorithm == 'bfs':
                self.info_label.config(text="Resolviendo con BFS...")
                path = self.solve_bfs()
            elif algorithm == 'astar':
                self.info_label.config(text="Resolviendo con A*...")
                path = self.solve_astar()
            else:
                path = None
                
            end_time = time.time()
            solve_time = round((end_time - start_time) * 1000, 2)
            
            if path:
                self.draw_solution(path)
                algorithm_name = "BFS" if algorithm == 'bfs' else "A*"
                self.info_label.config(text=f"¡Resuelto con {algorithm_name}! "
                                          f"Longitud: {len(path)} pasos, "
                                          f"Tiempo: {solve_time}ms")
            else:
                self.info_label.config(text="No se encontró solución")
                messagebox.showinfo("Sin solución", "No existe un camino al objetivo")
                
        except Exception as e:
            self.info_label.config(text=f"Error: {str(e)}")
            
        finally:
            self.is_solving = False
    
    def clear_solution(self):
        """Limpia la visualización de la solución anterior"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] in [self.VISITED, self.CURRENT, self.SOLUTION]:
                    self.maze[row][col] = self.PATH
        
        # Restaurar inicio y final
        self.maze[self.start_pos[0]][self.start_pos[1]] = self.START
        self.maze[self.end_pos[0]][self.end_pos[1]] = self.END
        
        self.draw_maze()
        self.info_label.config(text="Listo para resolver")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# Clase para futura implementación con Pygame
class PygameMazeSolver:
    """
    Clase preparada para implementación con Pygame.
    
    Ventajas de Pygame sobre Tkinter:
    - Mejor rendimiento para animaciones
    - Control más fino sobre los gráficos
    - Manejo más fluido de eventos
    - Posibilidad de efectos visuales avanzados
    
    Para usar Pygame, instalar con: pip install pygame
    """
    
    def __init__(self):
        # Importación condicional de Pygame
        try:
            import pygame
            self.pygame = pygame
            self.pygame_available = True
        except ImportError:
            self.pygame_available = False
            print("Pygame no está instalado. Usa 'pip install pygame' para habilitarlo.")
    
    def init_pygame(self):
        """Inicializa Pygame (implementar cuando sea necesario)"""
        if not self.pygame_available:
            return False
            
        self.pygame.init()
        # Aquí iría la configuración de Pygame
        return True

def main():
    """Función principal"""
    print("=== Resolvedor de Laberintos ===")
    print("\nAlgoritmos implementados:")
    print("• BFS (Búsqueda en Anchura): Garantiza la solución más corta")
    print("• A*: Más eficiente, usa heurística de distancia Manhattan")
    print("\nColores:")
    print("• Verde: Inicio")
    print("• Rojo: Final") 
    print("• Naranja: Celdas visitadas durante la búsqueda")
    print("• Azul: Camino de la solución")
    print("\nGenerando laberinto...")
    
    # Crear y ejecutar el resolvedor
    solver = MazeSolver()
    solver.run()

if __name__ == "__main__":
    main()