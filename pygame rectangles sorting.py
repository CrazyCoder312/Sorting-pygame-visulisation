import pygame
import sys
import time
import random

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
    rectangles = []
    screen.fill(BG_COLOUR)
    j = 0
    for i in list_s:
        j+=1
        rectangles.append((j,SCREEN_HEIGHT-i,1,i))

    for i in rectangles:
        pygame.draw.rect(screen, (255,255,255), i)

    clock.tick(60)
        
        
    



def main():
    pygame.init()

    SCREEN_WIDTH= 1920
    SCREEN_HEIGHT= 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


    clock = pygame.time.Clock()

    BG_COLOUR = (0,0,0)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Game Logic Updates ---
        # (Move players, check collisions, etc. would go here)


        

        # --- Drawing / Rendering ---
        screen.fill(BG_COLOUR)  # Clear the screen with a solid background
        
        # (Draw your sprites, shapes, and text here)

        height = 100
        rect = (0,SCREEN_HEIGHT-height,100,height)

        pygame.draw.rect(screen, (255,255,255), rect)





        # --- Update the Display ---
        pygame.display.flip()  # Swap buffers to reveal the new frame
        
        # --- Maintain Frame Rate ---
          # Cap the game loop at 60 Frames Per Second

    # 5. Clean up and Exit safely
    pygame.quit()
    sys.exit()
                


main()
