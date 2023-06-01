import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

# Selected object
selected = None

# Set of removed objects
removed = set()

# size of cube array
n = 3

# rotation angle
angle = 0


def draw_scene():
    "Draws the scene emitting a 'name' for each cube"
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0,0,-3)
    glRotatef (-80, 1,0,0)
    glRotatef (angle,0,1,1)
    size = 1/n
    for i in range(n):
        x = i - (n-1)/2 
        for j in range(n):
            y = j - (n-1)/2 
            for k in range(n):
                z = k - (n-1)/2 
                name = (i*n + j) * n + k
                # Ignore removed objects
                if name in removed: continue 
                glLoadName(name)
                glPushMatrix()
                glTranslatef(x*size,y*size,z*size)
                glutSolidCube(size*0.8)
                glPopMatrix()
            
def display():
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


def reshape(width,height):
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity()
    global projectionArgs, windowSize
    windowSize = width,height
    projectionArgs = 50, width/height, 0.1,20
    gluPerspective (*projectionArgs)
    glViewport (0,0,width,height)
 
def pick(x,y):
    glMatrixMode (GL_PROJECTION)
    glPushMatrix ()
    glLoadIdentity ();
    viewport = glGetIntegerv(GL_VIEWPORT)
    gluPickMatrix (x,windowSize[1]-y,2,2,viewport);
    gluPerspective (*projectionArgs)
    glSelectBuffer(100)
    glRenderMode(GL_SELECT)
    glInitNames()
    glPushName(-1)
    draw_scene()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glPopName()
    buffer = glRenderMode(GL_RENDER)
    obj,z = -1,100
    for zmin,zmax,name in buffer:
        if name != [] and zmin < z: obj,z = name[0],zmin
    return obj,z

def mousePressed(button,state,x,y):
    global selected
    if state == GLUT_DOWN:
        global prevx, prevy, prevz 
        prevx,prevy = x,y
        selected,prevz = pick(x,y)
        if selected >= 0:
            removed.add(selected)
    glutPostRedisplay()

def idle():
    """Idle callback. Rotate and redraw the scene"""
    global angle
    angle += 0.4
    glutPostRedisplay()

def main():
    glutInit(sys.argv);
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE);
    glutInitWindowSize (400, 400); 
    glutInitWindowPosition (100, 100);
    glutCreateWindow ("picking");
    init ();
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mousePressed)
    glutIdleFunc(idle)
    glutMainLoop();

main()