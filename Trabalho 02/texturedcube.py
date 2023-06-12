from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from PIL  import Image
from arcball import ArcBall
from math import degrees

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
    glBegin(GL_QUADS)  # Start Drawing The Cube

    # x y z
    direction = [0, 1, 0]

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
    # glTexCoord2f(0.0, 0.0)
    glTexCoord2f(0.8, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    # glTexCoord2f(1.0*size, 0.0)
    glTexCoord2f(0.8, 0.8)
    glVertex3f(1.0*size, 1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    # glTexCoord2f(1.0*size, 1.0*size)
    glTexCoord2f(1.0, 0.8)
    glVertex3f(1.0*size, 1.0*size, -1.0*size)  # Top Right Of The Texture and Quad

    # Bottom Face
    glNormal3f(0,-1,0)
    # glTexCoord2f(1.0*size, 1.0*size)
    glTexCoord2f(0.4, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Top Right Of The Texture and Quad
    # glTexCoord2f(0.0, 1.0*size)
    glTexCoord2f(0.6, 0.0)
    glVertex3f(1.0*size, -1.0*size, -1.0*size)  # Top Left Of The Texture and Quad
    # glTexCoord2f(0.0, 0.0)
    glTexCoord2f(0.6, 0.2)
    glVertex3f(1.0*size, -1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    # glTexCoord2f(1.0*size, 0.0)
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
    glColor3f(1.0, 1.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, -1.0*size)  # Top Left Of The Texture and Quad

    glEnd()


def drawCube2(size = 0.5):
    glBegin(GL_QUADS)  # Start Drawing The Cube

    # x y z
    direction = [0, 1, 0]

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
    # glTexCoord2f(0.0, 0.0)
    glTexCoord2f(0.8, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    # glTexCoord2f(1.0*size, 0.0)
    glTexCoord2f(0.8, 0.8)
    glVertex3f(1.0*size, 1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    # glTexCoord2f(1.0*size, 1.0*size)
    glTexCoord2f(1.0, 0.8)
    glVertex3f(1.0*size, 1.0*size, -1.0*size)  # Top Right Of The Texture and Quad

    # Bottom Face
    glNormal3f(0,-1,0)
    # glTexCoord2f(1.0*size, 1.0*size)
    glTexCoord2f(0.4, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Top Right Of The Texture and Quad
    # glTexCoord2f(0.0, 1.0*size)
    glTexCoord2f(0.6, 0.0)
    glVertex3f(1.0*size, -1.0*size, -1.0*size)  # Top Left Of The Texture and Quad
    # glTexCoord2f(0.0, 0.0)
    glTexCoord2f(0.6, 0.2)
    glVertex3f(1.0*size, -1.0*size, 1.0*size)  # Bottom Left Of The Texture and Quad
    # glTexCoord2f(1.0*size, 0.0)
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
    glColor3f(1.0, 1.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, -1.0*size)  # Bottom Left Of The Texture and Quad
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-1.0*size, -1.0*size, 1.0*size)  # Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, 1.0*size)  # Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*size, 1.0*size, -1.0*size)  # Top Left Of The Texture and Quad

    glEnd()


if __name__=='__main__':
    # Screen width and height
    width,height =1000,1000

    # Current rotation angle in degrees
    angle = 0

    def init():
        """Initialize state"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # Helps with antialiasing
        glEnable(GL_MULTISAMPLE)

        # Texture initialization
        textureId = loadTexture("youwin.png")
        glEnable(GL_TEXTURE_2D)
        global matrix 
        matrix = glGetDoublev(GL_MODELVIEW_MATRIX)

        
    def display():
        """Display callback: draw a sphere"""   
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0,0,-5)
        # glRotatef(90, 0, 0, 1)
        # glRotatef (80, 1,0,0)
        # glRotatef (angle,0,1,1)
        
        # glutSolidSphere(1,40,50)
        # glutSolidCube(1)
        glMultMatrixd (matrix)
        drawCube2(1)
        
        glutSwapBuffers()
        
    def reshape(w,h):
        """Reshape Callback"""
        glViewport(0,0,w,h)
        global width,height
        width,height = w,h
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective (60, w/h, 1, 10)

    def idle():
        """Idle callback. Rotate and redraw the globe"""
        global angle
        angle += 0.4
        glutPostRedisplay()
    
    def mousepress (button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                global arcball
                arcball = ArcBall ((width/2,height/2,0), width/2)
                global startx, starty
                startx, starty = x,y
                glutMotionFunc (rotatecallback)
            else:
                glutMotionFunc (None)
                
    def rotatecallback (x, y):
        global startx,starty,matrix
        angle, axis = arcball.rot (startx, height - starty, x, height - y)
        glLoadIdentity ()
        glRotatef (degrees(angle),*axis)
        glMultMatrixd (matrix)
        matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        startx,starty = x,y
        glutPostRedisplay()
        
    glutInit(sys.argv)
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-width)//2,
                        (glutGet(GLUT_SCREEN_HEIGHT)-height)//2)
    glutInitWindowSize (width,height)
    glutCreateWindow ("Textured Cube")
    glutDisplayFunc (display)
    glutReshapeFunc (reshape)
    glutMouseFunc(mousepress)
    # glutIdleFunc(idle)
    init()
    glutMainLoop()