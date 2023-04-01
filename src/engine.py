import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np

'''
Engine needs to do the following:
-   Draw Background (2 triangles to make a square, disregard index buffers) 
-   Create a shader (read from file, compile, attach) 
-   

'''

class Engine:

    def __init__(self, width=640, height=480):
        self.screenWidth = width
        self.screenHeight = height

        self.shader = self.CreateShader()
        self.computeShader = self.CreateComputeShader()

        glUseProgram(self.shader)

    def CreateBG(self, rgba=np.ones(4, np.uint8)):
        #[x, y]
        self.background = np.array(
            [-1.0, -1.0, # bottom left
             -1.0,  1.0, # top left
              1.0, -1.0, # bottom right
             -1.0,  1.0, # top left
              1.0, -1.0, # bottom right
              1.0,  1.0], #top right
              dtype=np.float 
        )
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(self.vbo)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4 * 2, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 2, ctypes.c_void_p(12)) # Not sure what the pointer should be passed

    def createColorBuffer(self):

        self.colorBuffer = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.screenWidth, self.screenHeight, 0, GL_RGBA, GL_FLOAT, None)
    

    def CreateShader(self):
        #Handles shaders
        with( open("shader/fragment.glsl")) as fragf:
            fragmentShaderSource = vertf.readlines()

        with( open("shader/vertex.glsl")) as vertf:
            vertexShaderSource = vertf.readlines()

        shader = compileProgram(compileShader(vertexShaderSource, GL_VERTEX_SHADER),
                                compileShader(fragmentShaderSource, GL_FRAGMENT_SHADER))

        return shader

    def CreateComputeShader(self):
        with( open("shader/compute.glsl")) as f:
            computedShaderSource = f.readlines()

        shader = compileProgram(compileShader(computedShaderSource, GL_COMPUTE_SHADER))

        return shader


    def renderScene(self):
        """
            Draw all objects in the scene
        """
        
        glUseProgram(self.computeShader)

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.colorBuffer, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        
        glDispatchCompute(self.screenWidth, self.screenHeight, 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        glBindImageTexture(0, 0, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        self.drawScreen()

    def drawScreen(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glUseProgram(self.rayTracerShader)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        glDeleteProgram(self.rayTracerShader)
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(1, (self.colorBuffer,))
        glDeleteProgram(self.shader)
        
