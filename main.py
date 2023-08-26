import pygame
import random
import sys
import os

pygame.init()

screen_width = 800
screen_height = 600
black = (0, 0, 0)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Falling Objects Game")

character_idle = pygame.image.load(os.path.join("assets", "character.png"))
character_idle = pygame.transform.scale(character_idle, (50, 50))
character_jump = pygame.image.load(os.path.join("assets", "character_jump.png"))
character_jump = pygame.transform.scale(character_jump, (50, 50))
character_left = pygame.image.load(os.path.join("assets", "character_left.png"))
character_left = pygame.transform.scale(character_left, (50, 50))
character_right = pygame.image.load(os.path.join("assets", "character_right.png"))
character_right = pygame.transform.scale(character_right, (50, 50))

current_character_image = character_idle

coin_sound = pygame.mixer.Sound(os.path.join("sounds", "coin.mp3"))
jump_sound = pygame.mixer.Sound(os.path.join("sounds", "jump.mp3"))

pygame.mixer.music.load(os.path.join("sounds", "background_music.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

character_x = screen_width // 2 - character_idle.get_width() // 2
character_y = screen_height - character_idle.get_height()
character_speed = 5
character_jump_power = -10
is_jumping = False

max_jump_power = -20
max_character_speed = 10

objects = []
object_speed = 3
speed_increment = 0.1

score = 0
font = pygame.font.Font(None, 36)

levels = [
    {"threshold": 0, "background": "background1.png", "objects": ["object1.png", "object2.png"]},
    {"threshold": 100, "background": "background2.png", "objects": ["object3.png", "object4.png"]},
    {"threshold": 250, "background": "background3.png", "objects": ["object5.png", "object6.png"]},
    {"threshold": 500, "background": "background4.png", "objects": ["object7.png", "object8.png"]}
]

current_level = 0
background = pygame.image.load(os.path.join("assets", levels[current_level]["background"]))
background = pygame.transform.scale(background, (screen_width, screen_height))
current_objects = levels[current_level]["objects"]

try:
    with open("highscore.bin", "rb") as file:
        high_score = int.from_bytes(file.read(), byteorder="big")
except FileNotFoundError:
    high_score = 0

animation_timer = 0
animation_interval = 20

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open("highscore.bin", "wb") as file:
                file.write(high_score.to_bytes(4, byteorder="big"))
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and not is_jumping and character_jump_power < max_jump_power:
        is_jumping = True

    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and character_x > 0:
        if character_speed > max_character_speed:
            character_speed = max_character_speed
        character_x -= character_speed
        current_character_image = character_left
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and character_x < screen_width - character_idle.get_width():
        if character_speed > max_character_speed:
            character_speed = max_character_speed
        character_x += character_speed
        current_character_image = character_right
    else:
        if is_jumping:
            current_character_image = character_jump
        else:
            animation_timer += 1
            if animation_timer >= animation_interval:
                animation_timer = 0
                if current_character_image == character_idle:
                    current_character_image = character_jump
                else:
                    current_character_image = character_idle

    if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and not is_jumping:
        jump_sound.play()
        is_jumping = True

    if is_jumping:
        current_character_image = character_jump
        character_y += character_jump_power
        character_jump_power += 1

        if character_y >= screen_height - current_character_image.get_height():
            character_y = screen_height - current_character_image.get_height()
            is_jumping = False
            character_jump_power = -10

    while current_level < len(levels) - 1 and (score >= levels[current_level + 1]["threshold"] or high_score >= levels[current_level + 1]["threshold"]):
        current_level += 1
        background = pygame.image.load(os.path.join("assets", levels[current_level]["background"]))
        background = pygame.transform.scale(background, (screen_width, screen_height))
        current_objects = levels[current_level]["objects"]

    if random.randint(1, 100) < 2:
        random_object_filename = random.choice(current_objects)
        random_object = pygame.image.load(os.path.join("assets", random_object_filename))
        random_object = pygame.transform.scale(random_object, (40, 40))
        random_x = random.randint(0, screen_width - random_object.get_width())
        objects.append([random_object, random_x, 0])

    for obj in objects:
        obj[2] += object_speed

    for obj in objects:
        obj_rect = obj[0].get_rect(topleft=(obj[1], obj[2]))
        character_rect = current_character_image.get_rect(topleft=(character_x, character_y))
        if character_rect.colliderect(obj_rect):
            objects.remove(obj)
            score += 1
            object_speed += speed_increment
            coin_sound.play()
            if score > high_score:
                high_score = score

    screen.fill(black)
    screen.blit(background, (0, 0))
    screen.blit(current_character_image, (character_x, character_y))

    for obj in objects:
        screen.blit(obj[0], (obj[1], obj[2]))

    score_text = font.render(f"Score: {score}   High Score: {high_score}", True, black)

    if current_level == len(levels) - 1:
        score_text_color = (255, 0, 0)
    else:
        score_text_color = black

    score_text = font.render(f"Score: {score}   High Score: {high_score}", True, score_text_color)
    screen.blit(score_text, (10, 10))

    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, black)
    screen.blit(fps_text, (10, 40))

    pygame.display.flip()

    objects = [obj for obj in objects if obj[2] < screen_height]

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    clock.tick(60)
