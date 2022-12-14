import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
# font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 12)

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

# User defined variables
UI_WIDTH = 400
UI_HEIGHT = 800

FLOORS = 8
AGENTS = 2

ELEVATOR_WIDTH = 100
ELEVATOR_HEIGHT = UI_HEIGHT / FLOORS
SPEED = 10

class Elevator:
    '''
        Elevator agent Class
    '''
    def __init__(self, id, init_flr):
        self.agent_id = id # Agent id
        self.curr_flr = 0 # Where is it located currently?
        self.next_dest_flr = 0 # Which floor should agent visit next?
        self.visit_list = [] # Which floors should agent visit until the simulation ends?

    def _some_functions(self):
        pass


class EGCS:
    '''
        Elevator Group Control System (Solving problem)
    '''
    
    def __init__(self, w=400, h=800):
        # Set width and height
        self.w = w
        self.h = h

        # initialize display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Elevator Group Control System')
        self.clock = pygame.time.Clock()
        self.start_ticks = pygame.time.get_ticks()
        self.temp_ticks = 0
        
        # init game state
        self.next_dest_flr = 0; #  direction = Direction.STAY
        
        self.state_elevators = [1, 1] # List : Contains the location of elevators. Double-deck Elevator.
        self.state_directions = [0, 0] # List : Contains the direction of elevators.
        self.state_hall_calls = [] # List : Contains the flag of hall calls. Binary
        self.flag_hall_calls = []
        self.reversed_hall_calls = [] # List : Reverse of hall_calls

        self.queue_syst = []
        self.queue_elv1 = []
        self.queue_elv2 = []

        self.cnt_passengers_elv1 = 0
        self.cnt_passengers_elv2 = 0

        self.score = 0
        self.arrived_passengers = 0
        self._init_hall_calls()
    
    
    def _init_hall_calls(self):
        for i in range(0, FLOORS):
            self.state_hall_calls.append(0)
            self.flag_hall_calls.append(0)
            # if i==0:
            #     self.state_hall_calls.append(0)
            # self.state_hall_calls.append(random.randint(0,1))
        print("Hall calls: ", self.state_hall_calls)

    def _convert_flr_to_elevator_pivot(self, agent, floor):
        if agent == 0:
            x_align = 0
        elif agent == 1:
            x_align = UI_WIDTH - ELEVATOR_WIDTH

        return Point(x_align, UI_HEIGHT-(floor*ELEVATOR_HEIGHT))

    def _convert_flr_to_passenger_pivot(self, floor):
        x_align = UI_WIDTH / 2 - 10

        return Point(x_align, (UI_HEIGHT-30)-(floor*ELEVATOR_HEIGHT))
    
        
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
        
        # 2. place new passenger
        self._place_passenger()

        self._move()

        self._onboard()

        self._deliever()

        self._outboard()
        
        # 3. check if game over
        # game_over = False
        # if self._is_collision():
        #     game_over = True
        #     return game_over, self.score
        
        # 4. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        # return game_over, self.score

        return False, 0

    def _place_passenger(self):
        curr_ticks = pygame.time.get_ticks()
        print("ticks: ", curr_ticks)
        if (self.temp_ticks + 100 < curr_ticks): # TODO : Poisson distribution should be applied.
            print("place_passenger()")
            rand_flr = random.randint(2, FLOORS)
            self.state_hall_calls[rand_flr-1] += 1
            self.flag_hall_calls[rand_flr-1] = 1
            self.temp_ticks = curr_ticks
        # self._assign_highest_first()
        self._assign()
    
    def _is_collision(self):
        # # hits boundary
        # if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
        #     return True
        # # hits itself
        # if self.head in self.snake[1:]:
        #     return True
        
        # return False
        pass

    def _assign_flr_to_elv(self, elvid, flr):
        if elvid == 1:
            self.queue_elv1.append(flr)
            self.queue_elv1.sort(reverse=True)
            for f in self.queue_elv1:
                if f > self.state_elevators[0]:
                    self.queue_elv1.remove(f)
                    self.queue_elv1.append(f)
        elif elvid == 2:
            self.queue_elv2.append(flr)
            self.queue_elv2.sort(reverse=True)
            for f in self.queue_elv2:
                if f > self.state_elevators[0]:
                    self.queue_elv2.remove(f)
                    self.queue_elv2.append(f)
        else:
            print("WATCH OUT")

    def _assign_flr_to_sys(self, elv, flr):
        '''
        Assign the input flr into the appropriate elv regarding the state of system.
        '''  
        if flr == 0 or elv ==0:
            return

        # Assign
        if elv == 1:
            if flr not in self.queue_elv1:
                self.queue_elv1.append(flr)
                self.queue_elv1.sort()
                for f in self.queue_elv1:
                    if f > self.state_elevators[0]:
                        self.queue_elv1.remove(f)
                        self.queue_elv1.append(f)
                # self.flag_hall_calls[flr-1] = 0
        elif elv == 2:
            if flr not in self.queue_elv2:
                self.queue_elv2.append(flr)
                self.queue_elv2.sort()
                for f in self.queue_elv2:
                    if f > self.state_elevators[1]:
                        self.queue_elv2.remove(f)
                        self.queue_elv2.append(f)
                # self.flag_hall_calls[flr-1] = 0
        else:
            print("WATCH OUT")

    def _assign(self):
        '''
        1. Select flr to visit next.
        2. Assign appropriate elv to visit there.

        '''
        # self._assign_next_visit_flr()
        self._assign_highest_first()

        print("===== information =====")
        print("self.state_hall_calls : ", self.state_hall_calls)
        print("self.flag_hall_calls : ", self.flag_hall_calls)
        print("self.state_elevators : ", self.state_elevators)
        print("self.state_directions : ", self.state_directions)

        print("get highest hall call flr: ", self._get_highest_hall_call_flr())
        print("queue_elv1 : ", self.queue_elv1)
        print("queue_elv2 : ", self.queue_elv2)
        
        print("Total arrived passengers : ", self.arrived_passengers)

    def _assign_next_visit_flr(self):
        '''_assign_flr_to_elv
        Return the floor should be visit next. Update every ticks.
        '''
        # Should be designed in detail..!!

        state_elv1 = self.state_elevators[0]
        state_elv2 = self.state_elevators[1]
        # Case 1. Both elevators are on the GF.
        if state_elv1 == 1 and state_elv2 == 1:
            next_visit_flr = self._get_highest_hall_call_flr()
            self._assign_flr_to_sys(1, next_visit_flr)

        # Case 2. One of the elevators is on the GF, one is moving.
        # Case 2-1. Elv2 is moving.
        elif state_elv1 == 1 and state_elv2 != 1: 

            # Case 2-1-1. Check whether there is request below elv2.
            next_visit_flr_below = self._return_request_below_flr(state_elv2)

            # If there exists request below elv2, then push it into a queue.
            if next_visit_flr_below != 0:
                next_visit_flr = next_visit_flr_below
                closer_elvid = self._get_closest_elevator_with_flr(next_visit_flr)
                self._assign_flr_to_elv(closer_elvid, next_visit_flr)
            # If there are no request below elv2, then go to the 1st flr
            # else:
            #     next_visit_flr = 1
            #     self._assign_flr_to_elv(2, next_visit_flr)

            # Case 2-1-2. Check whether there is request above elv2.
            next_visit_flr_above = self._return_request_above_flr(state_elv2)

            # If there exists request above elv2, then assign it to elv1.
            if next_visit_flr_above != 0:
                next_visit_flr = next_visit_flr_below
                self._assign_flr_to_elv(1, next_visit_flr)
            
        
        # Case 2-2. Elv1 is moving.
        elif state_elv1 != 1 and state_elv2 == 1: 

            # Case 2-2-1. Check whether there is request below elv1. 
            next_visit_flr_below = self._return_request_below_flr(state_elv1)

            # If there exists request below elv1, then push it into a queue.
            if next_visit_flr_below != 0:
                next_visit_flr = next_visit_flr_below
                closer_elvid = self._get_closest_elevator_with_flr(next_visit_flr)
                self._assign_flr_to_elv(closer_elvid, next_visit_flr)
            # If there are no request below elv2, then go to the 1st flr
            # else:
            #     next_visit_flr = 1
            #     self._assign_flr_to_elv(1, next_visit_flr)

            # Case 2-2-2. Check whether there is request above elv1.
            next_visit_flr_above = self._return_request_above_flr(state_elv1)

            # If there exists request above elv1, then assign it to elv2.
            if next_visit_flr_above != 0:
                next_visit_flr = next_visit_flr_below
                self._assign_flr_to_elv(2, next_visit_flr)

            
        # Case 3. Both elevators are moving.
        elif state_elv1 != 1 and state_elv2 != 1:

            # Case 3-1. both elevators are on the same floor.
            if state_elv1 == state_elv2:
                next_visit_flr_below = self._return_request_below_flr(state_elv1)
                self._assign_flr_to_elv(1, next_visit_flr)

            # Case 3-2. two are on the different floor.
            elif state_elv1 > state_elv2:
                next_visit_flr_below = self._return_request_below_flr(state_elv1)
                if next_visit_flr_below > state_elv2:
                    self._assign_flr_to_elv(1, next_visit_flr)
                elif next_visit_flr_below < state_elv2:
                    self._assign_flr_to_elv(2, next_visit_flr)
            
            elif state_elv1 < state_elv2:
                next_visit_flr_below = self._return_request_below_flr(state_elv2)
                if next_visit_flr_below > state_elv1:
                    self._assign_flr_to_elv(2, next_visit_flr)
                elif next_visit_flr_below < state_elv1:
                    self._assign_flr_to_elv(1, next_visit_flr)

    def _assign_highest_first(self):
        '''
        If there exist request under elv1 or elv2, push it into the queue.
        While it goes to request, if there comes new request which has high priority,
        then push the original target into queue, and set the new target for next visit.
        '''
        # Where to visit next?
        highest_elv_id = self._get_closest_elevator_with_flr(9)[0]
        highest_elv_flr = self._get_closest_elevator_with_flr(9)[1]
        state_elv1 = self.state_elevators[0]
        state_elv2 = self.state_elevators[1]

        # Where both elevator are on the GF
        if highest_elv_id == 1: 
            next_visit_flr = self._get_highest_hall_call_flr()
            next_visit_elv = 1 # self._get_closest_elevator_with_flr(next_visit_flr)
            self._assign_flr_to_sys(next_visit_elv, next_visit_flr)
        
        # One of the elevator is on the GF
        elif highest_elv_id != 1 and state_elv1 == 1:
            next_visit_flr = self._get_highest_hall_call_flr()
            next_visit_elv = 1
            self._assign_flr_to_sys(next_visit_elv, next_visit_flr)
        
        # One of the elevator is on the GF
        elif highest_elv_id != 1 and state_elv2 == 1:
            next_visit_flr = self._get_highest_hall_call_flr()
            next_visit_elv = 2
            self._assign_flr_to_sys(next_visit_elv, next_visit_flr)

        # Both elevators are not on the GF
        else:    
            # While examining the hall calls lower than the highest elevator,
            # if there is hall call, then assign it to the closests elev
            for i in range(FLOORS - highest_elv_flr, FLOORS, -1):
                if self.flag_hall_calls[i] == 1:
                    # Assign it
                    elvid = self._get_closest_elevator_with_flr(i)
                    self._assign_flr_to_elv(elvid, i)
                    

    def _move(self):
        '''
        Get to the floor of queue.front.
        '''
        # If there is a request in elv1, 
        if len(self.queue_elv1) != 0:
            next_visit_flr = self.queue_elv1[0]
            self.queue_elv1.remove(next_visit_flr)
            self.flag_hall_calls[next_visit_flr-1] = 0
        
            # Check whether the candidate flr is on direction of elv1
            if self._check_flr_on_direction(1, next_visit_flr) == 1:
                # current_flr = self.state_elevators[0]
                # if current_flr > next_visit_flr:
                #     for i in range(current_flr, next_visit_flr, -1):
                #         self.state_elevators[0] = i-1 # Go for it
                # elif current_flr < next_visit_flr:
                #     for i in range(current_flr, next_visit_flr):
                #         self.state_elevators[0] = i-1 # Go for it
                self.state_elevators[0] = next_visit_flr # Go for it
            # If not, postpone it
            else:
                self.queue_elv1.append(next_visit_flr)

        # If there is a request in elv2,
        if len(self.queue_elv2) != 0:
            next_visit_flr = self.queue_elv2[0]
            self.queue_elv2.remove(next_visit_flr)
            self.flag_hall_calls[next_visit_flr-1] = 0
        
            # Check whether the candidate flr is on direction of elv1
            if self._check_flr_on_direction(2, next_visit_flr) == 1:
                # current_flr = self.state_elevators[1]
                # if current_flr > next_visit_flr:
                #     for i in range(current_flr, next_visit_flr, -1):
                #         self.state_elevators[1] = i-1 # Go for it
                # elif current_flr < next_visit_flr:
                #     for i in range(current_flr, next_visit_flr):
                #         self.state_elevators[1] = i-1 # Go for it
                self.state_elevators[1] = next_visit_flr # Go for it
            # If not, postpone it
            else:
                self.queue_elv2.append(next_visit_flr)

    def _check_flr_on_direction(self, elvid, flr):
        '''
        Check whether the input flr is on direction of given elevator.
        '''
        elvindex = elvid-1
        direction = self.state_directions[elvindex]
        
        # Going down
        if direction == -1:
            if self.state_elevators[elvindex] >= flr:
                return 1
            else:
                return 0

        # Staying on a floor
        else: 
            return 1

    
    def _onboard(self):
        '''
        If there are passengers, and elev.state is 0 (stop) at the floor,
        then take the passenger into the elevator.
        '''
        # If there are passangers on the floor, take them
        elv1_flr = self.state_elevators[0]

        if self.state_hall_calls[elv1_flr-1] != 0:
            self.cnt_passengers_elv1 += self.state_hall_calls[elv1_flr-1]
            self.state_hall_calls[elv1_flr-1] = 0
            self.flag_hall_calls[elv1_flr-1] = 0

        elv2_flr = self.state_elevators[1]
        if self.state_hall_calls[elv2_flr-1] != 0:
            self.cnt_passengers_elv2 += self.state_hall_calls[elv2_flr-1]
            self.state_hall_calls[elv2_flr-1] = 0
            self.flag_hall_calls[elv2_flr-1] = 0

    def _deliever(self):
        '''
        If there are passengers inside the elevator, (it should be going down)
        then deliever them to the first floor.
        It means, push 1st floor into the queue,
        in order to set the next visit floor as the GF.
        '''
        # If there are passengers inside the elevator, deliever them to GF.
        if self.cnt_passengers_elv1 != 0:
            self.state_directions[0] = -1
            self._assign_flr_to_sys(1, 1)
        
        if self.cnt_passengers_elv2 != 0:
            self.state_directions[1] = -1
            self._assign_flr_to_sys(2, 1)
    
    def _outboard(self):
        '''
        Take passengers off onto the GF.
        '''
        if self.cnt_passengers_elv1 != 0 and self.state_elevators[0] == 1:
            self.arrived_passengers += self.cnt_passengers_elv1
            self.cnt_passengers_elv1 = 0
            self.state_elevators[0] = 1
            self.state_directions[0] = 0
        
        if self.cnt_passengers_elv2 != 0 and self.state_elevators[1] == 1:
            self.arrived_passengers += self.cnt_passengers_elv2
            self.cnt_passengers_elv2 = 0
            self.state_elevators[1] = 1
            self.state_directions[1] = 0
    
    def _get_closest_elevator_with_flr(self, flr):
        '''
        Return the closest elevator with the input floor.
        '''
        residual_elv1 = abs(flr - self.state_elevators[0])
        residual_elv2 = abs(flr - self.state_elevators[1])

        # Elevator 1 is closer with the input flr
        if residual_elv1 > residual_elv2:
            return 1, self.state_elevators[0]

        # Elevator 2 is closer with the input flr
        elif residual_elv1 < residual_elv2:
            return 2, self.state_elevators[1]

        # Elevator 1 has priority
        else: 
            return 1, self.state_elevators[0]
            
    def _get_highest_elevator_flr_info(self, floor):
        '''
        Return the highest floor that elevator locates.
        '''
        max_flr = floor
        max_elvid = -1

        # Comapare all the located floor among elevators
        for i in range(len(self.state_elevators)):
            flr = self.state_elevators[i]
            if max_flr < flr:
                max_flr = flr
                max_elvid = i
        
        if max_flr == 9 or max_elvid == -1:
            return 0, 9

        # Return the highest 
        return max_elvid, max_flr

    def _return_request_above_flr(self, flr):
        '''
        Check whether there are request above the target floor.
        '''
        flag = 0
        for f in range(FLOORS-1, flr, -1):
            if self.state_hall_calls[f] == 1:
                flag = f
        return flag

    def _return_request_below_flr(self, flr):
        '''
        Check whether there are request below the target floor.
        '''
        flag = 0
        for f in range(flr-1, 1, -1):
            if self.state_hall_calls[f] == 1:
                flag = f
        return flag




    def _get_highest_hall_call_flr(self):
        '''
        Return the highest floor that has hall call.
        '''
        if 1 not in self.flag_hall_calls:
            return 0
        
        else:
            self.reversed_hall_calls = list(reversed(self.state_hall_calls))
            reversed_flr = 0
            highest_call_flr = 0
            while (reversed_flr != FLOORS):
                highest_call_flr = reversed_flr
                if (self.reversed_hall_calls[reversed_flr] != 0):
                    break
                reversed_flr += 1
            highest = FLOORS - highest_call_flr
            # print("highest: ", highest)
            return highest

    def _get_highest_agent_flr(self):
        '''
        Return the highest floor that agent locates.
        '''
        return max(self.state_elevators)
    
    def _update_ui(self):
        # Clear the background
        self.display.fill(WHITE)

        # Printing out the vertical lines
        pygame.draw.line(self.display, BLACK, (100,0), (100,800))
        pygame.draw.line(self.display, BLACK, (300,0), (300,800))

        # Printing out the horizontal lines
        for i in range(0, FLOORS):
            y_align = i*ELEVATOR_HEIGHT
            pygame.draw.line(self.display, BLACK, (0, y_align), (UI_WIDTH, y_align))
        
        # Printing out agent(elevator) information
        for agt, flr in enumerate(self.state_elevators):
            
            # Printing out the Elevator UI
            pt = self._convert_flr_to_elevator_pivot(agt, flr)
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, ELEVATOR_WIDTH, ELEVATOR_HEIGHT))
            
            # Printing out elevator information
            text_agent = font.render("ELEVATOR "+str(agt+1), True, WHITE)
            self.display.blit(text_agent, [pt.x+14, pt.y+40])

        # Printing out floor information
        for flr, psg in enumerate(self.state_hall_calls):

            # Convert floor to the 2D passenger pivot point
            pt = self._convert_flr_to_passenger_pivot(flr)

            # GF
            if flr == 0: 
                text = font.render(str(self.arrived_passengers) + " arrived", True, BLACK)
                self.display.blit(text, [pt.x+10, pt.y+10])

                text_flrg = font.render("GF", True, BLACK)
                self.display.blit(text_flrg,[pt.x-80, pt.y+10] )

            # 2F ~ 8F
            else:
                text = font.render(str(psg), True, BLACK)
                self.display.blit(text, [pt.x+40, pt.y+10])

                text_flr = font.render(str(flr+1) + "F", True, BLACK)
                self.display.blit(text_flr, [pt.x-80, pt.y+10])

            

        # pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # text = font.render("Score: " + str(self.score), True, BLACK)
        time = font.render("TIME: " + str(round(pygame.time.get_ticks() / 1000, 2)) + "s", True, BLACK )
        self.display.blit(time, [180, 760])

        text_wz = font.render("# of passengers waiting", True, BLACK )
        self.display.blit(text_wz, [160, 10])
        
        pygame.display.flip()
        pass

if __name__ == '__main__':
    
    game = EGCS()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
    pygame.quit()