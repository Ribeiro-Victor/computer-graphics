import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from arcball import ArcBall
from math import degrees
from texturedcube import drawCube, loadTexture
import random

# Selected object
selected = None

# Set of removed objects
removed = set()

# size of cube array
n = 3

# rotation angle
angle = 0

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

possible_directions = { 0: [0, 0, 0, 0],    # Cima
                        1: [180, 1, 0, 0],  # Baixo
                        2: [90, 0, 0, 1],   # Esquerda
                        3: [90, 0, 0, -1],  # Direita
                        4: [90, 1, 0, 0],   # Frente
                        5: [90, -1, 0, 0],  # Trás
                    }

cubes_directions={}
# graph_cubes_dependency={'a':['b', 'c'],
#                         'b':['e', 'f'],
#                         'c':['g', 'd'],
#                         'd':['b', 'f'],
#                         'g':[],
#                         'f':[],
#                         'e':['f']}
graph_cubes_dependency = {}
# A -> B, significa que A precisa de B para ser liberado.

def find_cube_coords(name):
    # Acha as coordenas i, j, k do cubinho
    common_multiplier = n**(n-1) 
    i = name//(common_multiplier)
    j = (name-(i*common_multiplier)) // n
    k = (name-(i*common_multiplier)-(j*n)) % n #Só funciona para n = 3 por enquanto
    # print("i j k:", i, j, k)

    return [i, j, k]

def possible_blocking_cubes(name, direction):

    coords = find_cube_coords(name)
    i = coords[0]
    j = coords[1]
    k = coords[2]
    # direction = cubes_directions.get(name)

    if(direction[0] != 90): # Direção é cima ou baixo
        # Variação do J
        possible_blockings = [(i*n + j_var) * n + k for j_var in range(n)]
        possible_blockings.remove(name)
        if(direction[1] > 0): # Baixo
            blocking_cubes = [x for x in possible_blockings if x < name]
        else: # Cima
            blocking_cubes = [x for x in possible_blockings if x > name]
        
    elif(direction[1] == 0): # Direção é direita ou esquerda
        # Variação do I
        possible_blockings = [(i_var*n + j) * n + k for i_var in range(n)]
        possible_blockings.remove(name)
        if(direction[3] > 0): # Esquerda
            blocking_cubes = [x for x in possible_blockings if x < name]
        else: # Direita
            blocking_cubes = [x for x in possible_blockings if x > name]

    else: # Direção é frente ou trás
        # Variação do K
        possible_blockings = [(i*n + j) * n + k_var for k_var in range(n)]
        possible_blockings.remove(name)
        if(direction[1] > 0): # Frente
            blocking_cubes = [x for x in possible_blockings if x > name]
        else: # Trás
            blocking_cubes = [x for x in possible_blockings if x < name]
    
    return blocking_cubes


def init_cube_directions():
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
                temp_direction = possible_directions.get(random_n)
                temp_blockings = possible_blocking_cubes(name, temp_direction)
                while(not DFS(temp_blockings, name)):
                    random_n += 1
                    temp_direction = possible_directions.get(random_n%6)
                    temp_blockings = possible_blocking_cubes(name, temp_direction)
                    
                graph_cubes_dependency[name] = temp_blockings
                cubes_directions[name] = temp_direction

def DFS_Util(v, visited):
    visited.add(v)
    for u in graph_cubes_dependency.get(v):
        if u not in visited:
            DFS_Util(u, visited)

def DFS(starts: list, target):
    # Função DFS que checa se é possível criar dependencia entre vértices sem formar ciclo
    for start in starts:
        visited = set()
        DFS_Util(start, visited)
        if(target in visited):
            return False
    return True # Significa que não formará ciclo

# DFS(['e', 'c'],'a')
                

init_cube_directions()
print(graph_cubes_dependency)
# print(cubes_directions)



def possible_checkout(name):
    
    # blocking_cubes = possible_blocking_cubes(name, cubes_directions.get(name))
    blocking_cubes = graph_cubes_dependency.get(name)
    blocking_cubes = [x for x in blocking_cubes if x not in removed]

    # print('possible blocking_cubes', possible_blockings)
    # print('blocking_cubes', blocking_cubes)
    if(len(blocking_cubes)==0):
        return True
    else:
        return False
    

def draw_you_win():
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
    pass

def draw_scene(flatColors = False):
    "Draws the scene emitting a 'name' for each cube"
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0,0,-3)
    glMultMatrixd (matrix)
    # glRotatef (-80, 1,0,0)
    # glRotatef (angle,0,1,1)
    counter = 0
    size = 1/n
    if(len(removed)<n**(3)):
    # if(False):
        for i in range(n):
            x = i - (n-1)/2 
            for j in range(n):
                y = j - (n-1)/2 
                for k in range(n):
                    z = k - (n-1)/2 
                    name = (i*n + j) * n + k
                    # print(name)
                    if flatColors:
                        glColor3f((i+1)/n, (j+1)/n, (k+1)/n)
                    # glColor3f(1, 1, 0)
                    # Ignore removed objects
                    if name in removed: continue 
                    glLoadName(name)
                    glPushMatrix()
                    if(name == 2):
                        # print('display')
                        aa = 0.2
                    else:
                        aa = 0
                    glTranslatef((x*size),y*size,z*size)
                    # glutSolidCube(size*0.8)
                    direction = cubes_directions.get(name)
                    
                    glRotatef(direction[0], direction[1], direction[2], direction[3])
                    drawCube(0.4*size)
                    glPopMatrix()
    else:
        # glPushMatrix()
        # glutSolidCube(1)
        draw_you_win()
        # glPopMatrix()
            
def display():
   
    # glMultMatrixd (matrix)
    draw_scene();
    glutSwapBuffers ();

def init ():
    glClearColor (0.0, 0.0, 0.0, 0.0);
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
        # print("pressed:", x, y)
        if selected >= 0:
            print('selected:', selected)
    
            # glLoadIdentity()
            # glLoadName(selected)
            # glPushMatrix()
            # glTranslatef(100, 0, 0)
            # drawCube()
            # glPopMatrix()
            if(possible_checkout(selected)):
                removed.add(selected)
                print('removido')
            else:
                print('existem cubos bloqueantes')

        # else:
        #     global arcball
        #     arcball = ArcBall ((width/2,height/2,0), width/2)
        #     global startx, starty
        #     startx, starty = x,y
        #     glutMotionFunc (rotatecallback)
    glutPostRedisplay()

# def mousepressArc (button, state, x, y):
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
    glutInit(sys.argv);
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE);
    glutInitWindowSize (WINDOW_WIDTH, WINDOW_HEIGHT); 
    # glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-WINDOW_WIDTH)//2, (glutGet(GLUT_SCREEN_HEIGHT)-WINDOW_HEIGHT)//2)
    glutInitWindowPosition(((glutGet(GLUT_SCREEN_WIDTH)-WINDOW_WIDTH)//2)+400, (glutGet(GLUT_SCREEN_HEIGHT)-WINDOW_HEIGHT)//2)
    glutCreateWindow ("picking");
    init ();
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mousePressed)
    glutMotionFunc(mousepressArc)
    # glutIdleFunc(idle)
    # glutMouseFunc(mousepressArc)
    glutMainLoop();

main()