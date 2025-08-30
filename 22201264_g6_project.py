from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys, random, time, math

WINDOW_W, WINDOW_H = 1000, 800
ROWS, COLS = 12, 12             # Grid: 12X12 tiles
TILE_W, TILE_H = 60, 30
PLAY_BOUND_X = (COLS * TILE_W) / 2 - 20
PLAY_BOUND_Y = (ROWS * TILE_H) / 2 - 20

PLAYER_SPEED = 120.0
START_LIFE = 3


player_pos = [-PLAY_BOUND_X+30, 0.0, 20.0]  # slightly inside the left boundary
player_angle = 90
score = 0


keys_down = set()       # set of currently pressed keys
last_time = None

# Extra State
lives = START_LIFE
paused = False
slow_mode = False

# Moving walls
walls = [
    {'x':0,'y':0,'z':20,'dir':1},
    {'x':0,'y':60,'z':20,'dir':-1}
]
WALL_SPEED = 80.0
WALL_LIMIT = 150.0

# Trap tiles (vanishing)
tile_cheat = False
TRAP_COUNT = 10
TRAP_VANISH_TIME = 15.0     # Number of seconds a trap stays visible or invisible
trap_tiles = []

# Invisibility (V cheat)
invisible = False
inv_timer = 0.0            # how long the player has been invisible
INV_DURATION = 5.0


def spawn_traps():         # recreates trap tiles
    global trap_tiles
    trap_tiles = []
    for _ in range(TRAP_COUNT):
        i = random.randint(0, ROWS-1)
        j = random.randint(0, COLS-1)
        trap_tiles.append({
            'i':i,'j':j,
            'vanish':False,
            'timer':random.uniform(5,10)  # start with random delay, controls when each trap vansihes/respawns
        })

def draw_floor():
    half_w = COLS * TILE_W / 2
    half_h = ROWS * TILE_H / 2

    for i in range(ROWS):
        for j in range(COLS):
            is_trap = any(t['i']==i and t['j']==j for t in trap_tiles)    # does a trap exist in (i,j)
            color = None
            if is_trap:
                trap = next(t for t in trap_tiles if t['i']==i and t['j']==j)   # finds the trap dictionary that matches (i,j)
                if trap['vanish']:
                    continue  # vanished tile = hole
                elif trap['timer']<3:
                    color=(1.0,0.0,0.0) # warning red

            if not color:
                color=(0.6,0.6,0.6)

                
def draw_walls():
    glColor3f(0.8,0.2,0.2)
    for w in walls:
        glPushMatrix()
        glTranslatef(w['x'], w['y'], w['z'])
        glScalef(30,10,40)
        glutSolidCube(1)
        glPopMatrix()


def check_collisions():
    global score, game_over, lives
    if invisible:
        return
    
    for w in walls:
        if abs(player_pos[0]-w['x'])<20 and abs(player_pos[1]-w['y'])<20:
            lose_life()

    half_w = COLS*TILE_W/2
    half_h = ROWS*TILE_H/2
    for trap in trap_tiles:
        x0 = -half_w + trap['j']*TILE_W       # bottom-left corner (x0, y0)
        y0 = -half_h + trap['i']*TILE_H
        x1,y1 = x0+TILE_W, y0+TILE_H         # top-right corner (x1, y1)
        if trap['vanish']:
            if (x0<=player_pos[0]<=x1 and y0<=player_pos[1]<=y1):
                game_over=True
                return

def lose_life():
    global lives, game_over, player_pos
    if invisible:   # immune
        return
    lives -= 1
    player_pos=[-PLAY_BOUND_X+30,0,20]
    if lives <= 0:
        game_over = True


def keyboardListener(key,x,y):
    global keys_down
    global tile_cheat, invisible, inv_timer, paused, slow_mode


    k=key.decode('utf-8','ignore').lower()
    if not k: 
        return       
    if key==b't':
        tile_cheat = not tile_cheat
    if key==b'v': 
        invisible = True; inv_timer=0.0
    if key==b'p': 
        paused = not paused
        if not paused:   # just unpaused
            last_time = None
    if key==b'm': 
        slow_mode = not slow_mode
    keys_down.add(k)

def keyboardUp(key,x,y):
    k=key.decode('utf-8','ignore').lower()
    if k in keys_down: keys_down.remove(k)


def idle():
    global last_time, player_pos, player_angle
    global paused, inv_timer, invisible
    global lives, game_over


    now=time.time()
    dt=(now-last_time) if last_time else 1/60.0   # If last_time is not set yet (first frame), it defaults to 1/60.0
    last_time=now

    if paused:
        last_time = time.time()   # keep syncing time while paused 
        return 

    if slow_mode: dt *= 0.3

    if invisible:
        inv_timer += dt
        if inv_timer >= INV_DURATION:
            invisible=False
            inv_timer=0.0

    for w in walls:
        w['y'] += w['dir']*WALL_SPEED*dt    # Moves wall along Y-axis
        if abs(w['y'])>WALL_LIMIT:        # if wall goes beyond the boundary, flip the direction
            w['dir']*=-1
    
    for trap in trap_tiles:
        if not tile_cheat:   # freeze traps if tile_cheat is True
            trap['timer'] -= dt
            if trap['timer'] <= 0:
                trap['vanish'] = not trap['vanish']    # if it was visible, it becomes invisible, and vice versa
                trap['timer'] = TRAP_VANISH_TIME

        check_collisions()

    glutPostRedisplay()

def showScreen():
    global score, lives

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,WINDOW_W,WINDOW_H)
    
    draw_walls()


def main():

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W,WINDOW_H)
    glutInitWindowPosition(50,50)
    glutCreateWindow(b"Operation Locker Loot - Safe Mode")
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUp)
    glutMainLoop()


if __name__=="__main__":
    main()