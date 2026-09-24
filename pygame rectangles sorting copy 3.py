import pygame
import sys
import time
import random
import math

last_time = 0 
running = True 

def is_convertible_to_int(val):
    try:
        int(val)
        return True
    except (ValueError, TypeError):
        return False

def is_convertible_to_float(val):
    try:
        float(val)
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

def step_delay(list_s):
    global step_sleep_time, last_time
    
    # Pure static delay calculated prior to execution
    if step_sleep_time > 0:
        time.sleep(step_sleep_time)

    # Render throttle at 60 FPS to prevent GUI lockup
    if time.time() - last_time > 1 / 60:
        last_time = time.time()
        update_screen(list_s)

def swap(list_s, ind1, ind2):
    list_s[ind1], list_s[ind2] = list_s[ind2], list_s[ind1]
    return list_s

def partition(list_s, start, end):
    rand_pivot_idx = random.randint(start, end)
    list_s[rand_pivot_idx], list_s[end] = list_s[end], list_s[rand_pivot_idx]

    pivot = list_s[end]
    i = start - 1
    for j in range(start, end):
        if not running:
            return i + 1
        
        # Incur the static predicted delay on every partition step
        step_delay(list_s)
        
        if list_s[j] < pivot:
            i += 1
            list_s = swap(list_s, j, i)   
    i += 1
    list_s = swap(list_s, end, i)
    return i

def quicksort(list_s, start, end):
    if not running or start >= end:
        return

    pivot_idx = partition(list_s, start, end)
    quicksort(list_s, start, pivot_idx - 1)
    quicksort(list_s, pivot_idx + 1, end)

def update_screen(list_s):
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOUR)

    n = len(list_s)
    height_mult = SCREEN_HEIGHT / n
    width_mult = SCREEN_WIDTH / n

    for index, val in enumerate(list_s):
        x1 = math.floor(index * width_mult)
        h = math.floor(val * height_mult)
        pygame.draw.rect(screen, (255, 255, 255), (x1, SCREEN_HEIGHT - h, math.ceil(width_mult), h))

    pygame.display.flip()


# --- CALIBRATION ---
# Instead of guessing a fixed microsecond cost per step, measure the ACTUAL
# per-iteration cost and the ACTUAL per-render cost, on this machine, for this
# AMOUNT, right before the real run. Render cost scales with AMOUNT (more
# rectangles to draw) and per-iteration cost is basically constant, so a single
# hardcoded constant can never fit both a small N and a large N run well.

def _calib_partition(a, start, end, counter):
    rand_pivot_idx = random.randint(start, end)
    a[rand_pivot_idx], a[end] = a[end], a[rand_pivot_idx]
    pivot = a[end]
    i = start - 1
    for j in range(start, end):
        counter[0] += 1
        if a[j] < pivot:
            i += 1
            a[j], a[i] = a[i], a[j]
    i += 1
    a[end], a[i] = a[i], a[end]
    return i

def _calib_quicksort(a, start, end, counter):
    if start >= end:
        return
    p = _calib_partition(a, start, end, counter)
    _calib_quicksort(a, start, p - 1, counter)
    _calib_quicksort(a, p + 1, end, counter)

def calibrate_overheads(amount):
    """Returns (base_overhead_per_step, cost_per_render), both in seconds,
    measured live for this AMOUNT on this machine."""

    # --- Cost of one update_screen() call for this AMOUNT ---
    sample_list = list(range(amount))
    random.shuffle(sample_list)
    update_screen(sample_list)  # warm-up call (first draw can be slower)
    RENDER_SAMPLES = 8
    t0 = time.perf_counter()
    for _ in range(RENDER_SAMPLES):
        update_screen(sample_list)
    cost_per_render = (time.perf_counter() - t0) / RENDER_SAMPLES

    # --- Cost of one raw partition step (comparison/swap/function call),
    #     with NO sleep and NO rendering involved ---
    calib_list = list(range(amount))
    random.shuffle(calib_list)
    counter = [0]
    t0 = time.perf_counter()
    _calib_quicksort(calib_list, 0, amount - 1, counter)
    elapsed = time.perf_counter() - t0
    base_overhead_per_step = elapsed / max(1, counter[0])

    return base_overhead_per_step, cost_per_render


def main():
    pygame.init()
    global SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOUR, screen, clock, running
    global step_sleep_time

    monitor_info = pygame.display.Info()
    SCREEN_WIDTH = monitor_info.current_w
    SCREEN_HEIGHT = monitor_info.current_h

    user_amount = input("input pixel val or SW (SCREEN WIDTH): ")
    if is_convertible_to_int(user_amount):
        AMOUNT = int(user_amount)
    else:
        AMOUNT = int(SCREEN_HEIGHT)

    user_time = input("input target duration in seconds (e.g. 5 or 0 for max speed): ")
    if is_convertible_to_float(user_time):
        target_duration = float(user_time)
    else:
        target_duration = 5.0

    # Need a screen/window to exist before we can time update_screen() calls
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    BG_COLOUR = (0, 0, 0)
    running = True

    # Theoretical average loop iterations for randomized Quicksort: ~1.39 * N * log2(N)
    predicted_iterations = 1.39 * AMOUNT * math.log2(max(2, AMOUNT))

    if target_duration > 0 and predicted_iterations > 0:
        base_overhead, render_cost = calibrate_overheads(AMOUNT)

        # How many renders will actually happen?
        # - If steps would naturally run faster than 60fps, renders are
        #   throttled by the time gate -> roughly target_duration * 60 renders.
        # - If each step (sleep+overhead) already exceeds 1/60s, the time-gate
        #   condition is true on effectively every step -> ~predicted_iterations renders.
        max_renders_at_60fps = target_duration * 60
        if predicted_iterations > max_renders_at_60fps:
            num_renders = max_renders_at_60fps
        else:
            num_renders = predicted_iterations

        render_time_budget = num_renders * render_cost
        remaining_budget = target_duration - render_time_budget

        raw_sleep = remaining_budget / predicted_iterations - base_overhead
        step_sleep_time = max(0, raw_sleep)
    else:
        step_sleep_time = 0

    while running:
        init(AMOUNT)
        start_time = time.time()
        
        quicksort(init_list, 0, AMOUNT - 1)
        
        # Prints exact actual run time to evaluate formula accuracy
        actual_time = time.time() - start_time
        print(f"Target: {target_duration:.2f}s | Actual: {actual_time:.2f}s")
        running = False

    pygame.quit()
    sys.exit()

main()