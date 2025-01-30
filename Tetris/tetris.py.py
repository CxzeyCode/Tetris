#Imports the Pygame library, which provides a set of Python modules designed for writing video games. This library handles graphics, sound, input, and other functionality needed for game development.
import pygame
import random
import json
import os
#this above is the imports i am required to have in order for the game to run and display, the json and os is for the ability for the leaderboard to be stored and displayed.
colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]
#the colours are defined for the blocks

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0
#def __init__(self, x, y): Initialises a figure with random shape (type), color, and starting position.
#
    def image(self):
        return self.figures[self.type][self.rotation]
         # Returns the current layout of the figure

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])
        # Rotates the figure to the next orientation


class Tetris:
    def __init__(self, height, width):
        #initialises the game gird, score and state
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = 0
        self.width = 0
        self.x = 200
        self.y = 160
        self.zoom = 30
        self.figure = None
    
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        #initialises the grid
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    #spawns a new figure at the top of the grid
    def new_figure(self):
        self.figure = Figure(3, 0)
    #resets the gamr state
    def reset(self):
        self.__init__(self.height, self.width)
    #checks if the current figure collides with edges or other blocks
    def intersects(self):
        intersection = False
        for i in range(4):  
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        #clears filled rows and shifts blocks above downwards to the bottom
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def go_space(self):
        #drops the figure directly to the lowest valid position
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        #moves the figyre one step downward
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        #fixes the figure into the grid when it lands
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        #moves the figure horizontally
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        #attempts to rotate the figure
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


class Text(pygame.sprite.Sprite):
    def __init__(self, x_coord, y_coord, text, size, colour):
        #creates the text sprite for displaying messages
        super().__init__()
        self.font = pygame.font.Font("/coolvetica/Coolvetica Rg.otf", size)
        self.image = self.font.render(text, "AA", colour)
        self.rect = self.image.get_rect(center=(x_coord, y_coord))


class Button:
    #creates a button with dimenstions, colour and text
    def __init__(self, x, y, width, height, color, text='', text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 35)
        self.text_surf = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        #draws the button on the game screen
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        #checks to see if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        #creates an input box for the player to enter theur name
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = pygame.font.Font(None, 35).render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        #handles the user interation with the input box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = pygame.font.Font(None, 35).render(self.text, True, self.color)
        return None

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


pygame.init()
pygame.joystick.init()  # Initialize joystick module

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (700, 800)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

background_image = pygame.image.load("/Tetris Images/sky-clouds-cinematic-clouds-wallpaper-3_1562-740.jpeg")
background_image = pygame.transform.scale(background_image, size)

area_fill = pygame.image.load("/Tetris Images/sky-clouds-cinematic-clouds-wallpaper-3_1562-740.jpeg")
area_fill = pygame.transform.scale(area_fill, size)

welcome_text = pygame.sprite.GroupSingle()
welcome_text.add(Text(350, 50, "Welcome to Tetris!", 35, "black"))

custom_font_path = ("/coolvetica/coolvetica/Coolvetica Rg.otf")

done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

leaderboard_file = 'leaderboard.json'

if os.path.exists(leaderboard_file):
    with open(leaderboard_file, 'r') as f:
        leaderboard = json.load(f)
else:
    leaderboard = []

input_box = InputBox(250, 475, 200, 50)
input_active = False
player_name = ""

def save_leaderboard():
    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f, indent=4)




# Detect joysticks
joystick_count = pygame.joystick.get_count()
joysticks = []

for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)

# Assign controller button indices
MOVE_LEFT_AXIS = 0     # Left joystick horizontal
MOVE_RIGHT_AXIS = 0
MOVE_DOWN_AXIS = 1     # Left joystick vertical
ROTATE_BUTTON = 0      # Button for rotation (e.g., "A" on Xbox)
DROP_BUTTON = 1        # Button for dropping (e.g., "B" on Xbox)
MOVE_LEFT_BUTTON = 0   # Button for movinmg left on the dpad
MOVE_RIGHT_BUTTON = 0  # Button for moving right on the dpad
MOVE_DOWN_BUTTON = 1   # Button for moving down on the dpad 

# Initialize joystick movement flags
joystick_left_moved = False
joystick_right_moved = False

def handle_controller_input():
    global pressing_down, joystick_left_moved, joystick_right_moved
    
    for joystick in joysticks:
        # Axis movement (joystick)
        axis_x = joystick.get_axis(MOVE_LEFT_AXIS)
        axis_y = joystick.get_axis(MOVE_DOWN_AXIS)
    

        # Handle left/right movement
        if axis_x < -0.75 and not joystick_left_moved:  # Move left if joystick pushed left
            game.go_side(-1)  # Move left one square
            joystick_left_moved = True  # Set flag to avoid repeated movement
        elif axis_x > 0.75 and not joystick_right_moved:  # Move right if joystick pushed right
            game.go_side(1)  # Move right one square
            joystick_right_moved = True  # Set flag to avoid repeated movement

        # Reset the movement flags when joystick returns to neutral
        if -0.2 < axis_x < 0.2:
            joystick_left_moved = False
            joystick_right_moved = False

        # Handle down movement
        if axis_y > 0.5:
            pressing_down = True
        else:
            pressing_down = False

        # Button presses (rotation, drop)
        if joystick.get_button(ROTATE_BUTTON):
            game.rotate()  # Rotate the piece
        if joystick.get_button(DROP_BUTTON):
            game.go_space()  # Hard drop the piece
        if joystick.get_button(MOVE_LEFT_BUTTON):
            game.go_side (-1)
        if joystick.get_button(MOVE_RIGHT_BUTTON):
            game.go_side (1)     
        if joystick.get_button(MOVE_DOWN_BUTTON):
                pressing_down = True

while not done:
    if game.figure is None:
        game.new_figure()

    score_counter = pygame.sprite.GroupSingle()
    score_counter.add(Text(45, 45, "Score: " + str(game.score), 25, "black"))

    score_counter2 = pygame.sprite.GroupSingle()
    score_counter2.add (Text(350,700, "you have scored: "+ str(game.score), 25, "black")) 

    rotate_text = pygame.sprite.GroupSingle()
    rotate_text.add(Text(630, 685, "rotate = x", 25, "black"))

    controls_text0 = pygame.sprite.GroupSingle()
    controls_text0.add(Text(350,85, "Keyboard controls", 40, "black"))

    controls_text1 = pygame.sprite.GroupSingle()
    controls_text1.add(Text(350,125, "left = left arrow key", 40, "black"))

    controls_text2 = pygame.sprite.GroupSingle()
    controls_text2.add(Text(350,185, "right = right arrow key", 40, "black"))

    controls_text3 = pygame.sprite.GroupSingle()
    controls_text3.add(Text(350,235, "down = down arrow key", 40, "black"))

    controller_controls_text1 = pygame.sprite.GroupSingle()
    controller_controls_text1.add(Text(350,315, "controller controls", 40, "blue" ))

    controller_controls_text2 = pygame.sprite.GroupSingle()
    controller_controls_text2.add(Text(350,355, "left = left joystick/left dpad", 30, "blue" ))

    controller_controls_text3 = pygame.sprite.GroupSingle()
    controller_controls_text3.add(Text(350,395, "right = push jopystick right/ right dpad", 30, "blue" ))

    controller_controls_text4 = pygame.sprite.GroupSingle()
    controller_controls_text4.add(Text(350,435, "rotate = X/A", 30, "blue" ))

    controller_controls_text5 = pygame.sprite.GroupSingle()
    controller_controls_text5.add(Text(350,475, "straight down = O/B", 30, "blue" ))

    start_button = Button(300, 400, 100, 50, "green", 'Start', "black")
    quit_button = Button(300, 460, 100, 50, "red", 'Quit', "black")
    quit_button2 = Button(300, 610, 100, 50, "red", "Quit", "black")
    quit_button3 = Button(300,725, 100, 50, "red", "Quit", "black")
    paused_button = Button(300, 575, 100, 50, "yellow", "resume", "black")
    controls_button = Button(300,490,100,50, "green", "Controls","Black")
    controls_button2 = Button(300,590,100,50, "green", "Controls","Black")
    return_to_start_button = Button(300, 550, 100, 50, "blue", "Return", "white")
    return_from_playing_button = Button(300, 650, 100, 50, "blue", "Return", "white")
    return_from_controls_button = Button(250,635, 200, 50, "blue", "pause menu", "white" )
    main_menu_button = Button(275,715, 150, 50, "black", "main menu", "white")
    counter += 1

    if game.state == "playing":
        if counter > 100000:
            counter = 0

        if counter % (fps // game.level // 2) == 0 or pressing_down:
            game.go_down()

    for event in pygame.event.get():
        if game.state == "start":
            if start_button.is_clicked(event):
                game.state = "playing"
            if quit_button.is_clicked(event):
                done = True
            elif controls_button2.is_clicked(event):
                game.state = "controls"     

        elif game.state == "controls": 
            if paused_button.is_clicked(event):
                game.state = "playing"
            if return_from_controls_button.is_clicked(event):
                game.state = "paused"  
            if main_menu_button.is_clicked(event):
                game.state = "start"      

        

        elif game.state == "paused":
            if paused_button.is_clicked(event):
                game.state = "playing"
            elif return_from_playing_button.is_clicked(event):
                game.reset()
                game.state = "start"
            elif controls_button.is_clicked(event):
                game.state = "controls"      
            elif quit_button3.is_clicked(event):
                quit()

        elif game.state == "gameover":
            if return_to_start_button.is_clicked(event):
                game.reset()
                game.state = "start"
            if quit_button2.is_clicked(event):
                done = True
            player_input = input_box.handle_event(event)
            if player_input is not None:
                player_name = player_input
                leaderboard.append({'name': player_name, 'score': game.score})
                leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:5]
                save_leaderboard()
                game.reset()
                game.state = "start"
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_ESCAPE:
                game.state = "paused"
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

        # Handle controller input
        handle_controller_input()

    if game.state == "start":
        screen.blit(background_image, (0, 0))
        start_button.draw(screen)
        quit_button.draw(screen)
        welcome_text.draw(screen)
        controls_button2.draw(screen)

        leaderboard_text = pygame.sprite.Group()
        leaderboard_text.add(Text(350, 100, "Leaderboard", 35, "black"))
        for idx, entry in enumerate(leaderboard[:5]):
            leaderboard_text.add(Text(350, 150 + idx * 30, f"{entry['name']}: {entry['score']}", 25, "black"))
        leaderboard_text.draw(screen)
    else:
        screen.blit(background_image, (0, 0))
        overlay = pygame.Surface((700, 800))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        screen.blit(overlay, (0, 0))

        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                if game.field[i][j] > 0:
                    pygame.draw.rect(screen, colors[game.field[i][j]],
                                     [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, colors[game.figure.color],
                                         [game.x + game.zoom * (j + game.figure.x) + 1,
                                          game.y + game.zoom * (i + game.figure.y) + 1,
                                          game.zoom - 2, game.zoom - 2])

        if game.state == "playing":
            score_counter.draw(screen)
            rotate_text.draw(screen)

        paused_text = pygame.sprite.GroupSingle()
        paused_text.add(Text(350, 400, "game paused!", 40, "black"))

        if game.state == "paused":
            screen.fill(WHITE)
            paused_text.draw(screen)
            paused_button.draw(screen)
            return_from_playing_button.draw(screen)
            controls_button.draw(screen)
            quit_button3.draw(screen)

        gameover_text = pygame.sprite.GroupSingle()
        gameover_text.add(Text(350, 400, "Game over!! ", 40, "black"))

        gameover_text3 = pygame.sprite.GroupSingle()
        gameover_text3.add(Text(350, 450, "insert Name: ", 40, "black"))

        if game.state == "gameover":
            screen.blit(background_image, (0, 0))
            gameover_text.draw(screen)
            gameover_text3.draw(screen)
            score_counter2.draw(screen)
            input_box.draw(screen)
            quit_button2.draw(screen)
            return_to_start_button.draw(screen)

        if game.state == "controls":
            screen.fill(WHITE) 
            controls_text0.draw(screen) 
            controls_text1.draw(screen)
            controls_text2.draw(screen)
            controls_text3.draw(screen)
            controller_controls_text1.draw(screen)
            controller_controls_text2.draw(screen)
            controller_controls_text3.draw(screen)
            controller_controls_text4.draw(screen)
            controller_controls_text5.draw(screen)
            paused_button.draw(screen)
            return_from_controls_button.draw(screen)
            main_menu_button.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
