import tkinter as tk
from PIL import Image, ImageTk
import random, heapq

def es_posible(estado):
    inversiones = 0
    for i in range(8):
        for j in range(i+1, 9):
            if estado[i] != 0 and estado[j] != 0 and estado[i] > estado[j]:
                inversiones += 1
    return inversiones % 2 == 0

class Rompecabezas8:
    def __init__(self, ventana, ruta_imagen, imagenes_disponibles):
        self.ventana = ventana
        self.ventana.title("Rompecabezas 8")
        self.ruta_imagen = ruta_imagen
        self.imagenes_disponibles = imagenes_disponibles

        self.tamano_tablero = 300
        self.piezas_img = []
        self.cargar_imagen_inicial(ancho=self.tamano_tablero, alto=self.tamano_tablero)

        self.estado = list(range(9))
        while True:
            random.shuffle(self.estado)
            if es_posible(self.estado):
                break

        self.botones = []
        self.crear_tablero()
        self.actualizar_tablero()

        btn_resolver = tk.Button(
            self.ventana, 
            text="Resolver", 
            command=self.resolver_puzzle, 
            bg="#4CAF50",   
            fg="white",    
            font=("Arial", 12, "bold")  
        )
        btn_resolver.grid(row=3, column=0, columnspan=3, pady=10)

        self.imagen_seleccionada = tk.StringVar()
        self.imagen_seleccionada.set(list(self.imagenes_disponibles.keys())[0])
        menu_imagenes = tk.OptionMenu(self.ventana, self.imagen_seleccionada,
                                      *self.imagenes_disponibles.keys(),
                                      command=self.cambiar_imagen)
        menu_imagenes.grid(row=4, column=0, columnspan=3, pady=5)

        self.ventana.bind("<Configure>", self.redimensionar)

    def cambiar_imagen(self, opcion):
        self.ruta_imagen = self.imagenes_disponibles[opcion]
        
        ancho_actual = self.ventana.winfo_width()
        alto_actual = self.ventana.winfo_height()
        evento_simulado = type('Event', (object,), {
            'widget': self.ventana,
            'width': ancho_actual,
            'height': alto_actual
        })()
        self.redimensionar(evento_simulado)  
    
    
    def cargar_imagen_inicial(self, ancho, alto):
        imagen_original = Image.open(self.ruta_imagen)
        self.piezas = []
        self.piezas_img = []
        pieza_size_x = imagen_original.width // 3
        pieza_size_y = imagen_original.height // 3
        for fila in range(3):
            for columna in range(3):
                x0, y0 = columna * pieza_size_x, fila * pieza_size_y
                pieza = imagen_original.crop((x0, y0, x0 + pieza_size_x, y0 + pieza_size_y))
                pieza = pieza.resize((ancho//3, alto//3), Image.LANCZOS)
                pieza_tk = ImageTk.PhotoImage(pieza)
                self.piezas.append(pieza_tk)
                self.piezas_img.append(pieza_tk)

    
    def crear_tablero(self):
        for i in range(9):
            fila, columna = divmod(i, 3)
            b = tk.Button(self.ventana, command=lambda pos=i: self.mover_pieza(pos))
            b.grid(row=fila, column=columna, padx=1, pady=1, sticky="nsew")
            self.botones.append(b)

        
        for i in range(3):
            self.ventana.grid_rowconfigure(i, weight=1)
            self.ventana.grid_columnconfigure(i, weight=1)

    
    def mover_pieza(self, posicion):
        pos_vacia = self.estado.index(0)
        fila, columna = divmod(posicion, 3)
        fila_vacia, columna_vacia = divmod(pos_vacia, 3)

        if (abs(fila - fila_vacia) == 1 and columna == columna_vacia) or \
           (abs(columna - columna_vacia) == 1 and fila == fila_vacia):
            self.estado[pos_vacia], self.estado[posicion] = self.estado[posicion], self.estado[pos_vacia]
            self.actualizar_tablero()
            self.verificar_victoria()

    
    def actualizar_tablero(self):
        for i in range(9):
            valor = self.estado[i]
            if valor == 0:
                self.botones[i].config(image="", state=tk.DISABLED, bg="lightgray")
            else:
                self.botones[i].config(image=self.piezas[valor], state=tk.NORMAL, bg="SystemButtonFace")
                self.botones[i].image = self.piezas[valor]

    
    def verificar_victoria(self):
        if self.estado == list(range(9)):
            self.animacion_victoria()

    
    def animacion_victoria(self):
        colores = ["red", "yellow", "green", "blue", "orange", "pink", "purple"]
        for _ in range(30):
            i = random.randint(0, 8)
            self.botones[i].config(bg=random.choice(colores))
        self.ventana.after(500, self.restaurar_colores)

    def restaurar_colores(self):
        for i in range(9):
            self.botones[i].config(bg="SystemButtonFace")

    
    def resolver_puzzle(self):
        solucion = self.a_estrella(self.estado)
        if solucion:
            self.animar_movimientos(solucion)

    def a_estrella(self, inicio):
        meta = list(range(9))
        def heuristica(estado):
            distancia = 0
            for i, val in enumerate(estado):
                if val == 0: continue
                fila, col = divmod(i, 3)
                fila_goal, col_goal = divmod(val, 3)
                distancia += abs(fila - fila_goal) + abs(col - col_goal)
            return distancia

        frontera = [(heuristica(inicio), 0, inicio, [])]
        visitados = set()

        while frontera:
            _, costo, actual, camino = heapq.heappop(frontera)
            if actual == meta:
                return camino
            visitados.add(tuple(actual))

            pos_vacia = actual.index(0)
            fila, col = divmod(pos_vacia, 3)

            movimientos = []
            if fila > 0: movimientos.append(-3)
            if fila < 2: movimientos.append(3)
            if col > 0: movimientos.append(-1)
            if col < 2: movimientos.append(1)

            for mov in movimientos:
                nuevo = actual[:]
                nuevo[pos_vacia], nuevo[pos_vacia+mov] = nuevo[pos_vacia+mov], nuevo[pos_vacia]
                if tuple(nuevo) not in visitados:
                    heapq.heappush(frontera, (costo+1+heuristica(nuevo), costo+1, nuevo, camino+[nuevo]))
        return None

    def animar_movimientos(self, solucion):
        def paso(i=0):
            if i < len(solucion):
                self.estado = solucion[i]
                self.actualizar_tablero()
                self.ventana.after(300, paso, i+1)
            else:
                self.verificar_victoria()
        paso()

    
    def redimensionar(self, event):
        if event.widget == self.ventana:
            ancho_celda = event.width // 3
            alto_celda = event.height // 3
            if ancho_celda < 50 or alto_celda < 50:
                return

            self.cargar_imagen_inicial(ancho=event.width, alto=event.height)
            self.actualizar_tablero()


ventana = tk.Tk()
ventana.geometry("650x650")

imagenes_disponibles = {
    "BMW M3 GTR": "./bmw m3 gtr.jpg",
    "Lancer": "./lancer.jpg",
}

app = Rompecabezas8(ventana, imagenes_disponibles["BMW M3 GTR"], imagenes_disponibles)

ventana.mainloop()
