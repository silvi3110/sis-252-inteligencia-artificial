import pygame as pg
from functools import lru_cache
import random

# ---------- Paleta (Pastel Cute) ----------
C = {
    'bg':     (250, 248, 255),   # lavanda muy claro (fondo)
    'surf':   (226, 233, 255),   # periwinkle suave (tarjetas/botón grande)
    'pill':   (235, 246, 252),   # celeste-menta muy claro (chips/estado)
    'text':   (45, 55, 72),      # slate oscuro texto principal
    'muted':  (114, 125, 148),   # slate medio labels

    'grid':   (108, 162, 156),   # verde azulado suave (líneas tablero)
    'board':  (195, 246, 228),   # menta pastel (TABLERO)
    'neon':   (120, 255, 210),   # línea victoria (pastel brillante)

    'X':      (255, 150, 170),   # rosa pastel para X y títulos
    'O':      (160, 200, 255),   # celeste pastel para O
    'accent': (180, 190, 255),   # borde activo de píldoras

    # Fondo del cartel de resultado — distinto al del tablero
    'banner': (255, 235, 250),   # rosa/lila pastel

    # Lila más CLARO para CTAs (reiniciar / resetear)
    'cta_fg': (170, 164, 255),

    # Rosa de texto un poquito más intenso para que destaque sobre el banner
    'title_pink': (235, 120, 160),
}

# ---------- Bitboards & combinatoria ----------
WINS=[0b111000000,0b000111000,0b000000111,
      0b100100100,0b010010010,0b001001001,
      0b100010001,0b001010100]
LINES=[(0,1,2),(3,4,5),(6,7,8),
       (0,3,6),(1,4,7),(2,5,8),
       (0,4,8),(2,4,6)]
CORNERS=[0,2,6,8]; SIDES=[1,3,5,7]; CENTER=4
RC=[(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]
OPPOSITE={0:8,1:7,2:6,3:5,4:4,5:3,6:2,7:1,8:0}

def win(m): return any((m&w)==w for w in WINS)   # Verifica si un jugador ganó
def full(xm,om): return (xm|om)&0x1FF==0x1FF     # Revisa si el tablero está lleno
def popcnt(n): return n.bit_count()    # Cuenta cuántos bits están en 1
def marks(xm,om): return popcnt(xm|om)    # Retorna el número total de jugadas (X + O)

def forced_move(xm,om,turn):
    # Busca si hay una jugada obligada (para ganar o bloquear)
    me,op=(xm,om) if turn=='X' else (om,xm)
    empty=~(me|op)&0x1FF
    # ganar
    for w in WINS:
        need=w&~me
        if (need&empty) and popcnt(me&w)==2 and (op&w)==0:
            for i in range(9):
                if need&(1<<i): return i
    # bloquear
    for w in WINS:
        need=w&~op
        if (need&empty) and popcnt(op&w)==2 and (me&w)==0:
            for i in range(9):
                if need&(1<<i): return i
    return None

def count_imminent_wins(me,op):
    # Cuenta cuántas jugadas me darían victoria inmediata
    cnt=0
    for a,b,c in LINES:
        w=(1<<a)|(1<<b)|(1<<c)
        if (op&w)==0 and (me&w) and popcnt(me&w)==2:
            cnt+=1
    return cnt

def fork_move(me,op):
    # Intenta crear un "fork": dos amenazas de ganar a la vez
    empty=~(me|op)&0x1FF
    for i in range(9):
        if empty&(1<<i) and count_imminent_wins(me|(1<<i),op)>=2:
            return i
    return None

def block_fork(me,op):
        # Detecta si el rival puede hacer un fork y lo bloquea
    empty=~(me|op)&0x1FF
    forks=[i for i in range(9) if empty&(1<<i) and count_imminent_wins(op|(1<<i),me)>=2]
    if len(forks)==1: return forks[0]
    for i in range(9):
        if empty&(1<<i) and count_imminent_wins(me|(1<<i),op)>=1:
            return i
    return None

@lru_cache(None)
def negamax(me,op,alpha=-1,beta=1):
    if win(op): return -1
    if (me|op)==0x1FF: return 0
    best=-2; empty=~(me|op)&0x1FF
    order=[4,0,2,6,8,1,3,5,7]
    for i in order:
        if empty&(1<<i):
            v=-negamax(op,me|(1<<i),-beta,-alpha)
            if v>best: best=v
            if best>alpha: alpha=best
            if alpha>=beta: break
    return best

def best_move(xm,om,x_turn=True):
    # Calcula la mejor jugada usando Negamax (elige la de mayor valor)
    me,op=(xm,om) if x_turn else (om,xm)
    empty=~(me|op)&0x1FF; best=-2; mv=None
    order=[4,0,2,6,8,1,3,5,7]
    for i in order:
        if empty&(1<<i):
            v=-negamax(op,me|(1<<i))
            if v>best: best,mv=v,i
    return mv

def manhattan(i,j):
    # Calcula distancia Manhattan entre dos casillas del tablero
    (r1,c1),(r2,c2)=RC[i],RC[j]
    return abs(r1-r2)+abs(c1-c2)

# ---------- Libro de aperturas (naturalidad) ----------
def opening_choice(diff):
    # Decide jugada de apertura según dificultad (easy, medium, hard)
    r=random.random()
    if diff=='easy':
        if r<0.55: return random.choice(SIDES)
        if r<0.90: return random.choice(CORNERS)
        return CENTER
    if diff=='medium':
        if r<0.40: return CENTER
        if r<0.90: return random.choice(CORNERS)
        return random.choice(SIDES)
    return CENTER if r<0.50 else random.choice(CORNERS)

def book_move(xm,om,turn,diff,last_h):
    # “Libro de aperturas”: jugadas típicas iniciales según dificultad
    me,op=(xm,om) if turn=='X' else (om,xm)
    n=marks(xm,om)
    empty=~(me|op)&0x1FF
    if n==0:
        return opening_choice(diff)
    if n==1 and last_h is not None:
        if last_h==CENTER:
            if diff=='easy':
                pool=[i for i in SIDES if empty&(1<<i)] or [i for i in range(9) if empty&(1<<i)]
                return random.choice(pool) if pool else None
            pool=[i for i in CORNERS if empty&(1<<i)]
            if pool: return random.choice(pool)
        if last_h in CORNERS:
            if diff=='easy' and random.random()<0.5:
                pool=[i for i in (SIDES+CORNERS) if empty&(1<<i)]
                return random.choice(pool) if pool else None
            if empty&(1<<CENTER): return CENTER
        if last_h in SIDES:
            if diff=='easy' and random.random()<0.6:
                opp=OPPOSITE[last_h]
                return opp if empty&(1<<opp) else (CENTER if empty&(1<<CENTER) else None)
            if empty&(1<<CENTER): return CENTER
    if n==2:
        if (me&(1<<CENTER)) and any(op&(1<<c) for c in CORNERS):
            for c in CORNERS:
                if op&(1<<c):
                    oc=OPPOSITE[c]
                    if empty&(1<<oc): return oc
        my_corners=[c for c in CORNERS if me&(1<<c)]
        if my_corners and (op&(1<<CENTER)):
            oc=OPPOSITE[my_corners[0]]
            if empty&(1<<oc): return oc
        if any(op&(1<<a) for a in CORNERS) and any(op&(1<<OPPOSITE[a]) for a in CORNERS):
            if me&(1<<CENTER):
                sides=[i for i in SIDES if empty&(1<<i)]
                if sides: return random.choice(sides)
    return None

# ---------- IA principal ----------
def ai_pick(xm,om,turn,diff,last_h=None):
    # Decide el movimiento de la IA según dificultad
    me,op=(xm,om) if turn=='X' else (om,xm)
    empty=~(me|op)&0x1FF
    moves=[i for i in range(9) if empty&(1<<i)]
    n=marks(xm,om)

    # Jugadas de apertura (inicio de partida)
    if diff!='easy':
        bm=book_move(xm,om,turn,diff,last_h)
        if bm is not None and (empty&(1<<bm)): return bm
    else:
        if n==0:
            return opening_choice(diff)

    # Movimiento forzado: ganar o bloquear
    fm=forced_move(xm,om,turn)
    if fm is not None:
        if diff=='easy' and random.random()<0.65:
            pass
        else:
            return fm

    # Buscar fork (dos formas de ganar) o bloquear fork del rival
    if diff!='easy':
        mv=fork_move(me,op)
        if mv is not None: return mv
        if not (diff=='medium' and random.random()<0.20):
            mv=block_fork(me,op)
            if mv is not None: return mv

    # Función para puntuar casillas según centro/esquinas/lados y amenazas
    def score(i):
        if not (empty&(1<<i)): return -999
        s=0.0
        s += 3.0 if i==CENTER else 2.2 if i in CORNERS else 1.0
        if last_h is not None:
            d=manhattan(i,last_h)
            s += d*0.9
            if d==1: s -= 1.2
            if last_h in CORNERS and OPPOSITE[last_h]==i:
                s += 1.0
        threats=count_imminent_wins(me|(1<<i),op)
        s += threats*1.8
        if count_imminent_wins(op|(1<<i),me)>=2: s -= 3.0
        return s

    # Estrategias según nivel de dificultad
    if diff=='easy':
        # Juega casi aleatorio, con algo de lógica
        if random.random()<0.85:
            if last_h is not None:
                neigh=[i for i in moves if manhattan(i,last_h)==1]
                sides=[i for i in moves if i in SIDES]
                far  =[i for i in moves if manhattan(i,last_h)>=2]
                for pool,prob in [(neigh,0.50),(sides,0.50),(far,0.35),(moves,1.00)]:
                    if pool and random.random()<prob: return random.choice(pool)
            return random.choice(moves) if moves else None
        bm=best_move(xm,om,turn=='X')
        return bm if bm is not None else (random.choice(moves) if moves else None)

    if diff=='medium':
        # Combina Negamax con jugadas menos óptimas para parecer humano
        if random.random()<0.60:
            bm=best_move(xm,om,turn=='X')
            if bm is not None: return bm
        scored=[(score(i),i) for i in moves]
        if not scored: return None
        best=max(scored)[0]
        pool=[i for s,i in scored if s>=best-0.40]
        if len(pool)>=2 and random.random()<0.35:
            pool=pool[:-1]
        return random.choice(pool) if pool else max(scored)[1]
    
    # Difícil → usa Negamax puro (casi invencible)
    bm=best_move(xm,om,turn=='X')
    if bm is not None: return bm
    scored=[(score(i),i) for i in moves]
    return max(scored)[1] if scored else None

def win_mask(mask):
    # Revisa si hay línea ganadora y devuelve su máscara
    for w in WINS:
        if (mask&w)==w: return w
    return 0

# ---------- Fuentes ----------
def choose_font():
    # Elige una fuente bonita entre las disponibles
    prefer = ['quicksand','nunito','rubik','mulish','comfortaa','fredoka',
              'poppins','segoeui','roboto','arial']
    avail=set(pg.font.get_fonts())
    for n in prefer:
        if n in avail: return n
    return None

def make_fonts(w):
    # Ajusta tamaños de letra según ancho de la ventana
    base=max(12,int(min(w,1300)*0.013))
    name=choose_font()
    return {
        'sm':pg.font.SysFont(name,int(base*1.05)),
        'rg':pg.font.SysFont(name,int(base*1.38)),
        'sb':pg.font.SysFont(name,int(base*1.62),bold=True),
        'lg':pg.font.SysFont(name,int(base*2.45),bold=True),
        'xl':pg.font.SysFont(name,int(base*4.05),bold=True),
    }
def T(font,msg,color): return font.render(msg,True,color)     # Renderiza un texto en pantalla

# ---------- Estado ----------
class State:
    # Clase que guarda todo el estado del juego
    def __init__(self):
        self.diff='medium'; self.human='X'; self.turn='X' # qué ficha usa el jugador # de quién es el turno
        self.xm=0; self.om=0; self.over=False; self.wmask=0
        self.wait=False; self.scores={'W':0,'D':0,'L':0}
        self.status="Comienza la partida o elige jugador."
        self.last_h=None
S=State()

# ---------- Pygame ----------
pg.init()
pg.display.set_caption("Tic-Tac-Toe — Pastel Cute (Responsive)")
info=pg.display.Info()
W0=min(1280,int(info.current_w*0.9))
H0=min(800,  int(info.current_h*0.9))
screen=pg.display.set_mode((W0,H0), pg.RESIZABLE|pg.HWSURFACE|pg.DOUBLEBUF)
F=make_fonts(W0)

MARGIN=24
# Dibuja rectángulos con bordes redondeados (usado en botones/tablero)
def rrect(s,color,rect,r=16,w=0): pg.draw.rect(s,color,rect,w,border_radius=r)

# ---------- Layout (mismo margen arriba/abajo, tres gaps iguales g) ----------
def relayout():
    """
    Mantiene el mismo margen exterior arriba y abajo (=MARGIN).
    Entre SCORE → TABLERO → ESTADO → BOTÓN hay tres gaps iguales g.
    """
    global TOP, SCORE, BOARD, STAT, BTN
    w, h = screen.get_size()
    F.update(make_fonts(w)) # recalcula fuentes si se cambia tamaño

    row_h = max(64, int(h * 0.09))
    TOP   = pg.Rect(MARGIN, MARGIN, w - 2 * MARGIN, row_h)
    SCORE = pg.Rect(MARGIN, TOP.bottom + 10, w - 2 * MARGIN, row_h - 8)

    stat_h = 30
    btn_h  = 44
    GAP_MIN = 18
    MIN_SIDE = 360

    side_by_w = min(int(w * 0.80), w - 2 * MARGIN)
    span = (h - MARGIN) - SCORE.bottom
    max_side_by_h = span - (stat_h + btn_h) - 3 * GAP_MIN
    side = max(MIN_SIDE, min(side_by_w, max_side_by_h))
    g = int(max(GAP_MIN, (span - side - stat_h - btn_h) / 3.0))

    BOARD = pg.Rect(0, SCORE.bottom + g, side, side); BOARD.centerx = w // 2
    STAT  = pg.Rect(0, BOARD.bottom + g, min(280, int(w * 0.35)), stat_h); STAT.centerx = w // 2
    BTN   = pg.Rect(0, STAT.bottom + g, min(560, int(w * 0.70)), btn_h);    BTN.centerx  = w // 2

relayout()

# ---------- Dibujo ----------
def draw_pill_text(s, rect, text, active=False):
    # Dibuja un botón tipo píldora con texto
    rrect(s, C['pill'], rect, 18)
    if active: pg.draw.rect(s, C['accent'], rect, 2, 18)
    img=T(F['rg'], text, C['text'])
    s.blit(img, img.get_rect(center=rect.center))

def draw_top(s):
    # Dibuja barra superior con dificultad y selección de X/O
    labels=[("Fácil","easy"),("Medio","medium"),("Imposible","hard")]
    symbs =["X","O"]
    def pill_w(txt,pad=22): return T(F['rg'],txt,C['text']).get_width()+pad*2

    items_w = sum(pill_w(n) for n,_ in labels) + 10*(len(labels)-1)
    items_w += 10 + sum(pill_w(sym,18) for sym in symbs)

    start_x = TOP.centerx - items_w//2
    y = TOP.y + (TOP.h-34)//2

    rrect(s, C['surf'], TOP, 16)
    s.blit(T(F['sm'],"Nivel",C['muted']), (TOP.x+14, TOP.y+8))

    pills=[]; x=start_x
    for name,val in labels:
        w=pill_w(name); rr=pg.Rect(x,y,w,34); draw_pill_text(s, rr, name, S.diff==val)
        pills.append((rr,('diff',val))); x+=w+10
    x+=10
    for sym in symbs:
        w=pill_w(sym,18); rr=pg.Rect(x,y,w,34); draw_pill_text(s, rr, sym, S.human==sym)
        pills.append((rr,('human',sym))); x+=w+10
    return pills

def draw_score(s):
    # Dibuja marcador de partidas (ganadas, empatadas, perdidas)
    rrect(s, C['surf'], SCORE, 16)
    y_center = SCORE.y + SCORE.h//2
    entries=[]
    for lbl,key in [("Ganadas:",'W'),("Empates:",'D'),("Perdidas:",'L')]:
        t_lbl=T(F['rg'],lbl,C['muted'])
        val =T(F['rg'],str(S.scores[key]),C['text'])
        chip_w = max(46, val.get_width()+18)
        entries.append((t_lbl, chip_w, val))
    gap=22
    group_w = sum(t.get_width()+chip_w+gap for t,chip_w,_ in entries)-gap
    gx = SCORE.centerx - group_w//2
    py = y_center-14
    for t_lbl, chip_w, val in entries:
        s.blit(t_lbl, (gx, py+2))
        rr=pg.Rect(gx+t_lbl.get_width()+6, py-2, chip_w, 28)
        rrect(s, C['pill'], rr, 14)
        s.blit(val, val.get_rect(center=rr.center))
        gx = rr.right + gap
    rr=pg.Rect(SCORE.right-120, y_center-14, 100, 28)
    rrect(s, C['pill'], rr, 14)
    lab=T(F['rg'],"RESETEAR",C['cta_fg'])  # mismo lila del CTA
    s.blit(lab, lab.get_rect(center=rr.center))
    return rr

def draw_board(s):
    # Dibuja tablero y las fichas (X y O)
    rrect(s, C['board'], BOARD, 18)
    step=BOARD.w//3; g=max(6,BOARD.w//170)
    for i in range(1,3):
        pg.draw.line(s,C['grid'],(BOARD.left+i*step,BOARD.top),(BOARD.left+i*step,BOARD.bottom),g)
        pg.draw.line(s,C['grid'],(BOARD.left,BOARD.top+i*step),(BOARD.right,BOARD.top+i*step),g)
    pad=int(step*0.18); thickX=max(12,step//10); thickO=max(14,step//12)
    for i in range(9):
        cx=BOARD.left+(i%3)*step; cy=BOARD.top+(i//3)*step
        cell=pg.Rect(cx,cy,step,step)
        if S.xm&(1<<i):
            pg.draw.line(s,C['X'],(cell.left+pad,cell.top+pad),(cell.right-pad,cell.bottom-pad),thickX)
            pg.draw.line(s,C['X'],(cell.right-pad,cell.top+pad),(cell.left+pad,cell.bottom-pad),thickX)
        elif S.om&(1<<i):
            pg.draw.circle(s,C['O'],cell.center,cell.w//2-pad,thickO)

# ---------- Línea ganadora (mapeo correcto) ----------
def neon_line(s,mask):
    # Dibuja la línea brillante cuando alguien gana
    if mask == 0: return
    step = BOARD.w // 3
    glow, core = 18, 10
    col = C['neon']

    # Filas (arriba→abajo)
    if   mask == 0b000000111: y = BOARD.top + step//2
    elif mask == 0b000111000: y = BOARD.top + 3*step//2
    elif mask == 0b111000000: y = BOARD.top + 5*step//2
    else: y = None
    if y is not None:
        a=(BOARD.left-24, y); b=(BOARD.right+24, y)
        pg.draw.line(s,col,a,b,glow); pg.draw.line(s,col,a,b,core); return

    # Columnas (izquierda→derecha)
    if   mask == 0b001001001: x = BOARD.left + step//2
    elif mask == 0b010010010: x = BOARD.left + 3*step//2
    elif mask == 0b100100100: x = BOARD.left + 5*step//2
    else: x = None
    if x is not None:
        a=(x, BOARD.top-24); b=(x, BOARD.bottom+24)
        pg.draw.line(s,col,a,b,glow); pg.draw.line(s,col,a,b,core); return

    # Diagonales
    if   mask == 0b100010001:
        a=(BOARD.left-24,  BOARD.top-24)
        b=(BOARD.right+24, BOARD.bottom+24)
    else:  # 0b001010100
        a=(BOARD.right+24, BOARD.top-24)
        b=(BOARD.left-24,  BOARD.bottom+24)
    pg.draw.line(s,col,a,b,glow); pg.draw.line(s,col,a,b,core)

def draw_bottom(s):
    # Dibuja el cuadro inferior con el estado (tu turno, pensando, finalizado)
    rrect(s, C['pill'], STAT, 14)
    lab=T(F['rg'],S.status,C['text'])
    s.blit(lab, lab.get_rect(center=STAT.center))
    rrect(s, C['surf'], BTN, 18)
    lab2=T(F['sb'],"REINICIAR PARTIDA",C['cta_fg'])
    s.blit(lab2, lab2.get_rect(center=BTN.center))

def draw_banner(s,kind):
    # Dibuja un cartel grande en el centro cuando hay empate o victoria
    box=pg.Rect(0,0,min(560,int(screen.get_width()*0.9)),210); box.center=(screen.get_width()//2,BOARD.centery)
    rrect(s, C['banner'], box, 20)
    TX=T(F['xl'],"X",C['X']); TO=T(F['xl'],"O",C['O'])
    # MÁS UNIDOS: gap reducido de 34px → 24px
    gap = 24
    s.blit(TX,TX.get_rect(midright=(box.centerx-gap,box.centery-8)))
    s.blit(TO,TO.get_rect(midleft =(box.centerx+gap,box.centery-8)))
    msg="¡EMPATE!" if kind=='D' else "¡GANADOR!"
    # Ahora EMPATE también va en rosa y con un tono que resalta sobre el banner
    title_col = C['title_pink']
    lab=T(F['sb'],msg,title_col)
    s.blit(lab, lab.get_rect(center=(box.centerx,box.centery+58)))

# ---------- Juego ----------
def cell_at(pos):
    # Convierte un click del mouse en la celda del tablero (0-8)
    if not BOARD.collidepoint(pos): return None
    step=BOARD.w//3
    c=(pos[0]-BOARD.left)//step; r=(pos[1]-BOARD.top)//step
    i=int(r*3+c); return i if 0<=i<=8 else None

def mark(i,ch):
    # Marca la celda 'i' con la ficha 'ch' (X o O) si está libre
    if (S.xm|S.om)&(1<<i): return False
    if ch=='X': S.xm|=(1<<i)
    else:       S.om|=(1<<i)
    return True

def win_mask_for_current():
    # Revisa si X u O tienen una línea ganadora y devuelve la máscara
    wx=win_mask(S.xm); wo=win_mask(S.om)
    return wx if wx else wo

def finish():
    # Verifica si terminó la partida:
    S.wmask=win_mask_for_current()
    if S.wmask:
        S.over=True
        if S.turn=='X': S.scores['W']+=1
        else:           S.scores['L']+=1
        S.status="Juego finalizado"; return True
    if full(S.xm,S.om):
        S.over=True; S.scores['D']+=1; S.status="Juego finalizado"; return True
    return False

AI_EVENT=pg.USEREVENT+1
def ask_ai():
    # Activa un temporizador → simula que la IA "piensa"
    if S.over: return
    S.status="Pensando…"; S.wait=True; pg.time.set_timer(AI_EVENT,700,True)

def ai_turn():
    # Juega el turno de la IA usando la función ai_pick()
    if S.over: S.wait=False; return
    mv=ai_pick(S.xm,S.om,S.turn,S.diff,S.last_h)
    if mv is None: S.wait=False; return
    if mark(mv,S.turn):
        if finish(): S.wait=False; return
        S.turn='O' if S.turn=='X' else 'X'; S.status="Tu turno."
    S.wait=False

def new_match():
    # Reinicia todo para comenzar una nueva partida
    S.xm=S.om=0; S.over=False; S.wmask=0; S.last_h=None
    negamax.cache_clear()
    S.turn='X'; S.status="Tu turno." if S.human=='X' else "Pensando…"
    if S.human=='O': ask_ai()

# ---------- Main loop ----------
def main(): # prepara layout y arranca partida nueva
    relayout(); new_match()
    clk=pg.time.Clock(); run=True
    while run:
        for e in pg.event.get(): # Manejo de eventos (cerrar, click, resize)
            if e.type==pg.QUIT: run=False
            elif e.type==pg.VIDEORESIZE: # si cambia tamaño ventana → reacomoda layout
                w=max(900,e.w); h=max(680,e.h)
                pg.display.set_mode((w,h), pg.RESIZABLE|pg.HWSURFACE|pg.DOUBLEBUF)
                relayout()
            elif e.type==pg.MOUSEBUTTONDOWN and e.button==1:
                pos=e.pos
                pills=draw_top(screen)  # hitboxes actuales
                for r,info in pills:
                    if r.collidepoint(pos):
                        typ,val=info
                        if   typ=='diff':   S.diff=val
                        elif typ=='human':  S.human=val; new_match()
                        break
                # botón reset
                y_center=SCORE.y+SCORE.h//2
                reset_rect=pg.Rect(SCORE.right-120, y_center-14, 100, 28)
                if reset_rect.collidepoint(pos): S.scores={'W':0,'D':0,'L':0}

                i=cell_at(pos)
                if i is not None and not S.over and not S.wait and S.turn==S.human:
                    if mark(i,S.turn):
                        S.last_h=i
                        if finish(): pass
                        else:
                            S.turn='O' if S.turn=='X' else 'X'; ask_ai()
                if BTN.collidepoint(pos): new_match()
            elif e.type==AI_EVENT:
                ai_turn() # ejecuta jugada de la IA después del "pensando"

        # render
        screen.fill(C['bg'])
        draw_top(screen); draw_score(screen); draw_board(screen); draw_bottom(screen)

        if S.over:  # si la partida terminó → mostrar línea ganadora o empate
            neon_line(screen, S.wmask)            # debajo
            draw_banner(screen,'D' if (S.wmask==0) else S.turn)  # encima

        pg.display.flip(); clk.tick(60) # actualiza la ventana
    pg.quit()

if __name__=="__main__":
    main() # punto de entrada del programa