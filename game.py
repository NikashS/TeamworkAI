import random
import pygame
import sys
from pygame import *
from easygui import *

# constant parameters
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 10
PAD_WIDTH = 10
PAD_HEIGHT = 10
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
PLAYER_ONE_POS = [WIDTH // 4, HEIGHT // 4]
PLAYER_TWO_POS = [WIDTH // 4, 3 * (HEIGHT // 4)]
GOAL_POS = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]

# variables
ball_pos = [0, 0]
ball_vel = [0, 0]
goalie_pos = [0, 0]
goalie_vel = [0, 0]
passing = False
shooting = False

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
            ball_vel = [0, 0]
            # define successful goal reward

def pass_action():
    global ball_pos, ball_vel, passing
    # set passing variable
    passing = True
    if ball_pos == PLAYER_ONE_POS:
        # if passing to player 2, set downward velocity
        ball_vel = [0, 5]
        ball_pos = [ball_pos[0], ball_pos[1]+5]
    if ball_pos == PLAYER_TWO_POS:
        # if passing to player 1, set upward velocity
        ball_vel = [0, -5]
        ball_pos = [ball_pos[0], ball_pos[1]-5]

def shoot_action():
    global ball_pos, ball_vel, shooting
    if ball_pos == PLAYER_ONE_POS or ball_pos == PLAYER_TWO_POS:
        # only allow shot if player has ball
        # set shooting variable
        shooting = True
        x_difference = GOAL_POS[0] - ball_pos[0]
        y_difference = GOAL_POS[1] - ball_pos[1]
        # update velocity towards goal, assign arbitrary increment (adjust to change speed)
        ball_vel = [int(x_difference / 75), int(y_difference / 75)]
        ball_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]

def update_goalie():
    global goalie_pos, goalie_vel, ball_pos, ball_vel
    x_difference = ball_pos[0] - GOAL_POS[0]
    y_difference = ball_pos[1] - GOAL_POS[1]
    goalie_vel = [int(x_difference / 100), int(y_difference / 100)]
    goalie_pos = [goalie_pos[0] + goalie_vel[0], goalie_pos[1] + goalie_vel[1]]

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
    pygame.draw.circle(canvas, RED, goalie_pos, 15, 0)

    # draw ball
    pygame.draw.circle(canvas, ORANGE, ball_pos, 10, 0)


def keydown(event):
    # if "p" key is pressed, execute pass action
    if event.key == K_p:
        pass_action()
    # if "s" key is pressed, execute shoot action
    if event.key == K_s:
        shoot_action()

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
            pygame.display.quit()
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fps.tick(60)