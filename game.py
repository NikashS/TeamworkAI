import random
import pygame
import sys
import math as pythonmath
from player import SoccerAgent
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
p1_num_passes = 0
p2_num_passes = 0

PASS_REWARD = 0.3
GOAL_REWARD = 1.0
FAIL_REWARD = -5.0
WAIT_REWARD = 0.0
HOLD_REWARD = 0.1
PASS_SHOT_REWARD = 5.0

DISPLAY = True

# randomness value
epsilon = 0.01
# learning rate
alpha = 0.3


fps = pygame.time.Clock()
pygame.init()
if DISPLAY:
    window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    pygame.display.set_caption("Soccer!")

def initialize():
    global goalie_pos, ball_pos, ball_vel, p1_num_passes, p2_num_passes
    # initialize goalie at goal with no velocity
    goalie_pos = GOAL_POS
    goalie_vel = [0, 0]
    # initialize ball at player one with no velocity
    ball_pos = PLAYER_ONE_POS
    ball_vel = [0, 0]
    # reset pass count
    p1_num_passes = 0
    p2_num_passes = 0

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

def ball_state():
    global ball_pos, goalie_pos

    epsilon = BALL_RADIUS
    if abs(ball_pos[1] - PLAYER_ONE_POS[1]) < epsilon:
        return "player_1"
    if abs(ball_pos[1] - PLAYER_TWO_POS[1]) < epsilon:
        return "player_2"
    dx, dy = goalie_pos[0] - ball_pos[0], goalie_pos[1] - ball_pos[1]
    if abs(dx) < 2*BALL_RADIUS and abs(dy) < 2*epsilon:
        return "goalie"
    if abs(ball_pos[0] - GOAL_POS[0]) < epsilon:
        return "goal"
    return None

def dist(pos1, pos2):
    return round(int(((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**0.5), -1)

def get_player_state(n = 1):
    global PLAYER_ONE_POS, PLAYER_TWO_POS, p1_num_passes, p2_num_passes
    pos = PLAYER_ONE_POS if n == 1 else PLAYER_TWO_POS
    passes = p1_num_passes if n == 1 else p2_num_passes
    return (
        ball_state() == ("player_" + str(n)), 
        dist(pos, goalie_pos),
        passes
        )

def update_ball(__passing, __shooting, __hold):
    # update ball position
    global ball_pos, ball_vel, goalie_pos, p1_num_passes, p2_num_passes, shooting, passing
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    if update_goalie():
        if p1_num_passes == 0 and p2_num_passes == 0:
            return ('TERMINAL_STATE', FAIL_REWARD*3)
        return ('TERMINAL_STATE', FAIL_REWARD)

    d1 = dist(goalie_pos, PLAYER_ONE_POS)
    d2 = dist(goalie_pos, PLAYER_TWO_POS)
    player_states = get_player_state(n=1), get_player_state(n=2)
    # current player chooses to hold
    if __hold:
        return player_states, HOLD_REWARD

    if __passing:
        if ball_pos == PLAYER_ONE_POS or ball_pos == PLAYER_TWO_POS:
            # if destination player is reached, set velocity to 0
            passing = False
            ball_vel = [0, 0]
            # must update passes
            if ball_pos == PLAYER_ONE_POS:
                s1 = (True, d1, p1_num_passes)
                s2 = (False, d2, p2_num_passes)
                return (s1, s2), PASS_REWARD
            # player two
            s1 = (False, d1, p1_num_passes)
            s2 = (True, d2, p2_num_passes)
            return (s1, s2), PASS_REWARD

    if __shooting:
        if abs(ball_pos[0] - GOAL_POS[0]) < BALL_RADIUS:
            # if ball reaches goal, set velocity to 0
            shooting = False
            if p1_num_passes > 0 or p2_num_passes > 0:
                return 'TERMINAL_STATE', PASS_SHOT_REWARD
            # define successful goal reward
            return 'TERMINAL_STATE', GOAL_REWARD
    
    return None

def pass_action():
    global ball_pos, ball_vel, passing, p1_num_passes, p2_num_passes
    # set passing variable
    passing = True
    epsilon = BALL_RADIUS
    if abs(ball_pos[1] - PLAYER_ONE_POS[1]) < epsilon:
        # if passing to player 2, set downward velocity
        p1_num_passes += 1
        ball_vel = [0, BALL_SPEED]
        ball_pos = [ball_pos[0], ball_pos[1]+BALL_SPEED]
    if abs(ball_pos[1] - PLAYER_TWO_POS[1]) < epsilon:
        # if passing to player 1, set upward velocity
        p2_num_passes += 1
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
        return True
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
    # goalie has not reached the ball
    return False

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

# initialize position variables
initialize()

# execute until program is quit
player1 = SoccerAgent(playerNum=1)
player2 = SoccerAgent(playerNum=2)

plays = 0
goals = 0
previous_action = None

# player states
p1_shooting, p2_shooting = False, False
p1_passing , p2_passing  = False, False
epochs, Ns, currentN = 0, [5000], 0
peek = None
prev_state = (None, None)
write_to_file = False

# file write
if Ns[len(Ns)-1] > 300: # only for meaningful data...
    file_name = "data_"
    for i in range(5):
        # generate random output 
        file_name += str(random.randint(0,9))
    file_name += ".txt"
    data_file = open(file_name, "w")
    print("Writing data to {0}".format(file_name))
    write_to_file = True
else:
    print("Not enough epochs--data not being saved")

while True:
    # display
    if DISPLAY:
        draw(window)
    """BEGIN EPISODIC CODE"""
    # if key is pressed or game is exited
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == QUIT:
            quitgame()
            # not necessary, but just in case
            data_file.close()
    
    s1, s2 = get_player_state(n=1), get_player_state(n=2)
    game_state = (s1, s2)

    # determine action
    action1 = player1.getAction(game_state[0])
    action2 = player2.getAction(game_state[1])
    
    action  = action1 if action1 != "wait" else action2
    hold = False
    # perform action 
    if possession() is not None:
        if action == "shoot":
            shoot_action()
            # player action states
            if action1 == "shoot":
                p1_shooting = True; p2_shooting = False
            else:
                p2_shooting = True; p1_shooting = False
        elif action == "pass" and previous_action != "shoot":
            pass_action()
            # player action states
            if action1 == "pass":
                p1_passing = True; p2_passing = False
            else:
                p2_passing = True; p1_passing = False
        else:
            hold = True
    
    previous_action = action
    step = update_ball(passing, shooting, hold)
    if step is not None:
        # reset game, terminal state
        if step[0] == "TERMINAL_STATE":
            reward = step[1]
            s1 = (False, dist(goalie_pos, PLAYER_ONE_POS), p1_num_passes)
            s2 = (False, dist(goalie_pos, PLAYER_TWO_POS), p2_num_passes)
            next_state = (s1, s2)

            if p1_shooting or p2_shooting:
                action1 = "shoot" if p1_shooting else "wait"
                action2 = "shoot" if p2_shooting else "wait"
                p1_shooting, p2_shooting = False, False
                assert action1 != action2, (action1, action2)
            elif p1_passing or p2_passing:
                action1 = "pass" if p1_passing else "wait"
                action2 = "pass" if p2_passing else "wait"
                p1_passing, p2_passing = False, False
                assert action1 != action2, (action1, action2)

            # update Q values
            player1.update(prev_state[0], action1, game_state[0], reward)
            player2.update(prev_state[1], action2, game_state[1], reward)
            plays += 1
            if reward == GOAL_REWARD or reward == PASS_SHOT_REWARD:
                # write to file
                if write_to_file:
                    data_file.write('1\n')
                goals += 1
            else:
                # write to file
                if write_to_file:
                    data_file.write('0\n')
            epochs += 1
            if epochs >= Ns[currentN]:
                # reset
                epochs = 0
                # print results
                print(str(Ns[currentN]) + " epochs: {0:.3f}".format(float(goals)/plays))
                goals = 0
                plays = 0
                currentN += 1
                # terminate
                if currentN >= len(Ns):
                    quitgame()
                # reset q values
                player1.reset()
                player2.reset()
            initialize()
        # basic 'living' reward (keeping the ball alive)
        else:
            if peek != (p1_num_passes, p2_num_passes):
                peek = (p1_num_passes, p2_num_passes)
                prev_state = game_state

    if DISPLAY:
        pygame.display.update()
    fps.tick(1000)