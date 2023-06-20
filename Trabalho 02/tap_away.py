import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from arcball import ArcBall
from math import degrees
from PIL  import Image
import random

# Selected object
selected = None

# Set of removed objects
removed = set()

# Set of objects translating to be removed
being_removed = set()

# size of cube array
n = 3

# rotation angle
angle = 0

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

# Parameters for removing translation
MINICUBE_SPACE = 1/n
MINICUBE_SIZE = MINICUBE_SPACE*0.8
TRANSLATE_INTERVAL = (MINICUBE_SPACE-MINICUBE_SIZE)*0.7

POSSIBLE_ROTATIONS = { 0: [0, 0, 0, 0],    # Up
                        1: [180, 1, 0, 0],  # Down
                        2: [90, 0, 0, 1],   # Left
                        3: [90, 0, 0, -1],  # Right
                        4: [90, 1, 0, 0],   # Forward
                        5: [90, -1, 0, 0],  # Backward
                    }

# Hashmap for cube top face direction
cubes_directions={}

# Hashmap for cube translation when being removed
cubes_translations={}

# Directed Graph for creating mini cubes dependecy
# A -> B means: A is blocked by B
graph_cubes_dependency = {}

def find_cube_coords(name):
    # Aux function to find i, j, k coords of mini cube
    k = name%n
    j = ((name-k)//n)%n
    i = ((name-k-(j*n)))//(n**2)

    return [i, j, k]

def possible_blocking_cubes(name, direction):
    # Find mini cube possible blockings through graph

    coords = find_cube_coords(name)
    i = coords[0]
    j = coords[1]
    k = coords[2]

    if(direction[0] != 90): # Up or Down
        # j is variable
        possible_blockings = [(i*n + j_var) * n + k for j_var in range(n)]
        possible_blockings.remove(name)
        if(direction[1] > 0): # Down
            blocking_cubes = [x for x in possible_blockings if x < name]
        else: # Up
            blocking_cubes = [x for x in possible_blockings if x > name]
        
    elif(direction[1] == 0): # Right or left
        # i is variable
        possible_blockings = [(i_var*n + j) * n + k for i_var in range(n)]
        possible_blockings.remove(name)
        if(direction[3] > 0): # Left
            blocking_cubes = [x for x in possible_blockings if x < name]
        else: # Right
            blocking_cubes = [x for x in possible_blockings if x > name]

    else: # Forward or backward
        # k is variable
        possible_blockings = [(i*n + j) * n + k_var for k_var in range(n)]
        possible_blockings.remove(name)
        if(direction[1] > 0): # Forward
            blocking_cubes = [x for x in possible_blockings if x > name]
        else: # Backward
            blocking_cubes = [x for x in possible_blockings if x < name]
    
    return blocking_cubes

def init_cube_directions():
    # Init cubes removing directions. Has to check if there is no cycle in dependency graph.

    for i in range(n):
        for j in range(n):
            for k in range(n):
                name = (i*n + j) * n + k
                graph_cubes_dependency[name] = []
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                name = (i*n + j) * n + k
                random_n = random.randint(0, 5)
                temp_direction = POSSIBLE_ROTATIONS.get(random_n)
                temp_blockings = possible_blocking_cubes(name, temp_direction)
                while(not DFS(temp_blockings, name)):
                    random_n += 1
                    temp_direction = POSSIBLE_ROTATIONS.get(random_n%6)
                    temp_blockings = possible_blocking_cubes(name, temp_direction)
                    
                graph_cubes_dependency[name] = temp_blockings
                cubes_directions[name] = temp_direction
                cubes_translations[name] = [0, 0, 0]

def DFS_Util(v, visited):
    visited.add(v)
    for u in graph_cubes_dependency.get(v):
        if u not in visited:
            DFS_Util(u, visited)

def DFS(starts: list, target):
    # DFS function to check if it is possible to create dependency without creating a cycle in graph.
    for start in starts:
        visited = set()
        DFS_Util(start, visited)
        if(target in visited):
            return False
    return True # No cycle

def possible_checkout(name):
    # Function to check if it is possible to remove a cube.
    
    blocking_cubes = graph_cubes_dependency.get(name)
    blocking_cubes = [x for x in blocking_cubes if x not in being_removed]

    if(len(blocking_cubes)==0):
        return True
    else:
        return False

def update_cube_translation(name, forward = 1):
    direction = cubes_directions[name]
    if(direction[0] != 90): # Up or Down
        if(direction[1] > 0): # Down
            cubes_translations[name][1] -= TRANSLATE_INTERVAL * forward
        else: # Up
            cubes_translations[name][1] += TRANSLATE_INTERVAL * forward
        
    elif(direction[1] == 0): # Right or left
        if(direction[3] > 0): # Left
            cubes_translations[name][0] -= TRANSLATE_INTERVAL * forward
        else: # Right
            cubes_translations[name][0] += TRANSLATE_INTERVAL * forward

    else: # Forward or backward
        if(direction[1] > 0): # Forward
            cubes_translations[name][2] += TRANSLATE_INTERVAL * forward
        else: # Backward
            cubes_translations[name][2] -= TRANSLATE_INTERVAL * forward

    return max(cubes_translations[name], key=abs)

def remove_success_animation(selected):
    
    actual_translation = update_cube_translation(selected, forward = 1)
    if(abs(actual_translation)<2): # Sufficient to exit screen
        glutTimerFunc(20, remove_success_animation, selected)
    else:
        removed.add(selected)
    glutPostRedisplay()

def remove_fail_animation_forward(selected):
    
    update_cube_translation(selected, forward = 1)
    glutTimerFunc(150, remove_fail_animation_backward, selected)
    glutPostRedisplay()

def remove_fail_animation_backward(selected):

    update_cube_translation(selected, forward = -1)
    cubes_translations[selected] = [0,0,0]
    glutPostRedisplay()

def loadTexture (filename):
    "Loads an image from a file as a texture"

    # Read file and get pixels
    imagefile = Image.open(filename)
    sx,sy = imagefile.size[0:2]
    global pixels
    pixels = imagefile.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    # Create an OpenGL texture name and load image into it
    image = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, image)  
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, sx, sy, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
    
    # Set other texture mapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    
    # Return texture name (an integer)

    return image

def drawCube(size = 0.5):
    # Function to draw a minicube
    size = size/2
    glBegin(GL_QUADS)  # Start Drawing The Cube

    # Front Face (note that the texture's corners have to match the quad's corners)
    glNormal3f(0,0,1)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(1.0, 0.0)
    glVertex3f(1.0*size, -1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(1.0*size, 1.0*size, 1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Top Left Of The Texture and Quad

    # Back Face
    glNormal3f(0,0,-1)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, -1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(1.0*size, 1.0*size, -1.0*size)  # Top Left Of The Texture and Quad
    glTexCoord2f(0.0, 0.0)
    glVertex3f(1.0*size, -1.0*size, -1.0*size)  # Bottom Left Of The Texture and Quad

    # Top Face
    glNormal3f(0,1,0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, -1.0*size)  # Top Left Of The Texture and Quad
    glTexCoord2f(0.8, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(0.8, 0.8)
    glVertex3f(1.0*size, 1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 0.8)
    glVertex3f(1.0*size, 1.0*size, -1.0*size)  # Top Right Of The Texture and Quad

    # Bottom Face
    glNormal3f(0,-1,0)
    glTexCoord2f(0.4, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.6, 0.0)
    glVertex3f(1.0*size, -1.0*size, -1.0*size)  # Top Left Of The Texture and Quad
    glTexCoord2f(0.6, 0.2)
    glVertex3f(1.0*size, -1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(0.4, 0.2)
    glVertex3f(-1.0*size, -1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad

    # Right face
    glNormal3f(1,0,0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(1.0*size, -1.0*size, -1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(1.0*size, 1.0*size, -1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(1.0*size, 1.0*size, 1.0*size)  # Top Left Of The Texture and Quad
    glTexCoord2f(0.0, 0.0)
    glVertex3f(1.0*size, -1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad

    # Left Face
    glNormal3f(-1,0,0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, -1.0*size)  # Top Left Of The Texture and Quad

    glEnd()

def draw_you_win():
    # Function to draw You win screen
    glDisable(GL_TEXTURE_2D)
    loadTexture("youwin.png")
    glEnable(GL_TEXTURE_2D)

    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0)
    glVertex2f(-1, -1)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(1, -1)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(1, 1)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(-1, 1)

    glEnd()



def draw_scene(flatColors = False):
    "Draws the scene emitting a 'name' for each cube"
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    size = 1/n
    if(len(removed)<n**(3)):
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0,0, -3)
        glMultMatrixd (matrix)
        for i in range(n):
            x = i - (n-1)/2 
            for j in range(n):
                y = j - (n-1)/2 
                for k in range(n):
                    z = k - (n-1)/2 
                    name = (i*n + j) * n + k
                    if flatColors:
                        glColor3f((i+1)/n, (j+1)/n, (k+1)/n)
                    # Ignore removed objects
                    if name in removed: continue 
                    glLoadName(name)
                    glPushMatrix()
                    glTranslatef((x*size),y*size,z*size)
                    translations = cubes_translations.get(name)
                    glTranslatef(translations[0], translations[1], translations[2])
                    direction = cubes_directions.get(name)
                    glRotatef(direction[0], direction[1], direction[2], direction[3])
                    drawCube(0.8*size)
                    glPopMatrix()
    else:
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0,0,-2)
        draw_you_win()
            
def display():
    draw_scene()
    glutSwapBuffers()

def init ():
    glClearColor (0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glLight(GL_LIGHT0, GL_POSITION, [.5,.2,1,0])
    glMaterial(GL_FRONT_AND_BACK, GL_EMISSION, [0.2,0.2,0.2,1])
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    # Helps with antialiasing
    glEnable(GL_MULTISAMPLE)

    textureId = loadTexture("arrow2.jpg")
    glEnable(GL_TEXTURE_2D)

    global matrix 
    matrix = glGetDoublev(GL_MODELVIEW_MATRIX)

    init_cube_directions()

def reshape(width,height):
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity()
    global projectionArgs, windowSize
    windowSize = width,height
    projectionArgs = 50, width/height, 0.1,20
    gluPerspective (*projectionArgs)
    glViewport (0,0,width,height)
 
def pick(x,y):
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    draw_scene(True)
    glFlush()
    glEnable (GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    buf = glReadPixels (x,windowSize[1]-y,1,1,GL_RGB,GL_FLOAT)
    pixel = buf[0][0]
    r,g,b = pixel
    i,j,k = int(r*n-1),int(g*n-1),int(b*n-1)
    if i >= 0: return (i*n + j) * n + k
    return -1 

def mousePressed(button,state,x,y):
    global selected
    if state == GLUT_DOWN:
        global prevx, prevy, prevz 
        prevx,prevy = x,y
        global startx, starty
        startx, starty = x,y
        selected = pick(x,y)
        if selected >= 0:
            if(possible_checkout(selected)):
                being_removed.add(selected)
                remove_success_animation(selected)
            else:
                remove_fail_animation_forward(selected)
    glutPostRedisplay()

def mousepressArc (x, y):

    global arcball
    arcball = ArcBall ((WINDOW_WIDTH/2,WINDOW_HEIGHT/2,0), WINDOW_WIDTH/2)
    global startx, starty
    startx, starty = x,y
    glutMotionFunc (rotatecallback)

            
def rotatecallback (x, y):
    global startx,starty,matrix
    angle, axis = arcball.rot (startx, WINDOW_WIDTH - starty, x, WINDOW_HEIGHT - y)
    glLoadIdentity ()
    glRotatef (degrees(angle),*axis)
    glMultMatrixd (matrix)
    matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    startx,starty = x,y
    glutPostRedisplay()

def idle():
    """Idle callback. Rotate and redraw the scene"""
    global angle
    angle += 0.4
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize (WINDOW_WIDTH, WINDOW_HEIGHT) 
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-WINDOW_WIDTH)//2, (glutGet(GLUT_SCREEN_HEIGHT)-WINDOW_HEIGHT)//2)
    glutCreateWindow ("Tap Away")
    init ()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mousePressed)
    glutMotionFunc(mousepressArc)
    glutMainLoop()

main()