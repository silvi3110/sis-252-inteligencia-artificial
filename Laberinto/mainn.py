import heapq
import math
import sys
import os
from typing import List, Tuple, Optional, Set
import pygame

pygame.init()
pygame.mixer.init()

ANCHO_VENTANA = 1200
ALTO_VENTANA = 690
TAMAÑO_CELDA = 35
COLS = 20
FILAS = 15

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
VERDE_CLARO = (215, 224, 67)
AZUL_CLARO = (173, 216, 230)
VERDE_OSCURO = (0, 128, 0)

MENU = 0
JUGANDO = 1
RESOLVIENDO = 2
GANADO = 3

class Nodo:
    def __init__(self, posicion: Tuple[int, int], g_costo: float = 0, h_costo: float = 0, padre: Optional['Nodo'] = None):
        self.posicion = posicion  
        self.g_costo = g_costo   
        self.h_costo = h_costo   
        self.f_costo = g_costo + h_costo  
        self.padre = padre       
    
    def __lt__(self, otro):
        return self.f_costo < otro.f_costo
    
    def __eq__(self, otro):
        return self.posicion == otro.posicion

class LaberintoAStar:
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Resolvedor de Laberintos A* - IA")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequena = pygame.font.Font(None, 24)
        self.fuente_grande = pygame.font.Font(None, 48)
        
        self.estado = MENU
        self.jugador_pos = (1, 1)
        self.objetivo_pos = (18, 13)
        self.direccion_jugador = "right"
        
        self.open_set = []  
        self.closed_set: Set[Tuple[int, int]] = set() 
        self.came_from = {} 
        self.g_score = {}   
        self.camino_optimo = []  
        self.nodos_explorados = [] 
        self.paso_actual = 0
        self.solucion_encontrada = False
        
        self.tiempo_inicio = 0
        self.tiempo_fin = 0
        self.pasos_algoritmo = 0
        self.nodos_expandidos = 0
        
        self.crear_laberinto()
        
        self.cargar_sprites()
        self.cargar_sonidos()
        
        self.musica_menu_sonando = False
    
    def crear_laberinto(self):
        self.laberinto = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
    
    def cargar_sprites(self):
        self.sprites = {}
        direcciones = ["up", "down", "left", "right"]
        colores = [AMARILLO, AMARILLO, AMARILLO, AMARILLO]
        
        for i, direccion in enumerate(direcciones):
            try:
                imagen = pygame.image.load(f"pacman-{direccion}.png")
                self.sprites[direccion] = pygame.transform.scale(imagen, (TAMAÑO_CELDA-4, TAMAÑO_CELDA-4))
            except:
                superficie = pygame.Surface((TAMAÑO_CELDA-4, TAMAÑO_CELDA-4))
                superficie.set_colorkey(NEGRO)
                pygame.draw.circle(superficie, colores[i], (TAMAÑO_CELDA//2-2, TAMAÑO_CELDA//2-2), TAMAÑO_CELDA//2-3)
                self.sprites[direccion] = superficie
        
        try:
            self.imagen_menu = pygame.image.load("./Laberinto/menu.gif")
            self.imagen_menu = pygame.transform.scale(self.imagen_menu, (ANCHO_VENTANA, ALTO_VENTANA))
        except:
            self.imagen_menu = None
        try:
            self.imagen_laberinto = pygame.image.load("./Laberinto/laberinto.jpg")
            self.imagen_laberinto = pygame.transform.scale(self.imagen_laberinto, (ANCHO_VENTANA, ALTO_VENTANA))
        except:
            self.imagen_laberinto = None
    
    def cargar_sonidos(self):
        """Carga los sonidos del juego"""
        try:
            self.sonido_victoria = pygame.mixer.Sound("./Laberinto/hasganado.mp3")
        except:
            self.sonido_victoria = None
        
        try:
            pygame.mixer.music.load("./Laberinto/menu.mp3")
        except:
            print("No se pudo cargar menu.mp3")
    
    def reproducir_musica_menu(self):
        if not self.musica_menu_sonando:
            try:
                pygame.mixer.music.play(-1)  
                self.musica_menu_sonando = True
            except:
                pass
    
    def detener_musica_menu(self):
        if self.musica_menu_sonando:
            pygame.mixer.music.stop()
            self.musica_menu_sonando = False
    
    def heuristica_manhattan(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def obtener_vecinos(self, posicion: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = posicion
        vecinos = []
        
        movimientos = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in movimientos:
            nuevo_x, nuevo_y = x + dx, y + dy
            
            if 0 <= nuevo_x < COLS and 0 <= nuevo_y < FILAS:
                if self.laberinto[nuevo_y][nuevo_x] == 0:
                    vecinos.append((nuevo_x, nuevo_y))
        
        return vecinos
    
    def inicializar_astar(self):
        inicio = self.jugador_pos
        objetivo = self.objetivo_pos
        
        self.open_set = []
        self.closed_set = set()
        self.came_from = {}
        self.g_score = {}
        self.camino_optimo = []
        self.nodos_explorados = []
        self.solucion_encontrada = False
        
        self.tiempo_inicio = pygame.time.get_ticks()
        self.tiempo_fin = 0
        self.pasos_algoritmo = 0
        self.nodos_expandidos = 0
        
        nodo_inicio = Nodo(inicio, 0, self.heuristica_manhattan(inicio, objetivo))
        self.g_score[inicio] = 0
        
        heapq.heappush(self.open_set, nodo_inicio)
    
    def paso_astar(self) -> bool:
        if not self.open_set:
            self.tiempo_fin = pygame.time.get_ticks()
            return False
        
        nodo_actual = heapq.heappop(self.open_set)
        posicion_actual = nodo_actual.posicion
        
        self.closed_set.add(posicion_actual)
        self.nodos_explorados.append(posicion_actual)
        self.pasos_algoritmo += 1
        self.nodos_expandidos += 1
        
        if posicion_actual == self.objetivo_pos:
            self.solucion_encontrada = True
            self.tiempo_fin = pygame.time.get_ticks()
            self.reconstruir_camino(nodo_actual)
            if self.sonido_victoria:
                self.sonido_victoria.play()
            return False
        
        for vecino_pos in self.obtener_vecinos(posicion_actual):
            if vecino_pos in self.closed_set:
                continue  
            
            tentativo_g = self.g_score[posicion_actual] + 1
            
            if vecino_pos not in self.g_score or tentativo_g < self.g_score[vecino_pos]:
                self.came_from[vecino_pos] = posicion_actual
                self.g_score[vecino_pos] = tentativo_g
                h_costo = self.heuristica_manhattan(vecino_pos, self.objetivo_pos)
                
                nodo_vecino = Nodo(vecino_pos, tentativo_g, h_costo, nodo_actual)
                heapq.heappush(self.open_set, nodo_vecino)
        
        return True 
    
    def reconstruir_camino(self, nodo_final: Nodo):
        camino = []
        nodo_actual = nodo_final
        
        while nodo_actual is not None:
            camino.append(nodo_actual.posicion)
            if nodo_actual.padre is None and nodo_actual.posicion in self.came_from:
                padre_pos = self.came_from[nodo_actual.posicion]
                nodo_actual = Nodo(padre_pos)
                if padre_pos in self.came_from:
                    continue
                else:
                    break
            else:
                nodo_actual = nodo_actual.padre
        
        if len(camino) <= 1:
            camino = []
            actual = self.objetivo_pos
            while actual in self.came_from:
                camino.append(actual)
                actual = self.came_from[actual]
            camino.append(self.jugador_pos)
        
        camino.reverse()  
        self.camino_optimo = camino
    
    def mover_jugador(self, nueva_pos: Tuple[int, int]):
        if nueva_pos != self.jugador_pos:
            dx = nueva_pos[0] - self.jugador_pos[0]
            dy = nueva_pos[1] - self.jugador_pos[1]
            
            if dx > 0:
                self.direccion_jugador = "right"
            elif dx < 0:
                self.direccion_jugador = "left"
            elif dy > 0:
                self.direccion_jugador = "down"
            elif dy < 0:
                self.direccion_jugador = "up"
            
            self.jugador_pos = nueva_pos
    
    def dibujar_laberinto(self):
        if self.imagen_laberinto:
            self.ventana.blit(self.imagen_laberinto, (0, 0))
            overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            overlay.fill(BLANCO)
            overlay.set_alpha(0)  
            self.ventana.blit(overlay, (0, 0))
        else:
            self.ventana.fill(BLANCO)
            
        for y in range(FILAS):
            for x in range(COLS):
                rect = pygame.Rect(x * TAMAÑO_CELDA, y * TAMAÑO_CELDA, TAMAÑO_CELDA, TAMAÑO_CELDA)
                
                if self.laberinto[y][x] == 1:  
                    pygame.draw.rect(self.ventana, VERDE_CLARO, rect)
                else:
                    pygame.draw.rect(self.ventana, BLANCO, rect)
                
                pygame.draw.rect(self.ventana, NEGRO, rect, 1)
    
    def dibujar_visualizacion_astar(self):
        for nodo in self.open_set:
            x, y = nodo.posicion
            rect = pygame.Rect(x * TAMAÑO_CELDA + 2, y * TAMAÑO_CELDA + 2, 
                             TAMAÑO_CELDA - 4, TAMAÑO_CELDA - 4)
            pygame.draw.rect(self.ventana, VERDE_CLARO, rect)
        
        for pos in self.closed_set:
            x, y = pos
            rect = pygame.Rect(x * TAMAÑO_CELDA + 4, y * TAMAÑO_CELDA + 4, 
                             TAMAÑO_CELDA - 8, TAMAÑO_CELDA - 8)
            pygame.draw.rect(self.ventana, AZUL_CLARO, rect)
        
        if self.camino_optimo:
            for pos in self.camino_optimo:
                x, y = pos
                rect = pygame.Rect(x * TAMAÑO_CELDA + 6, y * TAMAÑO_CELDA + 6, 
                                 TAMAÑO_CELDA - 12, TAMAÑO_CELDA - 12)
                pygame.draw.rect(self.ventana, MAGENTA, rect)
    
    def dibujar_elementos(self):
        obj_x, obj_y = self.objetivo_pos
        obj_rect = pygame.Rect(obj_x * TAMAÑO_CELDA + 2, obj_y * TAMAÑO_CELDA + 2, 
                              TAMAÑO_CELDA - 4, TAMAÑO_CELDA - 4)
        pygame.draw.rect(self.ventana, ROJO, obj_rect)
        
        jug_x, jug_y = self.jugador_pos
        sprite = self.sprites[self.direccion_jugador]
        self.ventana.blit(sprite, (jug_x * TAMAÑO_CELDA + 2, jug_y * TAMAÑO_CELDA + 2))
    
    def dibujar_info(self):
        info_y = FILAS * TAMAÑO_CELDA + 10
        
        if self.estado == GANADO and self.solucion_encontrada:
            tiempo_total = (self.tiempo_fin - self.tiempo_inicio) / 1000.0  
            
            textos = [
                f"¡LABERINTO RESUELTO! ✓",
                f"Tiempo: {tiempo_total:.2f} segundos",
                f"Pasos del algoritmo: {self.pasos_algoritmo}",
                f"Nodos explorados: {len(self.closed_set)}",
                f"Camino óptimo: {len(self.camino_optimo)} pasos",
                f"Nodos en frontera: {len(self.open_set)}"
            ]
            
            superficie_titulo = self.fuente_pequena.render(textos[0], True, VERDE_OSCURO)
            self.ventana.blit(superficie_titulo, (10, info_y))
            
            for i, texto in enumerate(textos[1:], 1):
                superficie = self.fuente_pequena.render(texto, True, NEGRO)
                self.ventana.blit(superficie, (10, info_y + i * 25))
        
        else:
            textos = [
                f"Open Set (Frontera): {len(self.open_set)} nodos",
                f"Closed Set (Explorados): {len(self.closed_set)} nodos",
                f"Pasos del algoritmo: {self.pasos_algoritmo}",
                f"Camino óptimo: {len(self.camino_optimo)} pasos" if self.camino_optimo else "Buscando camino..."
            ]
            
            for i, texto in enumerate(textos):
                superficie = self.fuente_pequena.render(texto, True, NEGRO)
                self.ventana.blit(superficie, (10, info_y + i * 25))
        
        leyenda_x = 400
        colores_leyenda = [
            (VERDE_CLARO, "Open Set (por explorar)"),
            (AZUL_CLARO, "Closed Set (explorados)"),
            (MAGENTA, "Camino óptimo"),
            (ROJO, "Objetivo"),
            (AMARILLO, "Jugador")
        ]
        
        for i, (color, desc) in enumerate(colores_leyenda):
            rect = pygame.Rect(leyenda_x, info_y + i * 20, 15, 15)
            pygame.draw.rect(self.ventana, color, rect)
            superficie = self.fuente_pequena.render(desc, True, NEGRO)
            self.ventana.blit(superficie, (leyenda_x + 20, info_y + i * 20))
    
    def dibujar_menu(self):
        self.reproducir_musica_menu()
        
        if self.imagen_menu:
            self.ventana.blit(self.imagen_menu, (0, 0))
            overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            overlay.fill(BLANCO)
            overlay.set_alpha(90) 
            self.ventana.blit(overlay, (0, 0))
        else:
            self.ventana.fill(BLANCO)
        
        titulo = self.fuente_grande.render("Resolvedor de Laberintos A*", True, NEGRO)
        titulo_sombra = self.fuente_grande.render("Resolvedor de Laberintos A*", True, GRIS)
        
        titulo_rect = titulo.get_rect(center=(ANCHO_VENTANA//2, 100))
        sombra_rect = titulo_sombra.get_rect(center=(ANCHO_VENTANA//2 + 2, 102))
        
        self.ventana.blit(titulo_sombra, sombra_rect)
        self.ventana.blit(titulo, titulo_rect)
        
        instrucciones = [
            "BIENVENIDOS"
            "Presiona ESPACIO para resolver con A*",
            "Presiona R para reiniciar",
            "ESC para salir",
            "",
            "El algoritmo A* encuentra el camino más corto",
            "usando una heurística inteligente."
        ]
        
        for i, instruccion in enumerate(instrucciones):
            if instruccion: 
                texto = self.fuente_pequena.render(instruccion, True, NEGRO)
                texto_rect = texto.get_rect(center=(ANCHO_VENTANA//2, 200 + i * 30))
                self.ventana.blit(texto, texto_rect)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                
                elif evento.key == pygame.K_r:
                    self.estado = MENU
                    self.jugador_pos = (1, 1)
                    self.open_set = []
                    self.closed_set = set()
                    self.came_from = {}
                    self.g_score = {}
                    self.camino_optimo = []
                    self.nodos_explorados = []
                    self.solucion_encontrada = False
                    self.tiempo_inicio = 0
                    self.tiempo_fin = 0
                    self.pasos_algoritmo = 0
                    self.nodos_expandidos = 0
                
                elif evento.key == pygame.K_SPACE:
                    if self.estado == MENU:
                        self.estado = RESOLVIENDO
                        self.detener_musica_menu()  
                        self.inicializar_astar()
        
        return True
    
    def actualizar(self):
        if self.estado == RESOLVIENDO:
            for _ in range(2): 
                if not self.paso_astar():
                    if self.solucion_encontrada:
                        self.estado = GANADO
                    else:
                        self.estado = MENU 
                    break
    
    def dibujar(self):
        if self.estado == MENU:
            self.dibujar_menu()
        
        elif self.estado == RESOLVIENDO or self.estado == JUGANDO or self.estado == GANADO:
            self.ventana.fill(GRIS)
            self.dibujar_laberinto()
            self.dibujar_visualizacion_astar()
            self.dibujar_elementos()
            self.dibujar_info()
            
            if self.estado == GANADO:
                mensaje_rect = pygame.Rect(10, 10, 300, 40)
                pygame.draw.rect(self.ventana, VERDE_CLARO, mensaje_rect)
                pygame.draw.rect(self.ventana, NEGRO, mensaje_rect, 2)
                
                mensaje = self.fuente.render("¡Presiona R para reiniciar!", True, NEGRO)
                mensaje_pos = mensaje.get_rect(center=mensaje_rect.center)
                self.ventana.blit(mensaje, mensaje_pos)
        
        pygame.display.flip()
    
    def ejecutar(self):
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)  
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = LaberintoAStar()
    juego.ejecutar()