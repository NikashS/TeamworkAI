import random
import pygame
import sys
import math as pythonmath
from pygame import *
from easygui import *

# constant parameters
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WIDTH = 1000
HEIGHT = 800
BALL_RADIUS = 10
PAD_WIDTH = 10
PAD_HEIGHT = 10
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
PLAYER_ONE_POS = [WIDTH // 4, HEIGHT // 4]
PLAYER_TWO_POS = [WIDTH // 4, 3 * (HEIGHT // 4)]
GOAL_POS = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
GOALIE_SPEED = 7
BALL_SPEED = 10

# variables
ball_pos = [0, 0]
ball_vel = [0, 0]
goalie_pos = [0, 0]
goalie_vel = [0, 0]
passing = False
shooting = False

# q learning variables

# (state, action): q-value
# True state means has ball
one_values = {
    (True, "pass"): 0.0,
    (True, "shoot"): 0.0,
    (True, "hold"): 0.0,
    (False, "wait"): 0.0
}
two_values = {
    (True, "pass"): 0.0,
    (True, "shoot"): 0.0,
    (True, "hold"): 0.0,
    (False, "wait"): 0.0
}
transitions = {
    (True, "pass"): False,
    (True, "shoot"): False,
    (True, "hold"): True,
    (False, "wait"): False
}

# state: valid actions
# True state means has ball
valid_actions = {
    True: ["pass", "shoot", "hold"],
    False: ["wait"]
}

# randomness value
epsilon = 0.1
# learning rate
alpha = 0.2

pygame.init()
fps = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption("Soccer!")

def initialize():
    global goalie_pos, ball_pos, ball_vel
    # initialize goalie at goal with no velocity
    goalie_pos = GOAL_POS
    goalie_vel = [0, 0]
    # initialize ball at player one with no velocity
    ball_pos = PLAYER_ONE_POS
    ball_vel = [0, 0]

def possession():
    # returns player position who is in possession of the ball
    global ball_pos
    pos = None
    epsilon = BALL_RADIUS
    if abs(ball_pos[1] - PLAYER_ONE_POS[1]) < epsilon:
        pos = PLAYER_ONE_POS
    elif abs(ball_pos[1] - PLAYER_TWO_POS[1]) < epsilon:
        pos = PLAYER_TWO_POS
    return pos

def update_ball(passing, shooting):
    # update ball position
    global ball_pos, ball_vel
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    if passing:
        if ball_pos == PLAYER_ONE_POS or ball_pos == PLAYER_TWO_POS:
            # if destination player is reached, set velocity to 0
            passing = False
            ball_vel = [0, 0]
            # define successful pass reward
    if shooting:
        if abs(ball_pos[0] - GOAL_POS[0]) < BALL_RADIUS:
            # if ball reaches goal, set velocity to 0
            shooting = False
            initialize()
            # define successful goal reward

def pass_action():
    global ball_pos, ball_vel, passing
    # set passing variable
    passing = True
    epsilon = BALL_RADIUS
    if abs(ball_pos[1] - PLAYER_ONE_POS[1]) < epsilon:
        # if passing to player 2, set downward velocity
        ball_vel = [0, BALL_SPEED]
        ball_pos = [ball_pos[0], ball_pos[1]+BALL_SPEED]
    if abs(ball_pos[1] - PLAYER_TWO_POS[1]) < epsilon:
        # if passing to player 1, set upward velocity
        ball_vel = [0, -BALL_SPEED]
        ball_pos = [ball_pos[0], ball_pos[1]-BALL_SPEED]

def shoot_action():
    global ball_pos, ball_vel, shooting
    # returns null if no one is possession of the ball
    player_position = possession()
    if player_position:
        # only allow shot if player has ball
        # set shooting variable
        shooting = True
        x_difference = GOAL_POS[0] - player_position[0]
        y_difference = GOAL_POS[1] - player_position[1]

        # update velocity towards goal, assign arbitrary increment (adjust to change speed)
        ball_vel = [int(x_difference / 50), int(y_difference / 50)]
        ball_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]

def update_goalie():
    global goalie_pos, goalie_vel, ball_pos, ball_vel
    dx, dy = goalie_pos[0] - ball_pos[0], goalie_pos[1] - ball_pos[1]
    if abs(dx) < 2*BALL_RADIUS and abs(dy) < 2*BALL_RADIUS:
        # if goalie reaches ball
        initialize()
    else:
        # update velocity towards ball position (adjust to change speed)
        xdir = -1 if dx >= 0 else 1
        ydir = -1 if dy >= 0 else 1
        if dx == 0:
            v_x, v_y = 0, GOALIE_SPEED * ydir
        else:
            v_x, v_y = GOALIE_SPEED * abs(pythonmath.cos(dy/dx)) * xdir, \
                       GOALIE_SPEED * abs(pythonmath.sin(dy/dx)) * ydir
        goalie_vel = [v_x, v_y]
    goalie_pos = [goalie_pos[0]+goalie_vel[0], goalie_pos[1]+goalie_vel[1]]

def draw(canvas):
    global ball_pos, goalie_pos

    # draw background
    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

    # draw goal
    pygame.draw.polygon(
        canvas,
        GREEN,
        [
            [GOAL_POS[0] - HALF_PAD_WIDTH, GOAL_POS[1] - 8*HALF_PAD_HEIGHT],
            [GOAL_POS[0] - HALF_PAD_WIDTH, GOAL_POS[1] + 8*HALF_PAD_HEIGHT],
            [GOAL_POS[0] + HALF_PAD_WIDTH, GOAL_POS[1] + 8*HALF_PAD_HEIGHT],
            [GOAL_POS[0] + HALF_PAD_WIDTH, GOAL_POS[1] - 8*HALF_PAD_HEIGHT],
        ],
        0,)

    # draw players
    pygame.draw.circle(canvas, WHITE, PLAYER_ONE_POS, 15, 0)
    pygame.draw.circle(canvas, WHITE, PLAYER_TWO_POS, 15, 0)

    # draw goalie
    goalie_pos = [int(goalie_pos[0]), int(goalie_pos[1])]
    pygame.draw.circle(canvas, RED, goalie_pos, 15, 0)

    # draw ball
    pygame.draw.circle(canvas, ORANGE, ball_pos, 10, 0)

def quitgame():
    pygame.display.quit()
    pygame.quit()
    sys.exit()

def keydown(event):
    # if "p" key is pressed, execute pass action
    if event.key == K_p:
        pass_action()
    # if "s" key is pressed, execute shoot action
    if event.key == K_s:
        shoot_action()
    # if "x" key is pressed, exit game
    if event.key == K_x:
        quitgame()

# q learning methods

def getQValue(state, action):
    global one_values, two_values
    if PLAYER_ONE_POS == possession():
        return one_values[(state, action)]
    else:
        return two_values[(state, action)]

def computeValueFromQValues(state):
    global valid_actions
    actions = valid_actions[state]
    max_value = float("-inf")
    for action in actions:
        if getQValue(state, action) > max_value:
            max_value = getQValue(state, action)
    return max_value

def computeActionFromQValues(state):
    global valid_actions
    actions = valid_actions[state]
    max_value = float("-inf")
    best_action = None
    for action in actions:
        if getQValue(state, action) > max_value:
            max_value = getQValue(state, action)
            best_action = action
    return best_action

def getAction(state):
    global valid_actions, epsilon
    actions = valid_actions[state]
    chosen_action = None
    if random.random() < epsilon:
        chosen_action = random.choice(actions)
    else:
        chosen_action = computeActionFromQValues(state)
    return chosen_action

def update(state, action, next_state, reward):
    global valid_actions, alpha
    updated = ((1 - alpha) * getQValue(state, action)) + (alpha * (reward + computeValueFromQValues(next_state)))
    if PLAYER_ONE_POS == possession():
        one_values[(state, action)] = updated
    else:
        two_values[(state, action)] = updated

# initialize position variables
initialize()

# execute until program is quit
while True:
    draw(window)
    update_ball(passing, shooting)
    update_goalie()

    # if key is pressed or game is exited
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == QUIT:
            quitgame()

    pygame.display.update()
    fps.tick(50)