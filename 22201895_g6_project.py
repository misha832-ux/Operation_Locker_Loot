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

TREASURE_COUNT = 15
LOCKER_SCORE = 100


player_pos = [-PLAY_BOUND_X+30, 0.0, 20.0]  # slightly inside the left boundary
player_angle = 90
score = 0
mission_complete = False
locker_visible = False

treasures = []
locker_pos = [0.0, 0.0, 20.0]
lasers = []

keys_down = set()       # set of currently pressed keys
last_time = None


# Laser on/off
laser_on = True
laser_timer = 0.0
LASER_INTERVAL = 2.0  # lasers blink every 2 seconds

laser_forced_off = False   # if True, disables all lasers
laser_forced_timer = 0.0      # counts how long lasers are off
LASER_FORCED_DURATION = 10.0  # 10 seconds vanish


def deg_to_rad(d): return d * math.pi / 180.0
def player_forward_xy():
    rad = deg_to_rad(player_angle)
    dx = math.sin(rad)
    dy = math.cos(rad)
    return dx, dy

def spawn_treasures():            # recreates treasures
    global treasures
    treasures = []
    half_w = COLS * TILE_W / 2 - 50
    half_h = ROWS * TILE_H / 2 - 50
    for _ in range(TREASURE_COUNT):
        x = random.uniform(-half_w, half_w)
        y = random.uniform(-half_h, half_h)
        big = random.random() < 0.3             # big=True, 30% treasures will be big
        treasures.append({'pos':[x,y,20.0],'big':big,'collected':False})

def setup_lasers():
    global lasers
    lasers = []
    half_w = COLS * TILE_W / 2
    for n in range(3, COLS, 3):         # lasers are placed after every 3 columns
        x = -half_w + n*TILE_W
        for offset in range(-20, 21, 10):
            lasers.append({'y0': PLAY_BOUND_Y+5, 'x': x+offset})
            lasers.append({'y0': -PLAY_BOUND_Y-5, 'x': x+offset})


def draw_floor():
    half_w = COLS * TILE_W / 2
    half_h = ROWS * TILE_H / 2

    # for i in range(ROWS):
    #     for j in range(COLS):
    #         is_trap = any(t['i']==i and t['j']==j for t in trap_tiles)    # does a trap exist in (i,j)
    #         color = None
    #         if is_trap:
    #             trap = next(t for t in trap_tiles if t['i']==i and t['j']==j)   # finds the trap dictionary that matches (i,j)
    #             if trap['vanish']:
    #                 continue  # vanished tile = hole
    #             elif trap['timer']<3:
    #                 color=(1.0,0.0,0.0) # warning red

    #         if not color:
    #             color=(0.6,0.6,0.6)

    x0 = -half_w + j*TILE_W
    x1 = x0 + TILE_W
    y0 = -half_h + i*TILE_H
    y1 = y0 + TILE_H

    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x0,y0,0)
    glVertex3f(x1,y0,0)
    glVertex3f(x1,y1,0)
    glVertex3f(x0,y1,0)
    glEnd()

def draw_bank_walls():
    half_w = COLS * TILE_W / 2
    half_h = ROWS * TILE_H / 2
    wall_h = 100   # taller bank walls
    t = 20         # thickness

    glColor3f(0.4,0.4,0.4)

    # Back wall
    glPushMatrix()
    glTranslatef(0, half_h+t/2, wall_h/2)
    glScalef(half_w*2+t*2, t, wall_h)
    glutSolidCube(1)
    glPopMatrix()

    # Front wall
    glPushMatrix()
    glTranslatef(0, -half_h-t/2, wall_h/2)
    glScalef(half_w*2+t*2, t, wall_h)
    glutSolidCube(1)
    glPopMatrix()

    # Left wall
    glPushMatrix()
    glTranslatef(-half_w-t/2, 0, wall_h/2)
    glScalef(t, half_h*2+t*2, wall_h)
    glutSolidCube(1)
    glPopMatrix()

    # Right wall
    glPushMatrix()
    glTranslatef(half_w+t/2, 0, wall_h/2)
    glScalef(t, half_h*2+t*2, wall_h)
    glutSolidCube(1)
    glPopMatrix()

    # Draw black grid lines above the walls
    glColor3f(0.1,0.1,0.1)
    glLineWidth(2)
    glBegin(GL_LINES)
    # vertical lines
    for x in range(-int(half_w), int(half_w)+1, 60):
        glVertex3f(x, -half_h, wall_h)
        glVertex3f(x, half_h, wall_h)
    # horizontal lines
    for y in range(-int(half_h), int(half_h)+1, 60):
        glVertex3f(-half_w, y, wall_h)
        glVertex3f(half_w, y, wall_h)
    glEnd()

def draw_vault_door():
    half_w = COLS * TILE_W / 2
    wall_h = 80  # door height

    # Door base (big steel rectangle)
    glPushMatrix()
    glTranslatef(-half_w-5, 0, wall_h/2)  # position at left wall center
    glScalef(5, 80, wall_h)  # thin but tall
    glColor3f(0.7, 0.7, 0.7)  
    glutSolidCube(1.0)
    glPopMatrix()

    # Vault circular plate
    glPushMatrix()
    glTranslatef(-half_w-3, 0, 40)  # in the middle of door
    glColor3f(0.85, 0.85, 0.85)  
    glutSolidSphere(15, 30, 30)
    glPopMatrix()

    # Handle (small black knob)
    glPushMatrix()
    glTranslatef(-half_w-1, 0, 40)
    glColor3f(0, 0, 0)
    glutSolidSphere(3, 15, 15)
    glPopMatrix()


def draw_thief():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0.0, 0.0, 1.0)

    # Head
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 35.0)
    glutSolidSphere(6.0, 20, 20)
    glPopMatrix()

    # Body
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 20.0)
    glScalef(6.0, 6.0, 18.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Arms
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(-6.0, 0.0, 22.0)
    glScalef(2.0, 2.0, 10.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(6.0, 3.0, 22.0)
    glScalef(2.0, 2.0, 10.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Legs
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(-3.0, 0.0, 8.0)
    glScalef(2.0, 2.0, 10.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(3.0, 0.0, 8.0)
    glScalef(2.0, 2.0, 10.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Bag
    glColor3f(0.5, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(-4.0, -5.0, 28.0)
    glutSolidSphere(5.0, 20, 20)
    glPopMatrix()

    glPopMatrix()
                  
def draw_treasure(t):
    if t['collected']: return
    glPushMatrix()
    glTranslatef(t['pos'][0],t['pos'][1],t['pos'][2])
    glColor3f(1,0.84,0) if t['big'] else glColor3f(1,0.6,0)
    glutSolidCube(14 if t['big'] else 8)
    glPopMatrix()

def draw_lasers():
    if laser_forced_off:
        return
    for L in lasers:
        glPushMatrix()
        glTranslatef(L['x'], L['y0'], 5)
        glColor3f(0.3,0.3,0.3)
        glutSolidCube(5)
        glPopMatrix()
        if laser_on:
            glColor3f(1.0,0.0,0.0)
            glBegin(GL_LINES)
            glVertex3f(L['x'], L['y0'], 5)
            glVertex3f(L['x'], -L['y0'], 5)
            glEnd()

def draw_locker():
    half_w = COLS * TILE_W / 2 - 30
    locker_pos[0] = half_w
    locker_pos[1] = 0

    glPushMatrix()
    glTranslatef(locker_pos[0], locker_pos[1], locker_pos[2])
    glColor3f(0.0, 1.0, 0.0)
    glPushMatrix()
    glScalef(20.0, 20.0, 30.0)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(6.0, 0.0, 10.0)
    glutSolidSphere(2.0, 12, 12)
    glPopMatrix()
    glPopMatrix()


def check_collisions():
    global score, locker_visible, game_over, lives
    if invisible:
        return
    for t in treasures:
        if not t['collected']:
            if math.hypot(player_pos[0]-t['pos'][0], player_pos[1]-t['pos'][1])<20:   # If the player is within 20 units of the treasure
                t['collected']=True         # player collects the treasure
                score += 20 if t['big'] else 10
                if score >= LOCKER_SCORE and not locker_visible:
                    locker_visible = True             # locker will pop up
                    half_w = COLS * TILE_W / 2 - 30
                    locker_pos[0] = half_w
                    locker_pos[1] = 0
    if locker_visible:
      if math.hypot(player_pos[0]-locker_pos[0],player_pos[1]-locker_pos[1])<25:   # If the player is within 25 units of the locker
        global mission_complete                   
        mission_complete = True             # mission complete
        game_over = True


    if laser_on and not laser_forced_off:          # if laser active
        for L in lasers:
            if abs(player_pos[0]-L['x'])<5 and abs(player_pos[1])<abs(L['y0']):
                lose_life()


def lose_life():
    global lives, game_over, player_pos
    if invisible:   # immune
        return
    lives -= 1
    player_pos=[-PLAY_BOUND_X+30,0,20]
    if lives <= 0:
        game_over = True


def keyboardListener(key,x,y):
    global keys_down, laser_forced_off, laser_forced_timer
    global tile_cheat, invisible, inv_timer, paused, slow_mode
    global camera_follow_player, camera_distance, camera_angle_x, camera_angle_y

    k=key.decode('utf-8','ignore').lower()
    if not k: 
        return
    if key==b'r': 
        restart_game()
    if key==b'l':
        laser_forced_off = True        # Disables laser
        laser_forced_timer = 0.0        
    
    keys_down.add(k)

def keyboardUp(key,x,y):
    k=key.decode('utf-8','ignore').lower()
    if k in keys_down: keys_down.remove(k)


def idle():
    global last_time, player_pos, player_angle, laser_on, laser_timer
    global laser_forced_off, laser_forced_timer
    global inv_timer, invisible
    global lives, game_over
    global game_time, time_up
    global camera_angle_y, camera_angle_x

    now=time.time()
    dt=(now-last_time) if last_time else 1/60.0   # If last_time is not set yet (first frame), it defaults to 1/60.0
    last_time=now

    
    
    laser_timer += dt
    if laser_timer >= LASER_INTERVAL:   # laser_on is flipped & timer is reset
        laser_on = not laser_on
        laser_timer = 0.0

    if laser_forced_off:            # if true (Laser disabled)
        laser_forced_timer += dt
        if laser_forced_timer >= LASER_FORCED_DURATION:
            laser_forced_off = False
            laser_forced_timer = 0.0

    if not game_over:
        angle_rad = math.radians(player_angle)
        dir_x =  math.sin(angle_rad)
        dir_y =  -math.cos(angle_rad)

        # Forward (W)
        if 'w' in keys_down:
            new_x = player_pos[0] + dir_x * PLAYER_SPEED * dt
            new_y = player_pos[1] + dir_y * PLAYER_SPEED * dt
            if -PLAY_BOUND_X < new_x < PLAY_BOUND_X and -PLAY_BOUND_Y < new_y < PLAY_BOUND_Y:
                player_pos[0], player_pos[1] = new_x, new_y

        # Backward (S)
        if 's' in keys_down:
            new_x = player_pos[0] - dir_x * PLAYER_SPEED * dt
            new_y = player_pos[1] - dir_y * PLAYER_SPEED * dt
            if -PLAY_BOUND_X < new_x < PLAY_BOUND_X and -PLAY_BOUND_Y < new_y < PLAY_BOUND_Y:
                player_pos[0], player_pos[1] = new_x, new_y

        # Rotate Left (A)
        if 'a' in keys_down:
            player_angle = (player_angle - 120* dt) % 360

        # Rotate Right (D)
        if 'd' in keys_down:
            player_angle = (player_angle + 120* dt) % 360
                
        player_pos[0] = max(min(player_pos[0], PLAY_BOUND_X), -PLAY_BOUND_X)
        player_pos[1] = max(min(player_pos[1], PLAY_BOUND_Y), -PLAY_BOUND_Y)

        check_collisions()

    glutPostRedisplay()

def showScreen():
    global score, lives

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,WINDOW_W,WINDOW_H)


    draw_floor()          # draw gray bank floor
    draw_bank_walls()
    draw_vault_door()
    for t in treasures: draw_treasure(t)
    if locker_visible: draw_locker()
    if not invisible: draw_thief()
    draw_lasers()
    
    glutSwapBuffers()



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