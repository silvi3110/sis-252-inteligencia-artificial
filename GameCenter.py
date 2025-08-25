import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os

class GameCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("Centro de Juegos")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2c3e50")
        
        self.center_window()
        
        self.bg_color = "#2c3e50"
        self.card_bg = "#34495e"
        self.text_color = "#ecf0f1"
        self.accent_color = "#3498db"
        self.hover_color = "#2980b9"
        self.title_color = "#f39c12"
        
        self.image_references = []
        
        self.create_welcome_screen()
        
    def center_window(self):
        self.root.update_idletasks()
        width = 1000
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_image(self, image_path, size=(80, 80)):
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                print(f"Archivo no encontrado: {image_path}")
                return None
        except Exception as e:
            print(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def create_welcome_screen(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(20, 30))
        
        title_label = tk.Label(title_frame, text="🎮 CENTRO DE JUEGOS", 
                              font=('Arial', 36, 'bold'),
                              bg=self.bg_color, fg=self.title_color)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Selecciona un juego para comenzar", 
                                 font=('Arial', 16), 
                                 bg=self.bg_color, fg=self.text_color)
        subtitle_label.pack(pady=(10, 0))
        
        games_container = tk.Frame(main_frame, bg=self.bg_color)
        games_container.pack(fill=tk.BOTH, expand=True)
        
        games = [
            ("Sudoku", self.open_sudoku, "sudoku_icon.PNG", "Resuelve puzzles numéricos con lógica"),
            ("Puzzle de 8", self.open_puzzle, "puzzle_icon.PNG", "Ordena las piezas en el orden correcto"),
            ("Tres en Raya", self.open_tictactoe, "tictactoe_icon.png", "Clásico juego de estrategia 3 en línea"),
            ("Laberinto", self.open_maze, "maze_icon.png", "Encuentra el camino hacia la salida")
        ]
        
        for i, (game_name, command, icon_path, description) in enumerate(games):
            row = i // 2
            col = i % 2
            
            game_frame = tk.Frame(games_container, bg=self.card_bg, relief=tk.RAISED, 
                                borderwidth=2, cursor="hand2", width=400, height=300)
            game_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            game_frame.grid_propagate(False)
            
            game_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
            game_frame.bind("<Enter>", lambda e, f=game_frame: self.on_enter(f))
            game_frame.bind("<Leave>", lambda e, f=game_frame: self.on_leave(f))
            
            content_frame = tk.Frame(game_frame, bg=self.card_bg)
            content_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            image = self.load_image(icon_path, size=(100, 100))
            if image:
                self.image_references.append(image)
                image_label = tk.Label(content_frame, image=image, bg=self.card_bg)
                image_label.image = image  
                image_label.pack(pady=(0, 15))
                
                image_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                image_label.configure(cursor="hand2")
            else:
                emoji_map = {
                    "Sudoku": "🔢",
                    "Puzzle de 8": "🧩", 
                    "Tres en Raya": "⭕",
                    "Laberinto": "🌀"
                }
                emoji_label = tk.Label(content_frame, text=emoji_map.get(game_name, "🎮"), 
                                      font=('Arial', 48), bg=self.card_bg, fg=self.title_color)
                emoji_label.pack(pady=(0, 15))
                emoji_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                emoji_label.configure(cursor="hand2")
            
            name_label = tk.Label(content_frame, text=game_name, 
                                 font=('Arial', 18, 'bold'), 
                                 bg=self.card_bg, fg=self.text_color)
            name_label.pack()
            
            desc_label = tk.Label(content_frame, text=description, 
                                 font=('Arial', 10), 
                                 bg=self.card_bg, fg=self.text_color, 
                                 wraplength=300, justify=tk.CENTER)
            desc_label.pack(pady=(10, 0))
            
            for widget in content_frame.winfo_children():
                widget.bind("<Button-1>", lambda e, cmd=command: cmd())
                widget.configure(cursor="hand2")
        
        games_container.grid_columnconfigure(0, weight=1)
        games_container.grid_columnconfigure(1, weight=1)
        games_container.grid_rowconfigure(0, weight=1)
        games_container.grid_rowconfigure(1, weight=1)
        
        exit_frame = tk.Frame(main_frame, bg=self.bg_color)
        exit_frame.pack(pady=30)
        
        exit_button = tk.Button(exit_frame, text="Salir", 
                               font=('Arial', 12, 'bold'),
                               bg="#e74c3c", fg="white", 
                               border=0, cursor="hand2",
                               command=self.exit_application,
                               width=15, height=2)
        exit_button.pack()
        exit_button.bind("<Enter>", lambda e: exit_button.config(bg="#c0392b"))
        exit_button.bind("<Leave>", lambda e: exit_button.config(bg="#e74c3c"))
    
    def on_enter(self, frame):
        frame.configure(bg=self.hover_color)
        for child in frame.winfo_children():
            try:
                child.configure(bg=self.hover_color)
                for grandchild in child.winfo_children():
                    try:
                        grandchild.configure(bg=self.hover_color)
                    except:
                        pass
            except:
                pass
    
    def on_leave(self, frame):
        frame.configure(bg=self.card_bg)
        for child in frame.winfo_children():
            try:
                child.configure(bg=self.card_bg)
                for grandchild in child.winfo_children():
                    try:
                        grandchild.configure(bg=self.card_bg)
                    except:
                        pass
            except:
                pass
    
    def show_error_message(self, game_name, error):
        messagebox.showerror(
            "Error", 
            f"No se pudo abrir {game_name}.\n\n"
            f"Error: {str(error)}\n\n"
            f"Verifica que el archivo existe y es ejecutable."
        )
    
    def open_sudoku(self):
        try:
            subprocess.Popen([sys.executable, "sudoku.py"])
        except Exception as e:
            self.show_error_message("Sudoku", e)
    
    def open_puzzle(self):
        try:
            subprocess.Popen([sys.executable, "puzzle.py"])
        except Exception as e:
            self.show_error_message("Puzzle de 8", e)
    
    def open_tictactoe(self):
        try:
            subprocess.Popen([sys.executable, "tres_en_raya.py"])
        except Exception as e:
            self.show_error_message("Tres en Raya", e)
    
    def open_maze(self):
        try:
            subprocess.Popen([sys.executable, "./Laberinto/mainn.py"])
        except Exception as e:
            self.show_error_message("Laberinto", e)
    
    def exit_application(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.root.quit()

def main():
    root = tk.Tk()
    app = GameCenter(root)
    root.mainloop()

if __name__ == "__main__":
    main()