import tkinter as tk
from tkinter import font as tkfont
import time

COLORES = {
    "fondo": "#2C3E50",
    "celda": "#ECF0F1", 
    "numero_fijo": "#2C3E50",
    "numero_solucion": "#E74C3C",
    "numero_explorando": "#F39C12",
    "boton_resolver": "#27AE60",
    "boton_limpiar": "#E74C3C",
    "boton_verificar": "#3498DB",
    "texto_titulo": "#ECF0F1",
    "exito": "#27AE60",
    "error": "#E74C3C"
}

class SudokuPSSR:    
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku PSSR - Búsqueda en Espacio de Estados")
        self.root.config(bg=COLORES["fondo"])
        
        self.tablero_inicial = [
            [7, 0, 0, 0, 0, 9, 0, 8, 0],
            [0, 4, 0, 6, 2, 7, 0, 0, 0],
            [0, 2, 3, 1, 5, 0, 4, 9, 0],
            [2, 0, 5, 8, 7, 1, 6, 0, 0],
            [0, 7, 6, 3, 0, 0, 0, 5, 1],
            [0, 8, 0, 0, 9, 6, 0, 0, 0],
            [0, 9, 0, 7, 1, 3, 5, 0, 0],
            [5, 0, 8, 0, 0, 0, 9, 7, 0],
            [0, 0, 7, 0, 8, 0, 0, 0, 0]
        ]
        
        self.tablero_inicial1 = [
            [7, 0, 0, 0, 0, 9, 0, 8, 0],
            [0, 4, 0, 6, 2, 7, 0, 0, 0],
            [0, 2, 3, 1, 5, 0, 4, 9, 0],
            [2, 0, 5, 8, 7, 1, 6, 0, 0],
            [0, 7, 6, 3, 0, 0, 0, 5, 1],
            [0, 8, 0, 0, 9, 6, 0, 0, 0],
            [0, 9, 0, 7, 1, 3, 5, 0, 0],
            [5, 0, 8, 0, 0, 0, 9, 7, 0],
            [0, 0, 7, 0, 8, 0, 0, 1, 0]
        ]
        
        self.celdas = []
        self.resolviendo = False
        self.crear_interfaz()
        self.cargar_tablero_inicial()

    def crear_interfaz(self):
        frame_principal = tk.Frame(self.root, bg=COLORES["fondo"])
        frame_principal.pack(padx=20, pady=20)

        titulo = tk.Label(
            frame_principal,
            text="SUDOKU PSSR\nBúsqueda por Backtracking en Espacio de Estados",
            font=tkfont.Font(family="Arial", size=16, weight="bold"),
            bg=COLORES["fondo"],
            fg=COLORES["texto_titulo"]
        )
        titulo.pack(pady=10)

        self.crear_tablero(frame_principal)

        frame_botones = tk.Frame(frame_principal, bg=COLORES["fondo"])
        frame_botones.pack(pady=15)

        tk.Button(
            frame_botones,
            text="🔍 Resolver con PSSR",
            bg=COLORES["boton_resolver"],
            fg="white",
            font=tkfont.Font(size=11, weight="bold"),
            command=self.iniciar_resolucion_pssr,
            width=18
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones,
            text="🧹 Limpiar",
            bg=COLORES["boton_limpiar"],
            fg="white", 
            font=tkfont.Font(size=11, weight="bold"),
            command=self.limpiar_solucion,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones,
            text="✓ Verificar",
            bg=COLORES["boton_verificar"],
            fg="white",
            font=tkfont.Font(size=11, weight="bold"),
            command=self.verificar_solucion,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        info = tk.Label(
            frame_principal,
            text="🔸 Amarillo: Estado siendo explorado\n🔸 Rojo: Estado en la solución final",
            font=tkfont.Font(size=9),
            bg=COLORES["fondo"],
            fg=COLORES["texto_titulo"],
            justify=tk.LEFT
        )
        info.pack(pady=5)

    def crear_tablero(self, parent):
        frame_tablero = tk.Frame(parent, bg=COLORES["fondo"])
        frame_tablero.pack()

        for i in range(9):
            fila = []
            for j in range(9):
                padx = (3, 1) if j % 3 == 0 and j != 0 else (1, 1)
                pady = (3, 1) if i % 3 == 0 and i != 0 else (1, 1)
                
                celda = tk.Entry(
                    frame_tablero,
                    width=3,
                    font=tkfont.Font(size=14, weight="bold"),
                    justify="center",
                    bg=COLORES["celda"],
                    relief="solid",
                    borderwidth=1
                )
                celda.grid(row=i, column=j, padx=padx, pady=pady, ipady=8)
                fila.append(celda)
            self.celdas.append(fila)

    def cargar_tablero_inicial(self):
        for i in range(9):
            for j in range(9):
                if self.tablero_inicial[i][j] != 0:
                    self.celdas[i][j].insert(0, str(self.tablero_inicial[i][j]))
                    self.celdas[i][j].config(
                        fg=COLORES["numero_fijo"], 
                        state="readonly"
                    )
    
    def obtener_estado_actual(self):
        estado = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                valor = self.celdas[i][j].get()
                estado[i][j] = int(valor) if valor.isdigit() else 0
        return estado

    def es_estado_valido(self, estado, fila, col, numero):
        for c in range(9):
            if c != col and estado[fila][c] == numero:
                return False

        for f in range(9):
            if f != fila and estado[f][col] == numero:
                return False

        inicio_fila, inicio_col = 3 * (fila // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                f, c = inicio_fila + i, inicio_col + j
                if (f != fila or c != col) and estado[f][c] == numero:
                    return False

        return True

    def encontrar_siguiente_estado(self, estado):
        for i in range(9):
            for j in range(9):
                if estado[i][j] == 0:
                    return i, j
        return None

    def es_estado_objetivo(self, estado):
        return self.encontrar_siguiente_estado(estado) is None

    def busqueda_backtracking(self, estado):
        if self.es_estado_objetivo(estado):
            return True

        posicion = self.encontrar_siguiente_estado(estado)
        if not posicion:
            return False
            
        fila, col = posicion

        for numero in range(1, 10):
            if self.es_estado_valido(estado, fila, col, numero):
                estado[fila][col] = numero
                
                self.visualizar_exploracion(fila, col, numero)
                
                if self.busqueda_backtracking(estado):
                    return True
                
                estado[fila][col] = 0
                self.visualizar_backtrack(fila, col)

        return False

    def visualizar_exploracion(self, fila, col, numero):
        if not self.resolviendo:
            return
            
        celda = self.celdas[fila][col]
        if celda["state"] == "normal":
            celda.delete(0, tk.END)
            celda.insert(0, str(numero))
            celda.config(fg=COLORES["numero_explorando"])
            
        self.root.update()
        time.sleep(0.1)

    def visualizar_backtrack(self, fila, col):
        if not self.resolviendo:
            return
            
        celda = self.celdas[fila][col]
        if celda["state"] == "normal":
            celda.delete(0, tk.END)
            
        self.root.update()
        time.sleep(0.05)

    def mostrar_solucion_final(self, estado_solucion):
        for i in range(9):
            for j in range(9):
                if self.celdas[i][j]["state"] == "normal":
                    self.celdas[i][j].config(fg=COLORES["numero_solucion"])



    def iniciar_resolucion_pssr(self):
        if self.resolviendo:
            return
            
        self.resolviendo = True
        estado_inicial = self.obtener_estado_actual()
        
        estado_trabajo = [fila[:] for fila in estado_inicial]
        
        if self.busqueda_backtracking(estado_trabajo):
            self.mostrar_solucion_final(estado_trabajo)
            self.mostrar_mensaje("¡Solución encontrada! 🎉", COLORES["exito"])
        else:
            self.mostrar_mensaje("No existe solución 😞", COLORES["error"])
            
        self.resolviendo = False

    def limpiar_solucion(self):
        for i in range(9):
            for j in range(9):
                if self.celdas[i][j]["state"] == "normal":
                    self.celdas[i][j].delete(0, tk.END)
                    self.celdas[i][j].config(fg=COLORES["numero_solucion"])

    def verificar_solucion(self):
        estado = self.obtener_estado_actual()
        
        for fila in estado:
            if 0 in fila:
                self.mostrar_mensaje("Tablero incompleto", COLORES["error"])
                return

        for i in range(9):
            for j in range(9):
                numero = estado[i][j]
                estado[i][j] = 0
                if not self.es_estado_valido(estado, i, j, numero):
                    estado[i][j] = numero  
                    self.mostrar_mensaje("Solución incorrecta ❌", COLORES["error"])
                    return
                estado[i][j] = numero  

        self.mostrar_mensaje("¡Solución correcta! ✅", COLORES["exito"])

    def mostrar_mensaje(self, texto, color):
        label = tk.Label(
            self.root,
            text=texto,
            fg=color,
            bg=COLORES["fondo"],
            font=tkfont.Font(size=12, weight="bold")
        )
        label.pack(pady=5)
        self.root.after(3000, label.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = SudokuPSSR(root)
    root.mainloop()