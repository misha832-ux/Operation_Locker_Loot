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
game_over = False
mission_complete = False


keys_down = set()       # set of currently pressed keys
last_time = None

# Camera controls
camera_distance = 500.0      # how far the camera is from the player
camera_angle_x = 45.0        # vertical tilt of camera
camera_angle_y = 45.0         # horizontal rotation of camera
camera_follow_player = True    # camera follows the player, if False, camera is fixed
camera_rotation_speed = 60.0   # degrees per second

# Time limit
game_time = 0.0
TIME_LIMIT = 300.0  # 5 minutes
time_up = False


def deg_to_rad(d): return d * math.pi / 180.0
def player_forward_xy():
    rad = deg_to_rad(player_angle)
    dx = math.sin(rad)
    dy = math.cos(rad)
    return dx, dy


# Drawing 
def draw_text(x, y, text):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text: 
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def keyboardListener(key,x,y):
    global keys_down, laser_forced_off, laser_forced_timer
    global tile_cheat, invisible, inv_timer, paused, slow_mode
    global camera_follow_player, camera_distance, camera_angle_x, camera_angle_y

    k=key.decode('utf-8','ignore').lower()
    if not k: 
        return
    if key==b'r': 
        restart_game()
    if key==b'c': 
        camera_follow_player = not camera_follow_player
    if key==b'=' or key==b'+':      # zoom in
        camera_distance = max(200, camera_distance - 50)
    if key==b'-':       # zoom out              
        camera_distance = min(1000, camera_distance + 50)
    if key==b'q': 
        camera_angle_y += 15  # Rotate camera left
    if key==b'e': 
        camera_angle_y -= 15  # Rotate camera right
    if key==b'z': 
        camera_angle_x = max(10, camera_angle_x - 15)  # Tilt camera down
    if key==b'x': 
        camera_angle_x = min(80, camera_angle_x + 15)  # Tilt camera up
    keys_down.add(k)

def keyboardUp(key,x,y):
    k=key.decode('utf-8','ignore').lower()
    if k in keys_down: keys_down.remove(k)

# Camera
def setupCamera():
    global camera_distance, camera_angle_x, camera_angle_y, camera_follow_player
    
    glMatrixMode(GL_PROJECTION); 
    glLoadIdentity()
    gluPerspective(60,float(WINDOW_W)/float(WINDOW_H),0.1,2000)
    glMatrixMode(GL_MODELVIEW); 
    glLoadIdentity()
    
    if camera_follow_player:
        # Follow player camera
        cam_x = player_pos[0] + camera_distance * math.sin(deg_to_rad(camera_angle_y))
        cam_y = player_pos[1] + camera_distance * math.cos(deg_to_rad(camera_angle_y))
        cam_z = camera_distance * math.sin(deg_to_rad(camera_angle_x))            # camera's height
        gluLookAt(cam_x, cam_y, cam_z, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)
    else:
        # Fixed camera
        gluLookAt(400,400,camera_distance,0,0,0,0,0,1)


def idle():
    global last_time, player_pos, player_angle, laser_on, laser_timer
    global laser_forced_off, laser_forced_timer
    global paused, inv_timer, invisible
    global lives, game_over
    global game_time, time_up
    global camera_angle_y, camera_angle_x

    now=time.time()
    dt=(now-last_time) if last_time else 1/60.0   # If last_time is not set yet (first frame), it defaults to 1/60.0
    last_time=now
    
    # Update game time
    if not game_over and not time_up:
        game_time += dt
        if game_time >= TIME_LIMIT:     # mark time-up
            time_up = True
            game_over = True
    
    # Smooth camera rotation with held keys
    if 'q' in keys_down:
        camera_angle_y += camera_rotation_speed * dt
    if 'e' in keys_down:
        camera_angle_y -= camera_rotation_speed * dt
    if 'z' in keys_down:
        camera_angle_x = max(10, camera_angle_x - camera_rotation_speed * dt)
    if 'x' in keys_down:
        camera_angle_x = min(80, camera_angle_x + camera_rotation_speed * dt)
    
    glutPostRedisplay()

def showScreen():
    global score, lives

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,WINDOW_W,WINDOW_H)
    setupCamera()


    # Display game info
    remaining_time = max(0, TIME_LIMIT - game_time)
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    if mission_complete:
       draw_text(10,WINDOW_H-20,"MISSION COMPLETED! Press R")
    elif game_over: 
       if time_up:
         draw_text(10,WINDOW_H-20,"TIME'S UP! Press R")
       else:
         draw_text(10,WINDOW_H-20,"GAME OVER! Press R")
       score = 0
       lives = 3
    else: 
       draw_text(10,WINDOW_H-20,f"Score: {score}  Lives: {lives}  Time: {time_str}")

    
       # Camera info
       camera_mode = "Follow" if camera_follow_player else "Fixed"
       draw_text(10,WINDOW_H-40,f"Camera: {camera_mode} (C)  Zoom: +/-  Rotate: Q/E/Z/X")
    
    glutSwapBuffers()


def restart_game():

    global player_pos,player_angle,score,game_over,locker_visible,lives
    global game_time, time_up, mission_complete

    player_pos=[-PLAY_BOUND_X+30,0,20]
    player_angle=90
    score=0
    lives=START_LIFE
    game_over=False 
    locker_visible=False
    game_time=0.0
    time_up=False
    mission_complete=False


def main():

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W,WINDOW_H)
    glutInitWindowPosition(50,50)
    glutCreateWindow(b"Operation Locker Loot - Safe Mode")
    restart_game()
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUp)
    glutMainLoop()


if __name__=="__main__":

    main()
