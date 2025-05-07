import pyglet
import time
from pyglet import window, shapes
from DIPPID import SensorUDP
import os

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

#Player
PLAYER_WIDTH = 175
PLAYER_HEIGHT = 15
player = shapes.Rectangle(40, 30, PLAYER_WIDTH, PLAYER_HEIGHT, (255, 0, 0))
player_y_gravity = 0
PLAYER_MAX_SCREEN_POSITION = WINDOW_WIDTH - player.width
PLAYER_MAX_NEGATIVE_GRAVITY = -6
PLAYER_MAX_POSITIVE_GRAVITY = 6
PLAYER_MAX_LIVES = 3
player_lives = PLAYER_MAX_LIVES

#Ball
BALL_WIDTH = 10
BALL_START_X = 345
BALL_START_Y = 80
ball = shapes.Rectangle(BALL_START_X, BALL_START_Y, BALL_WIDTH, BALL_WIDTH, (0, 0, 255))
ball_x_speed = 0
ball_y_speed = 0
BALL_START_SPEED = 3
BALL_MAX_SPEED = 15

#Time for the speedup of ball
start_time = time.time()
SPEEDUP_TIME_INCREMENT = 30

#Bricks
BRICK_WIDTH = 40
BRICK_HEIGHT = 20
NUM_OF_ROWS = WINDOW_WIDTH / BRICK_WIDTH
NUM_OF_COLUMN = 10
BRICK_OFFSET_FROM_GROUND = 350
brick_array = [[], [], [], [], [], [], [], [], [], []]
brick1_img = pyglet.image.load("2d_game/brick1.png")
brick2_img = pyglet.image.load("2d_game/brick2.png")
brick3_img = pyglet.image.load("2d_game/brick3.png")
brick4_img = pyglet.image.load("2d_game/brick4.png")
brick5_img = pyglet.image.load("2d_game/brick5.png")
brick6_img = pyglet.image.load("2d_game/brick6.png")
brick7_img = pyglet.image.load("2d_game/brick7.png")
brick8_img = pyglet.image.load("2d_game/brick8.png")
brick9_img = pyglet.image.load("2d_game/brick9.png")
brick10_img = pyglet.image.load("2d_game/brick10.png")
batch = pyglet.graphics.Batch()

#Score
current_score = 0
MAX_SCORE = NUM_OF_COLUMN * NUM_OF_ROWS

#UI
label_score = pyglet.text.Label("Bricks remaining: " + str(int(MAX_SCORE-current_score)), font_name="Times New Roman", x=WINDOW_WIDTH-100, y=WINDOW_HEIGHT-20, anchor_x="center", anchor_y="center", font_size=14)
label_lives = pyglet.text.Label("Lives remaining: "+ str(int(player_lives)), font_name="Times New Roman", x=10, y=WINDOW_HEIGHT-20, anchor_x="left", anchor_y="center", font_size=14)
label_restart_hint = pyglet.text.Label("Press R to restart the game and P to end the game.", font_name="Times New Roman", x=WINDOW_WIDTH/2, y=WINDOW_HEIGHT-20, anchor_x="center", anchor_y="center", font_size=14)
game_won = False

def initialize_bricks():
    global brick_array
    brick_array.clear()
    brick_array = [[], [], [], [], [], [], [], [], [], []]
    for x in range(int(NUM_OF_COLUMN)):
        for y in range(int(NUM_OF_ROWS)):
            brick_array[x].append(pyglet.sprite.Sprite(get_brick_color(x), y*BRICK_WIDTH, x*BRICK_HEIGHT + BRICK_OFFSET_FROM_GROUND, batch=batch))

def get_brick_color(x):
    if x == 0:
        return brick1_img
    if x == 1:
        return brick2_img
    if x == 2:
        return brick3_img
    if x == 3:
        return brick4_img
    if x == 4:
        return brick5_img
    if x == 5:
        return brick6_img
    if x == 6:
        return brick7_img
    if x == 7:
        return brick8_img
    if x == 8:
        return brick9_img
    if x == 9:
        return brick10_img
    else:
        return brick1_img

def calculate_ball():
    global ball_x_speed, ball_y_speed, start_time, brick_array, current_score, player_lives

    #duplicate ball with the next frame's position to use with collision computation
    collision_ball = shapes.Rectangle(ball.x + ball_x_speed, ball.y + ball_y_speed, BALL_WIDTH, BALL_WIDTH, (0,0,0))

    #check if the ball collides with a wall
    if ball_x_speed > 0 and ball.x + BALL_WIDTH + ball_x_speed >= WINDOW_WIDTH:
        ball_x_speed *= -1
    if ball_x_speed < 0 and ball.x + ball_x_speed <= 0:
        ball_x_speed *= -1
    if ball_y_speed > 0 and ball.y + BALL_WIDTH + ball_y_speed >= WINDOW_HEIGHT:
        ball_y_speed *= -1
    if ball_y_speed < 0 and ball.y + ball_y_speed <= -5:
        if player_lives == 0:
            initialize_game() #restart the game
        else:
            player_lives -= 1
            label_lives.text = "Lives remaining: " + str(int(player_lives))
            initialize_ball()

    #check if the ball collides with the player
    if check_rectangle_overlap(collision_ball, player):
        if abs(ball.y - (player.y + PLAYER_HEIGHT)) < abs(ball_x_speed):
            ball_y_speed *= -1
        else:
            ball_x_speed *= -1
        
    #check if the ball collides with the bricks
    bricks_to_be_removed = []
    for row_index, x in enumerate(brick_array):
        for col_index, y in enumerate(x):
            if y is not None and check_rectangle_overlap(collision_ball, y):
                if abs(ball.y + BALL_WIDTH - y.y) < abs(ball_x_speed) or abs(ball.y - (y.y + BRICK_HEIGHT)) < abs(ball_x_speed):
                    ball_y_speed *= -1
                else:
                    ball_x_speed *= -1
                bricks_to_be_removed.append((row_index, col_index))
                break
    for a, b in bricks_to_be_removed:
        brick_array[a][b] = None
        current_score += 1
        check_win_condition()
        if game_won is False:
            label_score.text = "Bricks remaining: " + str(int(MAX_SCORE-current_score))
        else:
            label_score.text = "YOU WON!"

    #check whether the ball should speed up, up to a maximum
    if start_time < time.time() - SPEEDUP_TIME_INCREMENT:
        if ball_x_speed > 0 and ball_x_speed < BALL_MAX_SPEED:
            ball_x_speed += 1
        if ball_x_speed < 0 and ball_x_speed > BALL_MAX_SPEED * -1: 
            ball_x_speed -= 1
        if ball_y_speed > 0 and ball_y_speed < BALL_MAX_SPEED:
            ball_y_speed += 1
        if ball_y_speed < 0 and ball_y_speed > BALL_MAX_SPEED * -1:
            ball_y_speed -= 1
        print("Speedup: " + str(ball_x_speed))
        start_time = time.time()

    #Move the ball
    ball.x += ball_x_speed
    ball.y += ball_y_speed

#checks whether two rectangles overlap
def check_rectangle_overlap(rect1, rect2):
    return (
        rect1.x < rect2.x + rect2.width and
        rect1.x + rect1.width > rect2.x and
        rect1.y < rect2.y + rect2.height and
        rect1.y + rect1.height > rect2.y
    )

def check_win_condition():
    global current_score, ball_x_speed, ball_y_speed, game_won
    if current_score == MAX_SCORE:
        ball_x_speed = 0
        ball_y_speed = 0
        game_won = True

def draw_bricks():
    global brick_array
    for x in brick_array:
        for y in x:
            if y is not None:
                y.draw()


def handle_acc(data):
    player_y_gravity = data['y']

    #Rounds the y value to two decimal values, for simplicity
    target_player_y = round(player_y_gravity, 2)

    #Makes the value adhere to set boundaries, so players do not have to fully tilt their phones
    if target_player_y < PLAYER_MAX_NEGATIVE_GRAVITY:
        target_player_y = PLAYER_MAX_NEGATIVE_GRAVITY
    if target_player_y > PLAYER_MAX_POSITIVE_GRAVITY:
        target_player_y = PLAYER_MAX_POSITIVE_GRAVITY
    
    #Shifts the gravity value from negative to 0-whateverTheEntireRangeIs
    target_player_y += (PLAYER_MAX_NEGATIVE_GRAVITY * -1)
    full_range = PLAYER_MAX_POSITIVE_GRAVITY + (PLAYER_MAX_NEGATIVE_GRAVITY * -1)

    #Calculate the percentage of movement from the phone's y gravity, and apply it to the player's x position
    gravity_percentage = target_player_y / full_range
    player.x = PLAYER_MAX_SCREEN_POSITION * gravity_percentage

def initialize_game():
    global current_score, player_lives
    initialize_bricks()
    initialize_ball()
    current_score = 0
    player_lives = PLAYER_MAX_LIVES
    initialize_ui()

def initialize_ball():
    global ball_x_speed, ball_y_speed
    ball.x = BALL_START_X
    ball.y = BALL_START_Y
    ball_x_speed = BALL_START_SPEED
    ball_y_speed = BALL_START_SPEED

def initialize_ui():
    label_lives.text = "Lives remaining: " + str(int(player_lives))
    label_score.text = "Bricks remaining: " + str(int(MAX_SCORE-current_score))

sensor.register_callback('gravity', handle_acc)
initialize_game()
print(os.getcwd())

@win.event
def on_key_press(symbol, modifiers):
    if symbol == window.key.R:
        initialize_game()
    if symbol == window.key.P:
        os._exit(0)

@win.event
def on_draw():
    win.clear()
    player.draw()
    calculate_ball()
    ball.draw()
    #draw_bricks()
    batch.draw()
    label_score.draw()
    label_lives.draw()
    label_restart_hint.draw()

pyglet.app.run()
