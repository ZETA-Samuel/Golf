import pygame, asyncio
from functools import lru_cache

pygame.init()
clock = pygame.time.Clock()

# full screen
full_width,full_height = 1325,960

width = 960
height = 540
play_x = (full_width - width) // 2
play_y = (full_height - height) // 2
# game variables

#ball_x,ball_y = 50,50
#speed = 5

# Settings
radius = 13
power = 8.0
max_drag = 150
friction = 0.98
bounce = 0.8
stop_speed = 5.0
hole_capture_speed = 350
overshoot_slowdown_radius = 60
overshoot_slowdown_duration = 0.35
overshoot_friction = 0.94


# screen
screen = pygame.display.set_mode((full_width,full_height))
game_area = pygame.Rect(play_x,play_y,width,height)
game_surface = pygame.Surface((width,height))
pygame.display.set_caption("Golf Club")

# load image
ball_img = pygame.image.load('images/golf_ball.png').convert_alpha()
hole_img = pygame.image.load('images/hole.png').convert_alpha()
flag_img = pygame.image.load('images/flag.png').convert_alpha()
game_over = pygame.image.load('images/game_over.png').convert_alpha()
hole_in_one = pygame.image.load('images/hole-in-one.png').convert_alpha()
par = pygame.image.load('images/par.png').convert_alpha()
birdie = pygame.image.load('images/birdie.png').convert_alpha()
eagle = pygame.image.load('images/eagle.png').convert_alpha()
bogey = pygame.image.load('images/bogey.png').convert_alpha()
double_bogey = pygame.image.load('images/double_bogey.png').convert_alpha()
triple_bogey = pygame.image.load('images/triple_bogey.png').convert_alpha()
quadruple_bogey = pygame.image.load('images/quadruple_bogey.png').convert_alpha()

# image conversion
ball_img = pygame.transform.scale(ball_img, (radius * 2,radius * 2))
hole_img = pygame.transform.scale(hole_img, (40,40))
flag_img = pygame.transform.scale(flag_img, (70,82))
game_over = pygame.transform.scale(game_over, (width,height))
hole_in_one = pygame.transform.scale(hole_in_one, (250,100))
par = pygame.transform.scale(par,(250,100))
birdie = pygame.transform.scale(birdie,(250,100))
eagle = pygame.transform.scale(eagle,(250,100))
bogey = pygame.transform.scale(bogey,(250,100))
double_bogey = pygame.transform.scale(double_bogey,(320,100))
triple_bogey = pygame.transform.scale(triple_bogey,(320,100))
quadruple_bogey = pygame.transform.scale(quadruple_bogey,(350,100))

# Text Font
text_font = pygame.font.SysFont("Arial",30)


@lru_cache(maxsize=128)
def render_text(font, text, text_col):
    return font.render(text, True, text_col)


def draw_text(surface,text,font,text_col,x,y):
    img = render_text(font, text, text_col)
    img_rect = img.get_rect(center=(x,y))
    surface.blit(img,img_rect)

# obstacle
levels = [
    # {
    #     "start": (1000,1000),
    #     "hole": (1000,1000),
    #     "walls": [],
    #     "moving_walls": [],
    #     "wall_speed": None,
    #     "wall_direction": None,
    # },
    {
        "start": (80, height/2),
        "hole": (width-80,height/2),
        "walls": [

        ],
        "moving_walls": [],
        "wall_speed": 0,
        "wall_direction": 0,
    },
    {
        "start": (80,height/2),
        "hole": (width-80,height/2),
        "walls": [
            pygame.Rect(width/2,0,12,height*0.7)
        ],
        "moving_walls": [],
        "wall_speed": 0,
        "wall_direction": 0,
    },
    {
        "start": (80,height/2),
        "hole": (width-80,height/2),
        "walls": [
            pygame.Rect(width/2,0,12,height*0.2),
            pygame.Rect(width/2,height*0.32,12,height*0.72),
        ],
        "moving_walls": [],
        "wall_speed": 0,
        "wall_direction": 0,
    },
    {
        "start": (80,height/2),
        "hole": (width-80,height/2),
        "walls": [
            pygame.Rect(width/3,height*0.45,12,height*0.15),
            pygame.Rect(2*width/3,height*0.45,12,height*0.15),
        ],
        "moving_walls": [],
        "wall_speed": 0,
        "wall_direction": 0,
    },

    {
        "start": (80, height/2),
        "hole": (width-80,height/2),
        "walls": [
            pygame.Rect(width/4,0,12,height*0.2),
            pygame.Rect(width/4,height*0.3,12,height*0.7),
            pygame.Rect(width/2,0,12,height*0.6),
            pygame.Rect(width/2,height*0.7,12,height*0.3),
            pygame.Rect(3*width/4,0,12,height*0.45),
            pygame.Rect(3*width/4,height*0.55,12,height*0.45),

        ],
        "moving_walls": [],
        "wall_speed": 0,
        "wall_direction": 0,
    },
    {
        "start": (80, height/2),
        "hole": (width-80,height/2),
        "walls":[
            pygame.Rect(width/2,0,12,height*0.4),
            pygame.Rect(width/2,height*0.6,12,height*0.4),
        ],
        "moving_walls": [
            pygame.Rect(width/2,height*0.4,12,height*0.1),
        ],
        "wall_speed": 2,
        "wall_direction": 1,
    },
]

# level loading
def load_level(level_number):
    level = levels[level_number]

    pos = pygame.Vector2(level["start"])
    vel = pygame.Vector2(0,0)
    hole_x,hole_y = level["hole"]
    walls = level["walls"]
    moving_walls = level["moving_walls"]
    wall_speed = level["wall_speed"]
    wall_direction = level["wall_direction"]
    attempt = 0

    return pos,vel,hole_x,hole_y,walls,moving_walls,wall_speed,wall_direction,attempt

async def main():
    game_state = "home"

    hole_x,hole_y = 700, height /2  
    dragging = False
    running = True
    show_result = False
    result_image = None
    overshoot_slowdown_timer = 0.0

    
    current_level = 0

    pos,vel,hole_x,hole_y,walls,moving_walls,wall_speed,wall_direction,attempt = load_level(current_level)
    screen.fill((35,35,45))

    while running:
        print("GAME LOOP RUNNING")
        dt = clock.tick(60) / 1000
        mouse = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(play_x, play_y)

        for event in pygame.event.get():
            print("Event:",event)

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN :
                print("Key pressed:", event.key)
                # home screen
                if game_state == "home":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "playing"

                # End screen
                elif game_state == "end":
                    if event.key == pygame.K_RETURN:
                        current_level = 0

                        pos, vel, hole_x, hole_y,walls,moving_walls, wall_speed, wall_direction, attempt = load_level(current_level)

                        show_result = False
                        result_image = None
                        dragging = False
                        game_state = "playing"

                # after completing a level
                elif game_state == "playing" and show_result and event.key == pygame.K_RETURN:
                    current_level += 1

                    if current_level < len(levels):
                        pos,vel,hole_x,hole_y,walls,moving_walls,wall_speed,wall_direction,attempt = load_level(current_level)

                        show_result = False
                        result_image = None
                        dragging = False

                    else:
                        game_state = "end"
                        show_result = False

            elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing"  and event.button == 1 and not show_result:
                if vel.length_squared() == 0 and mouse.distance_to(pos) <= radius:
                    dragging = True
                    overshoot_slowdown_timer = 0.0


            elif event.type == pygame.MOUSEBUTTONUP and game_state == "playing" and event.button == 1 and not show_result:

                if mouse.distance_to(pos) >= radius:
                    if dragging:
                        attempt += 1
                        print(f"strokes:{attempt}")
                else:
                    dragging = False
                if dragging:
                    dragging = False
                    pull = pos - mouse
                    if pull.length() > max_drag:
                        pull.scale_to_length(max_drag)
                    vel = pull * power

        if game_state == "home":
            screen.fill((35,35,45))

            draw_text(screen,"GOLF",text_font,(255,255,255), full_width // 2, full_height // 2 -60)
            draw_text(screen,"Press ENTER to start",text_font,(255,220,100),full_width // 2,full_height // 2 + 20)

            pygame.display.flip()
            await asyncio.sleep(0)
            continue

        if game_state == "end":
            screen.fill((35,35,45))
            draw_text(screen,"YOU COMPLETED ALL LEVELS!", text_font,(255,255,255), full_width // 2, full_height // 2 -60)
            draw_text(screen,"Press ENTER to Play Again",text_font,(255,220,100),full_width // 2, full_height // 2 + 20)

            pygame.display.flip()
            await asyncio.sleep(0)
            continue

        previous_pos = pos.copy()
        previous_rect = ball_img.get_rect(center=(round(previous_pos.x), round(previous_pos.y)))
        

        if not dragging and not show_result:
            pos += vel * dt

            movement = pos - previous_pos
            if overshoot_slowdown_timer <= 0 and vel.length() >= hole_capture_speed and movement.length_squared() > 0:
                hole_position = pygame.Vector2(hole_x, hole_y)
                to_hole = hole_position - previous_pos
                closest_t = max(0, min(1, to_hole.dot(movement) / movement.length_squared()))
                closest_position = previous_pos + movement * closest_t
                if closest_position.distance_to(hole_position) <= overshoot_slowdown_radius:
                    overshoot_slowdown_timer = overshoot_slowdown_duration

            active_friction = friction
            if overshoot_slowdown_timer > 0:
                active_friction = overshoot_friction
                overshoot_slowdown_timer = max(0, overshoot_slowdown_timer - dt)
            vel *= active_friction ** (dt * 60)

        if pos.x < radius:
            pos.x = radius
            vel.x *= -bounce
        elif pos.x > (width - radius):
            pos.x = width - radius
            vel.x *= -bounce
        if pos.y < radius:
            pos.y = radius
            vel.y *= -bounce
        elif pos.y > (height - radius):
            pos.y = height - radius
            vel.y *= -bounce

        if vel.length() < stop_speed:
            vel.update(0,0)

        # Draw
        game_surface.fill((35,145,65))


        if dragging:
            pull = pos - mouse
            length = min(pull.length(), max_drag)

            pygame.draw.line(game_surface, (200,80,80), pos, mouse, 3)

            if pull.length() > 0:
                aim_end = pos + pull.normalize() * length
                pygame.draw.line(game_surface, (0,0,0), pos, aim_end,3)

            pygame.draw.rect(game_surface, (255,100,120), (20,20,200 * length / max_drag, 16))

        # hole = pygame.draw.circle(screen,(0,0,0),(hole_x,hole_y),20)
        game_surface.blit(hole_img, (int(hole_x-20),int(hole_y-20)))
        # ball = pygame.draw.circle(screen,(255,255,255),(pos.x,pos.y),radius)
        game_surface.blit(ball_img, (int(pos.x-radius),(int(pos.y-radius))))
        ball_rect = ball_img.get_rect(center=(round(pos.x), round(pos.y)))
        game_surface.blit(flag_img, (int(hole_x),int(hole_y-82)))

        for wall in moving_walls:
            wall.y += wall_speed * wall_direction

            if wall.y >= height*0.5:
                wall_direction = -1
            elif wall.y <= height*0.4:
                wall_direction = 1

            pygame.draw.rect(game_surface,(0,0,0), wall)  
            if ball_rect.colliderect(wall):
                if (previous_rect.right <= wall.left or previous_rect.left >= wall.right):
                    pos.x = previous_pos.x
                    vel.x *= -bounce
                elif (previous_rect.bottom <= wall.top or previous_rect.top >= wall.bottom):
                    pos.y = previous_pos.y
                    vel.y *= -bounce
            
                ball_rect = ball_img.get_rect(center=(round(pos.x), round(pos.y)))  
        # walls
        for wall in walls:
            pygame.draw.rect(game_surface, (0,0,0), wall)

        for wall in walls:
            if ball_rect.colliderect(wall):
                if (previous_rect.right <= wall.left or previous_rect.left >= wall.right):
                    pos.x = previous_pos.x
                    vel.x *= -bounce
                elif (previous_rect.bottom <= wall.top or previous_rect.top >= wall.bottom):
                    pos.y = previous_pos.y
                    vel.y *= -bounce

                ball_rect = ball_img.get_rect(center=(round(pos.x), round(pos.y)))

        #text
        #draw_text("Hole-In-One",text_font,(255,0,0),width/2,20)

        offset_x,offset_y = (hole_x - pos.x),(hole_y - pos.y)
        offset = (offset_x**2 + offset_y**2)**(1/2)

        if not show_result and offset <= 20 and vel.length() < hole_capture_speed:
            pos.x,pos.y = hole_x,hole_y
            vel.update(0,0)
            show_result = True    
            if attempt == 1:
                result_image = hole_in_one
            elif attempt == 2:
                result_image = eagle
            elif attempt == 3:
                result_image = birdie
            elif attempt == 4:
                result_image = par
            elif attempt == 5:
                result_image = bogey
            elif attempt == 6:
                result_image = double_bogey
            elif attempt == 7:
                result_image = triple_bogey
            elif attempt == 8:
                result_image = quadruple_bogey
            else:
                result_image = game_over
                current_level = -1

        if show_result:
            game_surface.blit(result_image, result_image.get_rect(center=(width //2,height//2)))

            draw_text(game_surface,"Press ENTER to continue",text_font,(255,255,255),width // 2,height // 2 + 100)
        draw_text(game_surface,f"Stroke:{attempt}",text_font,(255,255,255),width//3,20)
        draw_text(game_surface,f"Level:{current_level+1}",text_font,(255,255,255),2*width//3,20)
        screen.blit(game_surface, game_area.topleft)
        pygame.display.update(game_area)
        await asyncio.sleep(0)

asyncio.run(main())
