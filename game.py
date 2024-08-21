# Name: Jay Sikka
# ID: bmt7uk

# Description: I made a Mario game with the goal of getting the maximum amount of coins within the time limit and not
# dying. This Mario game mimics the layout of the typical 1-1 level in Super Mario Bros.

# Instructions: To play the game use the up, down, right, and left arrow keys to move and jump. The goal is to gain the
# maximum amount of coins without dying to the "Goombas" which spawn on the screen within the time limit amd reach
# the victory flag. Coins can be gained from question boxes and goombas

# 3 Basic Features:
# 1. User input: the user will use the keys to move Mario
# 2. Game over: the game over screen will
# pop up when Mario dies
# 3. Graphics/Images: The game will have images for all aspects of the game as it is a very
# important part of setting the scene for Mario

# 4 Additional Features:
# (Changed) 1. Enemies: There will be typical Mario enemies that try to stop his movement across the map
# (Changed) 2. Collectibles: There will be coins that Mario can collect with a score appearing on the top of the screen
# 3. Sprite animation: Mario will have sprite animation when he moves
# 4. Scrolling Level: The level will be larger than the screen and mario will be able to move around in it


import uvage
import random
import time

width = 800
height = 600

camera = uvage.Camera(width, height)

speed = 10


class Obstacle(): # class to store obstacle data including sprite and type of obstacle for use later in the code
    def __init__(self, x, y, t, img, scale = 1.0):
        self.type = t
        self.init_x = x
        self.init_y = y
        self.sprite = uvage.from_image(x, y, img)
        self.sprite.scale_by(scale)


def setup(): # setting up and initializing all the features of the game
    global mario, timer, timer_display, mario_images, mario_touching, mario_images_mirrored, background, ground, current_frame_right, current_frame_left, current_direction, obstacles, back_wall, move_screen, victory_flag, victory, game_over, coins, coins_display, timer, coin_list, enemies
    mario_images = uvage.load_sprite_sheet('images/mario1.png', 1, 12)
    mario_images_mirrored = uvage.load_sprite_sheet('images/mario2.png', 1, 12)

    mario = uvage.from_image(200, height / 2, mario_images[0])
    mario.scale_by(0.8)

    background = uvage.from_image(width / 2, height / 2 - 45, 'images/background_sky.png')
    background.scale_by(1.6)

    current_frame_left = 8 # initializing the animation for when mario is moving left
    current_frame_right = 0 # initializing the animation for when mario is moving right

    current_direction = "right" # the direction that mario is facing for animation
    # booleans for ending the game, scrolling the screen, and animation
    move_screen = False
    victory = False
    game_over = False
    mario_touching = True

    # starting number for coins and timer
    coins = 0
    timer = 600
    timer_display = uvage.from_text(100, 550, str(int(coins)), 50, 'white', True)

    back_wall = uvage.from_color(-10, height / 2, "black", 20, height + 20)

    coins_display = uvage.from_text(50,550,str(int(coins)),50,'white',True)

    # Making Various Obstacles

    ground = Obstacle(width / 2, height - 45,'ground', 'images/ground_ext.png',1.6)

    victory_flag = Obstacle(3000, height - 300, 'flag','images/victory_flag.png',2.5)
    brick6 = Obstacle(2850, height / 2 + (50), 'brick', 'images/brick.png', 0.2)
    brick4 = Obstacle(2700, height / 2 + (50), 'brick', 'images/brick.png', 0.2)
    brick5 = Obstacle(2750, height / 2 + (50), 'brick', 'images/brick.png', 0.2)
    question6 = Obstacle(2800, height / 2 + (50), "question", 'images/question.png', 0.2)


    question0 = Obstacle(500, height/2 + (50), "question",'images/question.png',0.2)

    brick1 = Obstacle(700, height/2 + (50),'brick','images/brick.png',0.2)
    question1 = Obstacle(750, height/2 + (50), "question", 'images/question.png',0.2)
    brick2 = Obstacle(800, height / 2 + (50),'brick','images/brick.png',0.2)
    question2 = Obstacle(850, height/2 + (50), "question",'images/question.png',0.2)
    brick3 = Obstacle(900, height / 2 + (50),'brick','images/brick.png',0.2)

    question3 = Obstacle(800, height/2 - (150), "question",'images/question.png',0.2)

    pipe1 = Obstacle(1520, height - 150, 'pipe','images/pipe.png', 0.38)
    pipe2 = Obstacle(2010, height - 150, 'pipe', 'images/pipe.png', 0.38)
    pipe3 = Obstacle(2510, height - 150, 'pipe', 'images/pipe.png', 0.38)

    # Making all initial enemies

    goomba1 = uvage.from_image(1000, height - 115, 'images/goomba.png')
    goomba1.scale_by(0.2)

    goomba2 = uvage.from_image(1200, height - 115, 'images/goomba.png')
    goomba2.scale_by(0.2)

    goomba4 = uvage.from_image(1400, height - 115, 'images/goomba.png')
    goomba4.scale_by(0.2)

    goomba5 = uvage.from_image(1600, height - 115, 'images/goomba.png')
    goomba5.scale_by(0.2)


    #list of enemies and coins for drawing and moving them
    coin_list = []
    enemies = [
        goomba1,
        goomba2,
        goomba4,
        goomba5
    ]

    #list of obstacles for moving when the screen moves and editing obstacles
    obstacles = [
        ground,
        victory_flag,
        pipe1,
        pipe2,
        pipe3,
        brick1,
        brick2,
        brick3,
        brick4,
        brick5,
        question6,
        brick6,
        question1,
        question2,
        question0,
        question3
    ]


def handle_mariox(): #handling the x movement of the main character mario
    global mario, obstacles, mario_touching, current_frame_right, current_frame_left, mario_images, mario_images_mirrored, current_direction, move_screen, ground

    #booleans for mario animation
    is_moving_left = False
    is_moving_right = False

    mario.speedx = 0

    # moving mario right and left at a constant speed
    if uvage.is_pressing('left arrow'):
        move_screen = False
        mario.speedx = -speed
        is_moving_left = True # for determining animation
        current_direction = "left"
    if uvage.is_pressing('right arrow'):
        if not move_screen:
            mario.speedx = speed
        is_moving_right = True # for determining animation
        current_direction = "right"

    if mario_touching:
        if is_moving_right: # changes animation based on which direction mario is facing while moving
            current_frame_right += 0.3 # increases based on frames
            if current_frame_right >= 4:
                current_frame_right = 1
            mario.image = mario_images[int(current_frame_right)]
        elif is_moving_left:
            current_frame_left += 0.3
            if current_frame_left >= 11:
                current_frame_left = 8
            mario.image = mario_images_mirrored[int(current_frame_left)]
        elif current_direction == "right": #changes jumping image
            mario.image = mario_images[0]
        else:
            mario.image = mario_images_mirrored[11]
    else: #changes standing image
        if current_direction == "right":
            mario.image = mario_images[5]
        else:
            mario.image = mario_images_mirrored[6]


def handle_marioy(): #handles jump movement and animation
    global mario, obstacles, mario_touching
    mario.speedy += 3 #moves mario at a speed down and increases for the gravity effect
    if mario_touching: #if mario is on the ground or on an obstacle
        mario.speedy = 0
        if uvage.is_pressing('up arrow'):
            mario.speedy = -35

    mario.move_speed()
    camera.draw(mario)


def handle_obstacles(): # manages movement of obstacles, enemies, and coins in the game
    global mario, obstacles, move_screen, back_wall, victory_flag, victory, mario_touching, coins, coin_list, enemies, game_over
    for c in coin_list: #handles the coin animation whenever mario gains a coin
        if c.sprite.y <= (c.init_y-50):
            coin_list.remove(c)
        else:
            c.sprite.y -= 5
        c.sprite.move_speed() # moves the coins up until they reach a certain x value
        camera.draw(c.sprite)

    for e in enemies: #draws enemies
        e.move_speed()
        camera.draw(e)

    mario.move_to_stop_overlapping(back_wall) #makes sure mario can't go backwards out of the camera
    mario_touching = True
    count = 0
    if mario.x >= victory_flag.sprite.x: # initiates victory sequence once mario reaches the flag
        victory = True
    for o in obstacles:
        i = o.sprite #defines sprite of obstacle object
        if mario.bottom_touches(i) and o != victory_flag: #if mario is touching any obstacle
            count += 1
        i.speedx = 0
        if o != victory_flag: # makes sure mario doesn't fall through obstacles
            mario.move_to_stop_overlapping(i)
        if o.type == 'question': #rules for if the obstacle is a question box
            if i.bottom_touches(mario):
                coins += 1 # increases coins by 1 if the question block is hit and runs the coin animation
                i.image = 'images/question2.png'
                o.type = 'question_used'
                new_coin = Obstacle(i.x,i.y,'coin','images/coin.png',0.1)
                coin_list.append(new_coin)
        # scrolls the screen once mario reaches halfway through the screen
        if mario.x >= width / 2 and uvage.is_pressing('right arrow'):
            move_screen = True
            mario.speedx = 0 #makes mario speed 0 so the illusion of the scrolling screen works
            i.speedx = -speed
            #changes speed of coins and enemies when the screen scrolls
            for c in coin_list:
                c.sprite.speedx = -speed
            for e in enemies:
                e.speedx = -(speed+4)
        else: #handles enemies/coins when screen is not scrolling
            move_screen = False
            for c in coin_list:
                c.sprite.speedx = 0
            for e in enemies:
                e.speedx = -4
        for e in enemies: # handles mario jumping on enemies
            if mario.bottom_touches(e): #spawns a new goomba once mario jumps on one
                if victory_flag.sprite.x > width: #spawns new goombas as long as mario has not reached the flag yet
                    coins += 1
                    new_coin = Obstacle(e.x, e.y, 'coin', 'images/coin.png', 0.1)
                    coin_list.append(new_coin)
                    time.sleep(0.25)
                    enemies.remove(e)
                    goomba3 = uvage.from_image(width + 100, height - 115, 'images/goomba.png')
                    goomba3.scale_by(0.2)
                    enemies.append(goomba3)
            elif e.x < -20: # spawns a new goomba when it leaves the screen
                if victory_flag.sprite.x > width:
                    enemies.remove(e)
                    goomba3 = uvage.from_image(width + 100, height - 115, 'images/goomba.png')
                    goomba3.scale_by(0.2)
                    enemies.append(goomba3)
            if mario.left_touches(e) or mario.right_touches(e):
                game_over = True

        i.move_speed()
        camera.draw(i)
    if count == 0: #defines if mario is touching the ground
        mario_touching = False


def handle_scores(): #handles timer and score of coins
    global coins_display, coins, timer, timer_display, game_over
    if not game_over: #decreases time as long as the game is running
        timer -= 1
    #displays coins and timer sprites
    coins_display2 = uvage.from_image(720,50,'images/coin.png')
    timer_display2 = uvage.from_image(635,50,'images/timer.png')
    coins_display2.scale_by(0.08)
    timer_display2.scale_by(0.12)
    coins_display = uvage.from_text(750,50,str(int(coins)),50,'white',True)
    timer_display = uvage.from_text(675,50,str(int(timer/30)),50,'white',True)
    #changes alignment of timer and coins when it is double/single digits
    if coins >= 10:
        coins_display2.x = 715
    if timer <= 9:
        timer_display2.x = 645
    camera.draw(timer_display)
    camera.draw(timer_display2)
    camera.draw(coins_display)
    camera.draw(coins_display2)



def handle_background(): #draws background
    global background, mario
    camera.draw(background)


def handle_victory(): #draws a victory screen if mario reaches the end
    camera.draw(uvage.from_text(width / 2, height / 2, "Victory!", 135, "green"))


def handle_game_over():
    global mario, mario_images, ground, timer
    mario.image = mario_images[6] #draws a mario dying animation
    if mario.x < height+100: #animates mario dying and falling off the screen
        mario.y += 7
    handle_background() #draws background
    camera.draw(ground.sprite)
    camera.draw(mario)
    handle_scores() #draws score
    camera.draw(uvage.from_text(width / 2, height / 2, "Game Over", 135, "red"))


def tick(): #runs all functions defined above
    global victory, game_over, timer
    if victory: #handles victory
        handle_victory()
    elif game_over or timer < 1: #handles game over
        game_over = True
        handle_game_over()
    else: #runs all other functions of the game is running
        handle_background()
        handle_obstacles()
        handle_scores()
        handle_mariox()
        handle_marioy()

    camera.display()


setup()
uvage.timer_loop(30, tick)
