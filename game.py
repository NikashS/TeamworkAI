import random
import pygame
import sys
from pygame import *
from easygui import *

pygame.init()
fps = pygame.time.Clock()

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
ball_pos = [0, 0]
ball_vel = [0, 0]
goal_pos = [0, 0]
goalie_pos = [0, 0]
goalie_vel = [0, 0]

l_score = 0
r_score = 0
passing = False
shooting = False

window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption("Soccer!")

def ball_init():
    global ball_pos, ball_vel
    ball_pos = PLAYER_ONE_POS
    ball_vel = [0, 0]

def init():
    global goal_pos, goalie_pos# these are floats
    goal_pos = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    goalie_pos = goal_pos
    goalie_vel = [0, 0]
    ball_init()

def update_goalie():
    return
#     global goalie_pos, goalie_vel, ball_pos, ball_vel
#     x_difference = ball_pos[0] - goal_pos[0]
#     y_difference = ball_pos[1] - goal_pos[1]
#     goalie_vel = [int(x_difference / 100), int(y_difference / 100)]
#     goalie_pos = [goalie_pos[0] + goalie_vel[0], goalie_pos[1] + goalie_vel[1]]

def draw(canvas):
    global goal_pos, ball_pos, ball_vel, passing, shooting, goalie_pos

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(
        canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1
    )
    pygame.draw.circle(canvas, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    update_goalie()

    if passing:
        if ball_pos == PLAYER_ONE_POS or ball_pos == PLAYER_TWO_POS:
            passing = False
            ball_vel = [0, 0]

    if shooting:
        if abs(ball_pos[0] - goal_pos[0]) < BALL_RADIUS:
            shooting = False
            ball_vel = [0, 0]

    pygame.draw.polygon(
        canvas,
        GREEN,
        [
            [goal_pos[0] - HALF_PAD_WIDTH, goal_pos[1] - 8*HALF_PAD_HEIGHT],
            [goal_pos[0] - HALF_PAD_WIDTH, goal_pos[1] + 8*HALF_PAD_HEIGHT],
            [goal_pos[0] + HALF_PAD_WIDTH, goal_pos[1] + 8*HALF_PAD_HEIGHT],
            [goal_pos[0] + HALF_PAD_WIDTH, goal_pos[1] - 8*HALF_PAD_HEIGHT],
        ],
        0,
    )

    pygame.draw.circle(canvas, WHITE, PLAYER_ONE_POS, 15, 0)
    pygame.draw.circle(canvas, WHITE, PLAYER_TWO_POS, 15, 0)
    # pygame.draw.circle(canvas, RED, goalie_pos, 15, 0)
    pygame.draw.circle(canvas, ORANGE, ball_pos, 10, 0)


def keydown(event):
    global ball_pos, ball_vel, passing, shooting

    if event.key == K_p:
        passing = True
        if ball_pos == PLAYER_ONE_POS:
            ball_vel = [0, 5]
            ball_pos = [ball_pos[0], ball_pos[1]+5]
        if ball_pos == PLAYER_TWO_POS:
            ball_vel = [0, -5]
            ball_pos = [ball_pos[0], ball_pos[1]-5]
    if event.key == K_s:
        if ball_pos == PLAYER_ONE_POS or ball_pos == PLAYER_TWO_POS:
            shooting = True
            x_difference = goal_pos[0] - ball_pos[0]
            y_difference = goal_pos[1] - ball_pos[1]
            ball_vel = [int(x_difference / 75), int(y_difference / 75)]
            ball_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]
init()


while True:

    draw(window)

    for event in pygame.event.get():

        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fps.tick(60)