#
# This is a general relativity time dilation simulator.
#
# You and your twin sibling are 20 years old.
# One of you stays on Earth and one of you flies in a space ship towards a black hole.
#
# There are two calendars on the screen and each represents their respective date (on Earth or on the ship).
# To switch between calendars, hit the TAB button.
#
# If you get too close to the black hole's event horizon, you will get stuck and the simulation will end.
#

##########################

import pygame
import random
import math
import time
from pygame.locals import *

import calendar

from datetime import date
from datetime import timedelta





#######################################################################
# initialize general variables
#######################################################################


# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

GREY = (215, 215, 215)
PINK = (255, 125, 125)
PURPLE = (200, 100, 255)
SKY_BLUE = (100, 200, 255)
LIGHT_BLUE = (200, 200, 255)
YELLOW = (255, 255, 100)

# these define variables for the calendar fonts and the mode fonts
calendar_font_size = 16
calendar_font = 'Courier'

mode_font_size = 24      # 1 point font equals to 1 1/3 pixels
mode_font = 'Courier'

MONTH = [None, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]  # MONTH[i] provides a string of the month name

# set up pygame
pygame.init()
all_sprites = pygame.sprite.Group()

# set up display window
background_color = BLACK
(WINDOW_WIDTH, WINDOW_HEIGHT) = (1300, 700)

# define surface
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Simulation')

#####
# simulation variables
#####

# MODES of play
MODES = ["EARTH", "THE SPACESHIP"]

# the simulation's location of everything with respect to lightyears
earth_location = 0  # this is the Earth's location and is technically not necessary (it's included for ease of understanding the code)
bh_location = 1000  # this is the number of lightyears from earth
eh_location = 2000
ship_location = -1  # This is the location of the ship. It is between Earth and the blackhole. It starts off at Earth so it starts off at -1 (this keeps it in Earth mode).

SPEED = 5       # this is the speed of everything on the screen
ship_speed = 1  # this is the speed the ship travels in the simulation


# initialize the current date
earth_date = date.today()
ship_date = date.today()





#######################################################################
# classes
#######################################################################


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, location, speed, facing):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load('ship_right.png')
        self.image.set_colorkey(background_color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y) # this is the location of the ship on the screen
        self.location = location            # this is the location of the ship with respect to the simulation
        self.speed = 1                      # this controls the speed of the ship WRT it's location in the simulation (not the screen position/speed)
        self.facing = facing

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Earth(pygame.sprite.Sprite):
    def __init__(self, x, y, location):
        pygame.sprite.Sprite.__init__(self)
        self.location = location    # this is the location of Earth with respect to the simulation
        self.x = x
        self.y = y
        self.image = pygame.image.load('earth.png')
        self.image.set_colorkey(background_color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def move(self, speed):
        self.x = self.x + speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Black_hole(pygame.sprite.Sprite):
    def __init__(self, x, y, location, event_horizon):
        pygame.sprite.Sprite.__init__(self)
        self.location = location            # this is the location of Earth with respect to the simulation
        self.event_horizon = event_horizon  # this is the location of the event horizon with respect to the simulation
        self.x = x
        self.y = y
        self.image = pygame.image.load('black hole.png')
        # self.image = pygame.image.load('pink.png')
        self.image.set_colorkey(background_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.speed = 1

    def move(self, speed):
        self.x = self.x + speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, speed):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed

    def move(self, speed):
        self.x = self.x + speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)





#######################################################################
# functions
#######################################################################


# This writes the calendars' text onto the screen.
# Instead of a string, it uses a list of strings as its input
# along with it's top-left (x, y) location.
def draw_text(text_list, x, y):
        my_font = pygame.font.SysFont(calendar_font, calendar_font_size)
        for i in range(0, len(text_list)):
            line = my_font.render(text_list[i], True, WHITE)
            SCREEN.blit(line, (x, int(y + i*calendar_font_size * (1.33))))

################################################################################################################################################################################

# this writes the current mode onto the screen
def draw_mode():
        my_font = pygame.font.SysFont(mode_font, mode_font_size)
        text_surface = my_font.render("YOU ARE ON " + mode, False, WHITE)
        SCREEN.blit(text_surface, (25, 25))

def r(object_A, object_B):          # this is r = distance of Object B from Object A (so A is on the left and B on the right => returns positive int)
    return object_B.x - object_A.x

################################################################################################################################################################################

# this writes the distance of the ship from the event horizon on the screen
def draw_distance(distance, unit, place):
        my_font = pygame.font.SysFont(mode_font, mode_font_size)
        text_surface = my_font.render("THE SHIP IS " + str(distance) + " " + unit + " FROM " + place, True, WHITE)
        y = int(mode_font_size * 2)
        SCREEN.blit(text_surface, (25, y))

################################################################################################################################################################################

# this create the calendar (as a list of strings where each string is a row of the calendar)
def create_calendar(input_date, name_of_calendar, age):

    current_calendar = calendar.month(input_date.year, input_date.month)  # a calendar of the current month (as single string)
    today = int(input_date.day)
    split = current_calendar.split("\n")
    done = False

    if today < 10:
        for i in range(2, len(split)):
            if done == True:
                break
            elif done == False:
                for j in range(0, len(split[i])):
                    if split[i][j] == str(today):
                        string = split[i]
                        split[i] = string[:j] + " " + string[j+1:]
                        done = True
                        break
    elif today >= 10:
        for i in range(2, len(split)):
            if done == True:
                break
            elif done == False:
                for j in range(0, len(split[i])):
                    if split[i][j : j+2] == str(today):
                        string = split[i]
                        split[i] = string[:j] + "  " + string[j+2:]
                        done = True
                        break
    else:
        None

    if split[-1] == "":                                                     # remove the last row if it's blank
        del split[-1]

    last_row1 = " Today is: " + MONTH[input_date.month] + " " + str(today)
    split.append(last_row1)                                                 # add today's date to the last row
    last_row2 = "      Age: " + str(age)
    split.append(last_row2)                                                 # add the current age of the person to the last row
    split.insert(0, name_of_calendar)                                       # insert the calendar name at the top of the calendar
    return split                                                            # returns a list of strings that makes the current month's calendar

################################################################################################################################################################################

def draw_calendars():

    # draw the calendar for Earth
    earth_calendar_height = round(1.33 * calendar_font_size * len(earth_calendar))      # this sets the height for the black box behind the calendar
    pygame.draw.rect(SCREEN, background_color, (30, 250, 210, earth_calendar_height))   # draw the background rectangle for the calendar (so it's always readable)
    draw_text(earth_calendar, 35, 250)                                                  # draw the calendar

    # draw the calendar for the ship
    ship_calendar_height = round(1.33 * calendar_font_size * len(ship_calendar))                        # this sets the height for the black box behind the calendar
    pygame.draw.rect(SCREEN, background_color, (WINDOW_WIDTH - 255, 250, 210, ship_calendar_height))    # draw the background rectangle for the calendar (so it's always readable)
    draw_text(ship_calendar, WINDOW_WIDTH - 250, 250)                                                   # draw the calendar

    # draw the border around the appropriate calendar (this highlights the current mode's calendar)
    width = 2
    # set the variables for the appropriate calendar
    if mode == "EARTH":
        calendar_x, calendar_y, calendar_width, calendar_height =  30 - width, 250 - width, 210 + width + 1, earth_calendar_height + width + 1
    elif mode == "THE SPACESHIP":
        calendar_x, calendar_y, calendar_width, calendar_height =  WINDOW_WIDTH - 255 - width, 250 - width, 210 + width+1, ship_calendar_height + width+1
    else:
        None
    pygame.draw.rect(SCREEN, YELLOW, (calendar_x, calendar_y, calendar_width, calendar_height), width)  # draw the border around the appropriate calendar

################################################################################################################################################################################

# This is the number of milliseconds in the program that represents one "real" day in the calendar.
# In the simulation, we could have experienced time going at time's normal rate, but then you'd have to wait an entire day on your calendar
# to see one day move on the simulation's calendar. As such, we are shortening the simulation's experienced day to be faster than an actual experienced day.
# Generally, I will set it up to be about one real second = "one day you experience" in the simulation.
MILLISECONDS_PER_DAY = 1000

# The following amounts to gamma in the time contraction formula.
# This is used when you are on Earth watching a ship go closer to a mass.
# Your clock will stay the same but their clock will seem to slow down (from your perspective).
# This essentially provides the amount of slow-down given the ship's distance from the massive object.
# The closer the ship is to the mass (ie shorter the distance), the higher the returned integer.
# R is the distance from the ship to the event horizon and D is the distance from the black hole's "mode" to the event horizon
def SLOWER_DAY(R, D):
    factor = (math.sqrt(1 - ((D - R)/D)**2)) ** 2
    contract = round(MILLISECONDS_PER_DAY / factor)
    return contract


# The following amounts to gamma in the time dilation formula.
# This is used when you are on a ship (going towards a mass) watching Earth.
# Your clock will stay the same but Earth's clock will seem to speed up (from your perspective).
# This essentially provides the amount of speed-up given the ship's distance from the massive object.
# The closer the ship is to the mass (ie shorter the distance), the lower the returned integer.
# R is the distance from the ship to the event horizon and D is the distance from the black hole's "mode" to the event horizon
def FASTER_DAY(R, D):
    factor = (math.sqrt(1 - ((D - R)/D)**2)) ** 2
    dilate = round(MILLISECONDS_PER_DAY * factor)
    return dilate


################################################################################################################################################################################


##########################################################
# create and initialize simulation objects and variables #
##########################################################


x = WINDOW_WIDTH//2     # set the x-value for Earth's location on screen
y = WINDOW_HEIGHT//2    # set the y-value for Earth's location on screen
earth = Earth(x, y, 0)  # creating the Earth object (as a sprite)
all_sprites.add(earth)  # add the sprite to the Sprite Group

x = WINDOW_WIDTH                                        # set the x-value for the black hole's location on screen
y = 10                                                  # set the y-value for the black hole's location on screen
black_hole = Black_hole(x, y, bh_location, eh_location) # creating the black hole object (as a sprite)
all_sprites.add(black_hole)                             # add the sprite to the Sprite Group

ship = Ship(WINDOW_WIDTH//2, 350, ship_location, 1, "RIGHT") # creating the spaceship object (as a sprite)
all_sprites.add(ship)                   # adding the sprite to the Sprite Group


# The following will make the stars in the background.
# The use of the mod is so you can control the % of stars that are tiny and white.
# While most starts will be white, a few will be grey, yellow, or light blue (and of varying sizes).
# Just make all the specialty stars a small number compared to the mod.
# The more white stars you want, just make the mod a higher number.

stars_per_layer = 200
mod = 10

background_stars_0 = []
for i in range(0, stars_per_layer // 4):
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0 , WINDOW_HEIGHT)
    star = Star(x, y, 1, WHITE, 0)
    background_stars_0.append(star)


background_stars_1 = []
for i in range(0, stars_per_layer // 3):
    x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH + (1000 * ship_speed))
    y = random.randint(0 , WINDOW_HEIGHT)
    if i % mod == 0:
        color = LIGHT_BLUE
        radius = 3
    elif i % mod == 1:
        color = GREY
        radius = 2
    elif i % mod <= 3:
        color = YELLOW
        radius = 1
    else:
        color = WHITE
        radius = 1
    star = Star(x, y, radius, color, ship_speed)
    background_stars_1.append(star)

background_stars_2 = []
for i in range(0, stars_per_layer // 2):
    x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH + (1000 * SPEED))
    y = random.randint(0 , WINDOW_HEIGHT)
    if i % mod == 0:
        color = LIGHT_BLUE
        radius = 3
    elif i % mod == 1:
        color = GREY
        radius = 2
    elif i % mod <= 3:
        color = YELLOW
        radius = 1
    else:
        color = WHITE
        radius = 1
    star = Star(x, y, radius, color, SPEED)
    background_stars_2.append(star)

background_stars_3 = []
for i in range(0, stars_per_layer):
    x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH + (1000 * SPEED * 2))
    y = random.randint(0 , WINDOW_HEIGHT)
    if i % mod == 0:
        color = LIGHT_BLUE
        radius = 3
    elif i % mod == 1:
        color = GREY
        radius = 2
    elif i % mod <= 3:
        color = YELLOW
        radius = 1
    else:
        color = WHITE
        radius = 1
    star = Star(x, y, radius, color, SPEED * 2)
    background_stars_3.append(star)


################
# main program #
################


# this initiates the mode of play (between "staying on Earth" or "going on the ship")
k = 0
mode = MODES[k]

# initiate the ages of the two perspectives
earth_age = 20
earth_day_counter = 0

ship_age = 20
ship_day_counter = 0

# initialize the calendars
earth_calendar = create_calendar(earth_date, "  Earth's calendar", earth_age)
ship_calendar = create_calendar(ship_date, "Spaceship's calendar", ship_age)

# this begins the clock that is used reference the calendar speeds
mainClock = pygame.time.Clock()

earth_timer = 0     # initialize Earth's timer (milliseconds)
ship_timer = 0      # initialize the spaceship's timer (milliseconds)

earth_t0 = pygame.time.get_ticks()  # get the current time for Earth
ship_t0 = pygame.time.get_ticks()   # get the current time for the ship

travel_modes = ["near Earth", "interstellar", "near black hole"]
current_travel_mode = travel_modes[0]

speed = 0   # this initializes the speed of everything on the screen

R = black_hole.location - ship.location

TAB_down = False


#################
# the main loop #
#################

running = True

while running:

    mainClock.tick(60)  # set the program's clock to 60 Frames Per Second

    # Check to see if the user terminated the program.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        else:
            None

###############################
# update timers and calendars #
###############################

    # update timers
    t1 = pygame.time.get_ticks()   # get the current time
    earth_timer = t1 - earth_t0
    ship_timer = t1 - ship_t0

    # calculate the current date for each location (on Earth or on the spaceship) and for each situation (time proper vs dilated/contracted time)
    if mode == "EARTH":

        # update Earth's calendar as necessary
        if earth_timer >= MILLISECONDS_PER_DAY:                                             # if Earth's timer has exceeded enough for the calendar to move to the next day...
            earth_date = earth_date + timedelta(days=1)                                     # set Earth's date for the next day
            earth_calendar = create_calendar(earth_date, "  Earth's calendar", earth_age)   # create Earth's new calendae
            earth_timer = 0                                                                 # start over Earth's timer
            earth_day_counter = earth_day_counter + 1
            earth_t0 = pygame.time.get_ticks()
        else:
            None

        # update the spaceship's calendar as necessary
        # decide which length of a day to use (based on distance from even horizon -- this is the mode of travel)
        if current_travel_mode == "near black hole":
            radius = black_hole.event_horizon - ship.location
            DISTANCE = black_hole.event_horizon - black_hole.location
            ship_length_of_day = SLOWER_DAY(radius, DISTANCE)
        else:
            ship_length_of_day = MILLISECONDS_PER_DAY

        if ship_timer >= ship_length_of_day:                                                # if the spaceship's timer has exceeded enough for the calendar to move to the next day...
            ship_date = ship_date + timedelta(days=1)                                       # set the spaceship's date for the next day
            ship_calendar = create_calendar(ship_date, "Spaceship's calendar", ship_age)    # create the spaceship's new calendae
            ship_timer = 0                                                                  # start over the spaceship's timer
            ship_day_counter = ship_day_counter + 1
            ship_t0 = pygame.time.get_ticks()
        else:
            None


    elif mode == "THE SPACESHIP":

        # update Earth's calendar as necessary
        # decide which length of a day to use (based on distance from even horizon)
        if current_travel_mode == "near black hole":
            radius = black_hole.event_horizon - ship.location
            DISTANCE = black_hole.event_horizon - black_hole.location
            earth_length_of_day = FASTER_DAY(radius, DISTANCE)
        else:
            earth_length_of_day = MILLISECONDS_PER_DAY

        if earth_timer >= earth_length_of_day:                                      # if Earth's timer has exceeded enough for the calendar to move to the next day...
            radius = black_hole.event_horizon - ship.location
            if radius > 500:
                jump_days = 1
            elif radius > 250:
                jump_days = 2
            elif radius > 125:
                jump_days = 4
            elif radius > 62:
                jump_days = 8
            elif radius > 62:
                jump_days = 8
            elif radius > 30:
                jump_days = 16
            elif radius > 15:
                jump_days = 32
            elif radius > 8:
                jump_days = 64
            elif radius > 4:
                jump_days = 128
            elif radius > 2:
                jump_days = 256
            elif radius > 1:
                jump_days = 512
            earth_date = earth_date + timedelta(days=jump_days)                         # set Earth's date for the next day
            earth_calendar = create_calendar(earth_date, "  Earth's calendar", earth_age)  # create Earth's new calendae
            earth_day_counter = earth_day_counter + jump_days
            earth_timer = 0                                                         # start over Earth's timer
            earth_t0 = pygame.time.get_ticks()
        else:
            None

        # update the spaceship's calendar as necessary
        if ship_timer >= MILLISECONDS_PER_DAY:                                      # if the spaceship's timer has exceeded enough for the calendar to move to the next day...
            ship_date = ship_date + timedelta(days=1)                               # set the spaceship's date for the next day
            ship_calendar = create_calendar(ship_date, "Spaceship's calendar", ship_age)  # create the spaceship's new calendae
            ship_day_counter = ship_day_counter + 1
            ship_timer = 0                                                          # start over the spaceship's timer
            ship_t0 = pygame.time.get_ticks()
        else:
            None
    else:
        None

    while earth_day_counter > 365:
        earth_age = earth_age + 1
        earth_day_counter = earth_day_counter - 365

    if ship_day_counter > 365:
        ship_age = ship_age + 1
        ship_day_counter = 0
    else:
        None

########################
# player pressing keys #
########################

    # if a player RELEASES a key
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_TAB:
            TAB_down = False
    else:
        None


    # if a player PRESSES a key
    if event.type == pygame.KEYDOWN:
        # user hits the TAB key (to change perspective modes)
        if event.key == pygame.K_TAB:
            if TAB_down == False:
                k = (k + 1) % len(MODES)
                mode = MODES[k]
                TAB_down = True
            else:
                None

        # user hits the RIGHT arrow key
        if event.key == pygame.K_RIGHT:
            ship.facing = "RIGHT"
            ship.image = pygame.image.load('ship_right.png')
            ship.image.set_colorkey(background_color)

            if current_travel_mode == "near Earth":
                earth.move(-SPEED)
                if earth.rect.right <= 0:
                    ship.location = 0
            elif current_travel_mode == "interstellar":
                for i in range(0, len(background_stars_1)):   # move the stars
                    background_stars_1[i].x = background_stars_1[i].x - background_stars_1[i].speed
                for i in range(0, len(background_stars_2)):   # move the stars
                    background_stars_2[i].x = background_stars_2[i].x - background_stars_2[i].speed
                for i in range(0, len(background_stars_3)):   # move the stars
                    background_stars_3[i].x = background_stars_3[i].x - background_stars_3[i].speed
                ship.location = ship.location + ship.speed
            elif current_travel_mode == "near black hole":
                for i in range(0, len(background_stars_1)):   # move the stars
                    background_stars_1[i].x = background_stars_1[i].x - background_stars_1[i].speed
                for i in range(0, len(background_stars_2)):   # move the stars
                    background_stars_2[i].x = background_stars_2[i].x - (background_stars_2[i].speed // 2)
                for i in range(0, len(background_stars_3)):   # move the stars
                    background_stars_3[i].x = background_stars_3[i].x - (background_stars_3[i].speed // 5)
                ship.location = ship.location + ship.speed
                r = black_hole.event_horizon - ship.location
                if r % 3 == 0:
                    black_hole.speed = 2
                else:
                    black_hole.speed = 1
                black_hole.move(-black_hole.speed)
            else:
                None
            
        # user hits the LEFT arrow key
        if event.key == pygame.K_LEFT:
            ship.facing = "LEFT"
            ship.image = pygame.image.load('ship_left.png')
            ship.image.set_colorkey(background_color)

            if current_travel_mode == "near Earth":
                if earth.rect.right >= WINDOW_WIDTH:
                    None
                else:
                    earth.move(SPEED)
                    
            elif current_travel_mode == "interstellar":
                for i in range(0, len(background_stars_1)):   # move the stars
                    background_stars_1[i].x = background_stars_1[i].x + background_stars_1[i].speed
                for i in range(0, len(background_stars_2)):   # move the stars
                    background_stars_2[i].x = background_stars_2[i].x + background_stars_2[i].speed
                for i in range(0, len(background_stars_3)):   # move the stars
                    background_stars_3[i].x = background_stars_3[i].x + background_stars_3[i].speed
                
                if ship.location < 0:
                    None
                else:
                    ship.location = ship.location - ship.speed
                
            elif current_travel_mode == "near black hole":
                for i in range(0, len(background_stars_1)):   # move the stars
                    background_stars_1[i].x = background_stars_1[i].x + background_stars_1[i].speed
                for i in range(0, len(background_stars_2)):   # move the stars
                    background_stars_2[i].x = background_stars_2[i].x + (background_stars_2[i].speed // 2)
                for i in range(0, len(background_stars_3)):   # move the stars
                    background_stars_3[i].x = background_stars_3[i].x + (background_stars_3[i].speed // 5)
                ship.location = ship.location - ship.speed
                black_hole.move(black_hole.speed)
            else:
                None

    else:
        None


#########################################
# draw everything and update the screen #
#########################################

    SCREEN.fill(background_color)               # erase screen

    # determine the current travel mode
    if ship.location < 0:
        current_travel_mode = "near Earth"
    elif ship.location < black_hole.location:
        current_travel_mode = "interstellar"
    else:
        current_travel_mode = "near black hole"

    for i in range(0, len(background_stars_0)):   # draw the stationary stars
        background_stars_0[i].draw(SCREEN)

    if current_travel_mode == "near Earth":
        earth.draw(SCREEN)
        ship.draw(SCREEN)
        if ship.facing == "RIGHT":
            draw_distance(1000, "LIGHTYEARS", "THE EVENT HORIZON")
        elif ship.facing == "LEFT":
            draw_distance(0, "LIGHTYEARS", "EARTH")
        else:
            None
    elif current_travel_mode == "interstellar":

        for i in range(0, len(background_stars_1)):   # draw the moving stars
            background_stars_1[i].draw(SCREEN)
        for i in range(0, len(background_stars_2)):   # draw the moving stars
            background_stars_2[i].draw(SCREEN)
        for i in range(0, len(background_stars_3)):   # draw the moving stars
            background_stars_3[i].draw(SCREEN)

        ship.draw(SCREEN)   # draw the ship

        R = black_hole.location - ship.location
        if ship.facing == "RIGHT":
            draw_distance(R, "LIGHTYEARS", "THE EVENT HORIZON") # draw the distance to the event horizon
        elif ship.facing == "LEFT":
            draw_distance(ship.location, "LIGHTYEARS", "EARTH") # draw the distance to Earth
        else:
            None

    elif current_travel_mode == "near black hole":
        for i in range(0, len(background_stars_1)):   # draw the moving stars
            background_stars_1[i].draw(SCREEN)
        for i in range(0, len(background_stars_2)):   # draw the moving stars
            background_stars_2[i].draw(SCREEN)
        for i in range(0, len(background_stars_3)):   # draw the moving stars
            background_stars_3[i].draw(SCREEN)
        black_hole.draw(SCREEN)
        ship.draw(SCREEN)

        r = black_hole.event_horizon - ship.location
        if r <= 0:
            running = False
        else:
            if ship.facing == "RIGHT":
                draw_distance(r, "KM", "THE EVENT HORIZON") # draw the distance to the event horizon
            elif ship.facing == "LEFT":
                draw_distance(1000, "LIGHTYEARS", "EARTH")  # draw the distance to Earth
            else:
                None

    draw_calendars()                            # draw the calendars on the screen
    draw_mode()                                 # draw the mode onto the top of the screen

    pygame.display.flip()   # display the new screen

pygame.quit()

print("You got stuck in the event horizon. Time no longer exists.")
