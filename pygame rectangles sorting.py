import pygame
import sys
import time
import random
import math


x_speed = 5

# Global variable tracking application state
running = True 
def is_convertible_to_int(val):
    try:
        int(val)
        return True
    except (ValueError, TypeError):
        return False

sys.setrecursionlimit(10000000)

def init(len_i):
    global init_list
    init_list = []
    
    for i in range(len_i):
        init_list.append(i)
    random.shuffle(init_list)
    
def swap(list_s, ind1,ind2):
    list_s[ind1] , list_s[ind2] = list_s[ind2] , list_s[ind1]
    update_screen(list_s)
    return(list_s)

def quicksort(list_s,start,end):
    if not running:
        return []
    
    pivot = list_s[end]
    if start > end:
        return[]
    elif start == end:
        return[list_s[start]]

    i = start-1
    for j in range(start,end):
        if list_s[j] < pivot:
            i += 1
            list_s = swap(list_s,j,i)   
    i += 1
    list_s = swap(list_s,end,i)
    return quicksort(list_s, start, i - 1) + [list_s[i]] + quicksort(list_s, i + 1, end)

def update_screen(list_s):
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    rectangles = []
    screen.fill(BG_COLOUR)

    height_mult = SCREEN_HEIGHT/len(list_s) 
    print(height_mult)
    print(SCREEN_HEIGHT)
    print(len(list_s) )
    for index, i in enumerate(list_s):
        x1 = math.floor(index * SCREEN_WIDTH / len(list_s))
        x2 = math.floor((index + 1) * SCREEN_WIDTH / len(list_s))

        width = x2 - x1

        rectangles.append(
            (x1, SCREEN_HEIGHT - math.floor(i*height_mult), width, math.floor(i*height_mult))
        )

    for i in rectangles:
        pygame.draw.rect(screen, (255,255,255), i)

    pygame.display.flip()
    clock.tick(75 * x_speed)
        
        
    



def main():
    pygame.init()
    global SCREEN_WIDTH,SCREEN_HEIGHT,BG_COLOUR

    monitor_info = pygame.display.Info()
    monitor_width = monitor_info.current_w
    monitor_height = monitor_info.current_h

    SCREEN_WIDTH= monitor_width
    SCREEN_HEIGHT= monitor_height
    global screen

    user = input("input pixel val or SW (SCREEN WIDTH)")
    
    if is_convertible_to_int(user):
        AMOUNT = int(user)
    
    else:
        AMOUNT = int(SCREEN_HEIGHT)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    global clock
    clock = pygame.time.Clock()

    BG_COLOUR = (0,0,0)

    running = True

    

    while running:
        



        init(AMOUNT)
        quicksort(init_list,0,AMOUNT-1)
        

    




        running = False


    # 5. Clean up and Exit safely
    pygame.quit()
    sys.exit()
                


main()
