import pygame, sys, os
from pygame.locals import *

############################
#set up file directory info#
############################
main_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(main_dir,'data')

#############################
#set up the board properties#
#############################

board = {}                                        # a dictionary of tuples representing the coordinates
board_Rect = {}                                   # a dictionary of Rect objects representing each space on the board
FPS = 30                                          # frames per second, the general speed of the program
WINDOWWIDTH = 800                                 #((BOXSIZE*BOARDWIDTH)+(2*XMARGIN))
WINDOWHEIGHT = 700                                #((BOXSIZE*BOARDHEIGHT)+(2*YMARGIN))
BOXSIZE = 80                                      # size of box height & width in pixels
BOARDWIDTH = 7                                    # number of columns of icons
BOARDHEIGHT = 7                                   # number of rows of icons
XMARGIN = (WINDOWWIDTH - (BOXSIZE*BOARDWIDTH))/2
YMARGIN = (WINDOWHEIGHT - (BOXSIZE*BOARDHEIGHT))/2
TOTALSPACES = int(BOARDHEIGHT*BOARDWIDTH)

###################
#set up aesthetics#
###################

background_color = (255,255,255)
space_color1 = (128,128,128)
highlight_box_color = (120, 239, 244)
highlight_attack_color = (200,0,0,)
mousehover_color_empty = (0,128,0,128)      #uses alpha, so you need to display_surface.convert_alpha(), then blit back onto display_surface
mousehover_color_opponent = (128,0,0,128)   #uses alpha, so you need to display_surface.convert_alpha(), then blit back onto display_surface

#######################
#define game functions#
#######################
def board_initiator(some_surface):
    for each_row in range(BOARDWIDTH):
        for each_column in range(BOARDHEIGHT):
            left = XMARGIN + (each_row*BOXSIZE)
            top = YMARGIN + (each_column*BOXSIZE)
            board[((each_row+1),(each_column+1))] = (left, top)
            board_Rect[((each_row+1),(each_column+1))] = pygame.draw.rect(some_surface, space_color1, (left, top, BOXSIZE, BOXSIZE))
            
def box_converter(shorthand_coord):
    #converts intuitive coordinates to shitty display coordinates
    #takes in tuple, outputs tuple
    return board.get(shorthand_coord)

def mousetoboard(coord):
    #takes in mouseclick coordinates and converts it into board coordinates
    x = coord[0]
    y = coord[1]
    newx = None
    newy = None
    i = 1
    while i<=BOARDWIDTH:
        try:
            if x>=board[(i,1)][0] and x<board[(i+1,1)][0]:
                newx = i
                break
            else:
                i+=1
        except:
            newx = BOARDWIDTH
            break
    i = 1
    while i<=BOARDHEIGHT:
        try:
            if y>=board[(1,i)][1] and y<board[(1,i+1)][1]:
                newy = i
                break
            else:
                i+=1
        except:
            newy = BOARDHEIGHT
            break
    #print((newx, newy))
    return(newx, newy)
    
def image_creator(name, location):
    pic_pathname = os.path.join(data_dir,name)
    try:
        image = pygame.image.load(pic_pathname).convert()
    except pygame.error:
        print('can\'t load pic: ',pic_pathname)
    return image, image.get_rect(topleft=location)

def read_mapfile(file):
    file_location = os.path.join(data_dir,file)
    fhandle = open(file_location)
    
    map_roughdata = [] #list to hold all the contents from the map file
    map_obj = []

    enemy_coordinates = []        #coordinates of all the enemies
    player_coordinates = []       #coordinates of all Heroes
    empty_space = []              #coordinates of all empty spaces
    
    for each_line in fhandle:
        line = each_line.rstrip('\r\n')
        if line.startswith('<!'):
            pass
        elif line != '':
            map_roughdata.append(line)
        elif line == '' and len(map_roughdata) > 0:
            count_x=1
            count_y=1
            for y in map_roughdata:
                for x in y:
                    if x=="E":
                        enemy_coordinates.append(box_converter((count_x, count_y)))
                        count_x +=1
                    elif x=="H":
                        player_coordinates.append(box_converter((count_x, count_y)))
                        count_x +=1
                    elif x=="_":
                        empty_space.append(box_converter((count_x, count_y)))
                        count_x +=1
                count_x =1
                count_y +=1                    
    fhandle.close()
    return player_coordinates, enemy_coordinates

def highlight_squares(location,distance,some_surface):
    #takes in board coordinates and Sprite distance and highlights movement area space onto some_surface
    movable_field = []
    y = location[1]
    x = location[0]
    for i in range(distance):
        while x-(i+1)>=0:
            movable_field.append(((x-(i+1),y)))
            break
        while y-(i+1)>=0:
            movable_field.append((x,(y-(i+1))))
            break
        while x+(i+1)<=BOARDWIDTH:
            movable_field.append(((x+(i+1)),y))
            break
        while y+(i+1)<=BOARDHEIGHT:
            movable_field.append((x,(y+(i+1))))
            break
    verticies = 1
    while distance==2 and verticies<5:
        if verticies == 1:
            if x-1>0 and y-1>0:
                movable_field.append(((x-1),(y-i)))
            else: pass
        elif verticies==2:
            if x+1<=BOARDWIDTH and y+1<=BOARDHEIGHT:
                movable_field.append(((x+1),(y+1)))
            else: pass
        elif verticies==3:
            if x+1<=BOARDWIDTH and y-1>0:
                movable_field.append(((x+1),(y-1)))
            else: pass
        elif verticies==4:
            if x-1>0 and y+1<=BOARDHEIGHT:
                movable_field.append(((x-1),(y+i)))
            else: pass
        verticies+=1
    #print(movable_field)
    
    
    for coord in movable_field:
        output = box_converter(coord)
        #print(output)
        if output is not None:
            pygame.draw.rect(some_surface, highlight_box_color, (output[0], output[1], BOXSIZE, BOXSIZE))

def confirmation():
    return
################
#define sprites#
################

class Hero(pygame.sprite.Sprite):
    def __init__ (self, hero_type, hp, attack, movement,location):
        pygame.sprite.Sprite.__init__(self)                            #Required to initiate the Sprite class
        self.image, self.imgrect = image_creator(hero_type, location)  #hero_type must be an image file name
        #self.image.set_colorkey(background_color)                    
        self.hp = hp                                                   #hp: how much stamina character has before sprite.kill()
        self.attack = attack                                           #attack: the amount of hp decrease
        self.movement = movement                                       #movement: number of squares the character moves
        self.location = location                                       #location: initial coordinates of where the character will be placed
        pos = location                                                 #initially set the pos as initial location
        self.rect = pygame.Rect(pos[0],pos[1],BOXSIZE,BOXSIZE)         #create a Rect obj for 
        self.selected_val = 0
    def update(self):
        display_surface.blit(self.image,self.imgrect)
        #pass
    def damage (self, opponent):
        self.hp -= opponent.attack
    def attack (self, opponent):
        opponent.hp -= self.attack
    def move(self, position_move):
        if position_move == (-1,0):
            #move left
            self.imgrect = self.imgrect.move(-BOXSIZE,0)
            position_move = None
        elif position_move == (1,0):
            #move right
            pos = self.rect.move(BOXSIZE,0)
            position_move = None
        elif position_move == (0,-1):
            #move up
            pos = self.rect.move(0,-BOXSIZE)
            position_move = None
        elif position_move == (0,1):
            #move down
            pos = self.rect.move(0,BOXSIZE)
            position_move = None
    def selected(self, click_location):
        if self.rect.collidepoint(click_location):
            return True
        else:
            return False
            '''
            e = pygame.event.wait()
            print(type(e))
            if e.type in (pygame.KEYDOWN):
                self.move()
            '''    
    def it(self):
        if self.selected_val == 1:
            self.selected_val = 0
        elif self.selected_val == 0:
            self.selected_val = 1
    def printer(self):
        print('self.image: {}'.format(type(self.image)))
        print('self.rect: {}'.format(type(self.rect)))
        print('self.imgrect: {}'.format(type(self.imgrect)))
        print(self.imgrect)

class Goat(pygame.sprite.Sprite):
    def __init__ (self, goat_type, hp, attack, movement,location):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = image_creator(goat_type, location)
        #self.image.set_colorkey(background_color)
        self.hp = hp
        self.attack = attack
        self.movement = movement
        self.location = location
    def update(self):
        display_surface.blit(self.image,self.location)
        #pass
    def damage (self, opponent):
        self.hp -= opponent.attack
    def attack (self, opponent):
        opponent.hp -= self.attack
    def move(self):
        if leftmove == 1:
            pos = self.rect.move(BOXSIZE,0)
            leftmove = 0
        elif rightmove == 1:
            pos = self.rect.move(-BOXSIZE,0)
            rightmove = 0
        elif upmove == 1:
            pos = self.rect.move(0,-BOXSIZE)
            upmove = 0
        elif downmove == 1:
            pos = self.rect.move(0,BOXSIZE)
            downmove = 0

    


    
##############################################################################################################################################################
########################################################################LOAD ALPENTEST########################################################################
##############################################################################################################################################################

def main():
    global FPSCLOCK, display_surface, bg_surface, board, highlighting_surface
    #FPSCLOCK: fps variable used to limit and control fps of game
    #display_surface: the Surface object which the player sees on the screen
    #board: dictionary of the board coordinate layout that maps board{intuitive coordinates:pixel coordinates}

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    display_surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))      #viewing screen properties
    pygame.display.set_caption('Alpen Hero')                                    #Title of the Game
    
    #Create Sprite Groups for the two different characters in the game, the Hero and the Evil Goats
    hero_group = pygame.sprite.Group() 
    enemy_group = pygame.sprite.Group()
    
    #set up the background, and highlighting surfaces
    bg_surface = pygame.Surface(display_surface.get_size())
    board_initiator(bg_surface)
    highlighting_surface = pygame.Surface(display_surface.get_size())
    
    player_CO, enemy_CO = read_mapfile('map_data.txt')
    #print('player CO:{},\n enemy CO:{}'.format(player_CO, enemy_CO))
    
    #create a new Hero and Goat for every coordinate found from read_mapfile and add them to their respective Sprite Group 
    for each_player_coord in player_CO:
        Player1 = Hero('kampfer_real.jpg',20,2,2,each_player_coord)
        hero_group.add(Player1)
    for each_enemy_coord in enemy_CO:
        Goat_teki = Goat('evilgoat1.jpg',3,1,1,each_enemy_coord)
        enemy_group.add(Goat_teki)
        
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Attack and Destroy all Evil Goats!", 1, (100, 100, 100))
        textpos = text.get_rect(centerx=display_surface.get_width()/2)
        bg_surface.blit(text, textpos)
    display_surface.blit(bg_surface,(0,0))
    pygame.display.update()
    
    ################
    #MAIN GAME LOOP#
    ################

    while True:
        turn = 1
        allsprites = pygame.sprite.RenderPlain((hero_group, enemy_group))      #creates a easy goto group for both hero and enemy groups
        
        #main event loop for controlling player actions
        while turn==1:
            for event in pygame.event.get(): 
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for each_hero in hero_group:
                        if each_hero.selected(mouse_pos):
                            if each_hero.selected_val == 0:
                                #each_hero.printer()
                                board_space = mousetoboard(mouse_pos)
                                pygame.display.update()
                                display_surface.blit(bg_surface,(0,0))
                                for i in hero_group:
                                    i.selected_val = 0
                                
                                
                                highlighting_surface.fill(space_color1)
                                highlight_squares(board_space,each_hero.movement,highlighting_surface)
                                highlighting_surface.set_colorkey(space_color1)
                                
                                display_surface.blit(highlighting_surface,(0,0))
                                pygame.display.update()
                                each_hero.it()
                            elif each_hero.selected_val == 1:
                                display_surface.blit(bg_surface,(0,0))
                                pygame.display.update()
                                for i in hero_group:
                                    i.selected_val = 0
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    position_move = (-1,0)
                    print(position_move)
                    for i in hero_group:
                        if i.selected_val == 1:
                            i.move(position_move)
                            print("left")
                elif event.type == KEYDOWN and event.key == K_RIGHT:
                    position_move = (1,0)
                    print(position_move)
                    for i in hero_group:
                        if i.selected_val == 1:
                            i.move(position_move)
                            print("right")
                elif event.type == KEYDOWN and event.key == K_UP:
                    position_move = (0,-1)
                    print(position_move)
                    for i in hero_group:
                        if i.selected_val == 1:
                            i.move(position_move)
                            print("up")
                elif event.type == KEYDOWN and event.key == K_DOWN:
                    position_move = (0,1)
                    print(position_move)
                    for i in hero_group:
                        if i.selected_val == 1:
                            i.move(position_move)
                            print("down")
                elif event.type == KEYDOWN and event.key == K_RETURN:
                    turn = -1
            
            position_move = None
            #display_surface.blit(bg_surface,(0,0))
            allsprites.update()
            
            #allsprites.draw(display_surface)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        #main event loop for CPU actions
        while turn==-1:
            print('wagahai no bannjya')
            allsprites.update()        
            display_surface.blit(bg_surface,(0,0))
            allsprites.draw(display_surface)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            turn = 1

if __name__ == '__main__':
    main()
