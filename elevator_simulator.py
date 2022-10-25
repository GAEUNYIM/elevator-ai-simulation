import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
# font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)

# reset
# reward
# play
# game_iteration
# is_collision

class Direction(Enum):
    UP = 1
    STAY = 0
    DOWN = -1

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

FLOORS = 4
ELEVATOR_WIDTH = 100
ELEVATOR_HEIGHT = 200
# BLOCK_SIZE = 20
SPEED = 20

class Agent:
    '''
        Agent Class
    '''
    def __init__(self, id, init_flr):
        self.agent_id = id # Agent id
        self.curr_flr = 0 # Where is it located currently?
        self.next_dest_flr = 0 # Which floor should agent visit next?
        self.visit_list = [] # Which floors should agent visit until the simulation ends?

    def _some_functions(self):
        pass


class EGCS:
    
    def __init__(self, w=400, h=800):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Elevator Group Control System')
        self.clock = pygame.time.Clock()
        self.start_ticks = pygame.time.get_ticks()
        self.temp_ticks = 0
        
        # init game state
        self.next_dest_flr = 0;#  direction = Direction.STAY
        
        # self.head = Point(self.w/2, self.h/2)
        # self.snake = [self.head, 
        #               Point(self.head.x-BLOCK_SIZE, self.head.y),
        #               Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.elevators = [1, 1] # List : Contains the location of elevators. Double-deck Elevator.
        self.hall_calls = [] # List : Contains the flag of hall calls. Binary
        self.reversed_hall_calls = [] # List : Reverse of hall_calls
        self.score = 0
        self.passenger = None
        self._init_hall_calls()
        
    
    def _init_hall_calls(self):
        for i in range(0, FLOORS-1):
            if i==0:
                self.hall_calls.append(0)
            self.hall_calls.append(random.randint(0,1))
        print("Hall calls: ", self.hall_calls)

    def _floor_to_point_agent(self, agent, floor):
        if agent == 0:
            x_align = 0
        elif agent == 1:
            x_align = 300

        return Point(x_align, 800-(floor*ELEVATOR_HEIGHT))

    def _floor_to_point_passenger(self, floor):
        x_align = 180

        return Point(x_align, 770-(floor*ELEVATOR_HEIGHT))
    
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         self.direction = Direction.LEFT
            #     elif event.key == pygame.K_RIGHT:
            #         self.direction = Direction.RIGHT
            #     elif event.key == pygame.K_UP:
            #         self.direction = Direction.UP
            #     elif event.key == pygame.K_DOWN:
            #         self.direction = Direction.DOWN
        
        # 2. move
        self._move(self.next_dest_flr) # update the head
        # self.snake.insert(0, self.head)
        
        # 3. check if game over
        # game_over = False
        # if self._is_collision():
        #     game_over = True
        #     return game_over, self.score
            
        # 4. place new passenger
        self._place_passenger()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        # return game_over, self.score

        return False, 0

    def _place_passenger(self):
        curr_ticks = pygame.time.get_ticks()
        print("ticks: ", curr_ticks)
        if (self.temp_ticks + 1000 < curr_ticks): # TODO : Poisson distribution should be applied.
            print("place_passenger()")
            rand_flr = random.randint(1, FLOORS-1)
            self.hall_calls[rand_flr] += 1
            self.temp_ticks = curr_ticks
        print("Hall calls: ", self.hall_calls)
        # y = rand_update_uiom.randint(0, 8)*ELEVATOR_HEIGHT
        # self.passenger = Point(x, y)
        # If passenger meets elevator, then 
            # allocate new passenger next time
        pass
    
    def _is_collision(self):
        # # hits boundary
        # if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
        #     return True
        # # hits itself
        # if self.head in self.snake[1:]:
        #     return True
        
        # return False
        pass
        
    def _update_ui(self):
        self.display.fill(WHITE)
        
        # for pt in self.snake:
        #     pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        #     pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        for agt, flr in enumerate(self.elevators):
            pt = self._floor_to_point_agent(agt, flr)
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, ELEVATOR_WIDTH, ELEVATOR_HEIGHT))

        for flr, psg in enumerate(self.hall_calls):
            pt = self._floor_to_point_passenger(flr)
            if flr == 0:
                text = font.render("GF", True, BLACK)
            else:
                text = font.render(str(psg), True, BLACK)
            self.display.blit(text, [pt.x, pt.y])

        # pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, BLACK)
        # time = font.render("TIME: " + str(self.clock), True, BLACK )
        self.display.blit(text, [0, 0])
        # self.display.blit(time, [0, 40])
        pygame.display.flip()
        pass

        
    def _move(self, dest_flr):
        self.next_dest_flr = self._get_flr_highest_hall_call()
        # x = self.head.x
        # y = self.head.y
        # if direction == Direction.RIGHT:
        #     x += BLOCK_SIZE
        # elif direction == Direction.LEFT:
        #     x -= BLOCK_SIZE
        # elif direction == Direction.DOWN:
        #     y += BLOCK_SIZE
        # elif direction == Direction.UP: 
        #     y -= BLOCK_SIZE
            
        # self.head = Point(x, y)
        return 1
        

    def _get_size_hall_calls(self):
        return len(self.hall_calls)

    def _get_flr_highest_hall_call(self):
        self.reversed_hall_calls = list(reversed(self.hall_calls))
        reversed_flr = 0
        highest_call_flr = 0
        while (reversed_flr != FLOORS):
            highest_call_flr = reversed_flr
            if (self.reversed_hall_calls[reversed_flr] != 0):
                break
            reversed_flr += 1
        return (FLOORS - 1) - highest_call_flr
            

if __name__ == '__main__':
    
    game = EGCS()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
    pygame.quit()