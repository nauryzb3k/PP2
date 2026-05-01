import pygame
import sys
import datetime
from collections import deque

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS Paint Final")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

tool = "pencil"
color = (0, 0, 0)

thickness = 3

drawing = False
start_pos = None
prev_pos = None
curr_pos = None

font = pygame.font.SysFont("Arial", 20)

text_mode = False
text_pos = None
text_buffer = ""


def get_rect(p1, p2):
    return pygame.Rect(
        min(p1[0], p2[0]),
        min(p1[1], p2[1]),
        abs(p1[0] - p2[0]),
        abs(p1[1] - p2[1])
    )


def flood_fill(surface, x, y, new_color):
    width, height = surface.get_size()
    target_color = surface.get_at((x, y))

    if target_color == new_color:
        return

    q = deque()
    q.append((x, y))

    while q:
        cx, cy = q.popleft()

        if 0 <= cx < width and 0 <= cy < height:
            if surface.get_at((cx, cy)) == target_color:
                surface.set_at((cx, cy), new_color)

                q.append((cx + 1, cy))
                q.append((cx - 1, cy))
                q.append((cx, cy + 1))
                q.append((cx, cy - 1))


running = True
print("Controls:")
print("1 - Pencil")
print("2 - Line")
print("3 - Rectangle")
print("C - Clear canvas")
print("Ctrl + S - Save image")
print("+/- - Brush size")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if text_mode:
                if event.key == pygame.K_RETURN:
                    canvas.blit(font.render(text_buffer, True, color), text_pos)
                    text_mode = False
                    text_buffer = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_buffer = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    text_buffer += event.unicode

            else:
                if event.key == pygame.K_1:
                    tool = "pencil"

                if event.key == pygame.K_2:
                    tool = "line"

                if event.key == pygame.K_3:
                    tool = "rect"

                if event.key == pygame.K_4:
                    tool = "fill"

                if event.key == pygame.K_5:
                    tool = "text"

                if event.key == pygame.K_c:
                    canvas.fill((255, 255, 255))

                if event.key == pygame.K_MINUS:
                    thickness = max(1, thickness - 1)

                if event.key == pygame.K_EQUALS:
                    thickness += 1

                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved as {filename}")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if tool == "text":
                text_mode = True
                text_pos = event.pos
                text_buffer = ""

            elif tool == "fill":
                flood_fill(canvas, event.pos[0], event.pos[1], color)

            else:
                drawing = True
                start_pos = event.pos
                prev_pos = event.pos
                curr_pos = event.pos

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                curr_pos = event.pos

                if tool == "pencil":
                    pygame.draw.line(canvas, color, prev_pos, curr_pos, thickness)
                    prev_pos = curr_pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drawing = False

            if tool == "line":
                pygame.draw.line(canvas, color, start_pos, event.pos, thickness)

            if tool == "rect":
                pygame.draw.rect(canvas, color, get_rect(start_pos, event.pos), thickness)

            start_pos = None
            prev_pos = None
            curr_pos = None

    screen.blit(canvas, (0, 0))

    if drawing and start_pos and curr_pos:

        if tool == "line":
            pygame.draw.line(screen, color, start_pos, curr_pos, thickness)

        if tool == "rect":
            pygame.draw.rect(screen, color, get_rect(start_pos, curr_pos), thickness)

    if text_mode:
        preview = font.render(text_buffer, True, color)
        screen.blit(preview, text_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()