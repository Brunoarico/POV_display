import pygame
from pygame.locals import *
import numpy as np

pygame.init()

FONT = pygame.font.Font(None, 32)
gray = (50, 50, 50)
black = (0, 0, 0)
red   = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
color_x = (20, 20, 20)
white = (255)

class InputBox:
    def __init__(self, x, y, w, h, text='', color = [255,255,255] ):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.txt_surface = FONT.render(text, True, tuple(self.color))
        self.active = False

    def active_action(self):
        if self.active:
            for i in range(0,3):
                if self.color[i] > 0:
                    self.color[i] = 200 
        else:
            for i in range(0,3):
                if self.color[i] > 0:
                    self.color[i] = 255

                    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        self.active_action()
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < 3 and pygame.K_0 <= event.key <= pygame.K_9:
                    self.text += event.unicode
                    
                    if(int(self.text) > 255):
                        self.text = "255"  
                self.txt_surface = FONT.render(self.text, True, tuple(self.color))
        
        if(len(self.text) == 0 and not self.active):
            self.text = "0"
            self.txt_surface = FONT.render(self.text, True, tuple(self.color))
    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, tuple(self.color), self.rect, 2)


class Screen:
    def __init__(self):
        self.win_size = (750, 700)
        self.button_w = 15
        self.button_size = (self.button_w, self.button_w)
        self.pixelsx = 36
        self.pixelsy = 36
        self.cell_marg = 1
        self.screenpadx = 90 
        self.screenpady = 100 
        self.done = False 
        self.grid_p = np.zeros((self.pixelsy, self.pixelsx),dtype='object')
        self.window = pygame.display.set_mode(self.win_size)
        pygame.display.set_caption('Draw')
        self.clock = pygame.time.Clock()
        self.currentColor = red
        self.color_b = [255,255,255]
        self.grid_b = []
        self.setButtons()
        self.spawnTextBox()
        self.createCells()
        self.mainLoop()

    def rgb_to_hex(self, rgb):
        return int('%02x%02x%02x' % rgb, 16)
    
    def setButtons(self):
        self.printbutton = (700, 650, 50, 50)

    def drawButton(self):
        pygame.draw.rect(self.window, color_x, self.printbutton)
        self.window.blit(FONT.render('print', True, (0,150,150)), (700, 665))

    def spawnTextBox(self):
        base = 120
        input_red   = InputBox (80 +base , 20, 100, 30, "255", [255,0,0])
        input_green = InputBox (200 +base, 20, 100, 30, "255", [0,255,0])
        input_blue  = InputBox (320 +base, 20, 100, 30, "255", [0,0,255])
        self.input_boxes = [input_red, input_green, input_blue]

    def getText(self):
        self.currentColor = (int(self.input_boxes[0].text), int(self.input_boxes[1].text), int(self.input_boxes[2].text))
        
    def printGrid(self):
        s = "#define LINES "+str(self.pixelsx) +"\n\nconst uint16_t m["+str(self.pixelsx) +"]["+str(self.pixelsy) +"] PROGMEM = {"
        result = ""
        for i in range(0, self.pixelsx):
            s =s + "{"
            for j in range(0, self.pixelsy):
                s = s + str( hex(self.grid_p[j][i]) ) +", "
            s = s[:-2]
            result += s+"},\n"
            s = ""
        result = result[:-2] + "};"
        text_file = open("Output.txt", "w")
        text_file.write(result)
        text_file.close()
        print("file Saved")

    def createCells(self):
        offsetCells = self.button_w + self.cell_marg
        for y in range(self.pixelsy):
            self.row = []
            for x in range(self.pixelsx):
                self.row.append([x * (offsetCells) + self.screenpadx, y * (offsetCells) + self.screenpady, black])
            self.grid_b.append(self.row)
            
    def mainLoop(self):
        while not self.done:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.done = True
            
                for box in self.input_boxes:
                    box.handle_event(event)
                
                if event.type == MOUSEBUTTONDOWN:
                    
                    mpos_x, mpos_y = event.pos


                    button_x_min, button_y_min, button_width, button_height = self.printbutton
                    button_x_max, button_y_max = button_x_min + button_width, button_y_min + button_height
                    if button_x_min <= mpos_x <= button_x_max and button_y_min <= mpos_y <= button_y_max:
                        self.printGrid()


                    mpos_x -= self.screenpadx
                    mpos_y -= self.screenpady

                    col = mpos_x // (self.button_w + self.cell_marg) 
                    row = mpos_y // (self.button_w + self.cell_marg)

                    # make sure the user clicked on the GRID area
                    if row >= 0 and col >= 0:
                        try:
                            # calculate the boundaries of the cell
                            cell_x_min, cell_y_min =  col * (self.button_w + self.cell_marg), row * (self.button_w + self.cell_marg)
                            cell_x_max = cell_x_min + self.button_w
                            cell_y_max = cell_y_min + self.button_w
                            # now we will see if the user clicked the cell or the margin
                            self.getText()
                            if cell_x_min <= mpos_x <= cell_x_max and cell_y_min <= mpos_y <= cell_y_max:
                                self.grid_b[row][col][2] = self.currentColor if event.button == 1 else black
                                self.grid_p[row][col] = self.rgb_to_hex(self.currentColor)

                            else:
                                pass
                        except IndexError: 
                            pass           

            self.window.fill(gray)
            
            for box in self.input_boxes:
                box.draw(self.window)
                
            self.drawButton()
            
            for row in self.grid_b:
                for x, y, color in row:
                    pygame.draw.rect(self.window, color, (x, y, self.button_w, self.button_w))
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

Screen()
