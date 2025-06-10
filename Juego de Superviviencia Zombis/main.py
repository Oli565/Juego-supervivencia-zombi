import pygame
import random
import math
import os

pygame.init()

# Música de fondo
pygame.mixer.init()
if os.path.exists("musica_fondo.mp3"):
    pygame.mixer.music.load("musica_fondo.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Supervivencia Zombi")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

font = pygame.font.SysFont(None, 24)
font_big = pygame.font.SysFont(None, 48)

player_name = "Oli"
round_number = 1

def show_menu():
    while True:
        screen.fill(WHITE)
        title_text = font_big.render("Supervivencia Zombi", True, BLACK)
        start_text = font.render("Presiona ENTER para jugar", True, BLACK)
        exit_text = font.render("Presiona ESC para salir", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 330))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

def show_game_over():
    while True:
        screen.fill(WHITE)
        game_over_text = font_big.render("Game Over", True, RED)
        restart_text = font.render("Presiona R para reiniciar o ESC para salir", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

def draw_player(pos):
    pygame.draw.rect(screen, BLUE, (*pos, 40, 40))
    name_text = font.render(player_name, True, BLACK)
    screen.blit(name_text, (pos[0], pos[1] - 20))

def draw_bullet(pos):
    pygame.draw.circle(screen, BLACK, pos, 5)

def draw_zombie(z):
    colors = {
        'normal': RED,
        'tank': DARK_RED,
        'mutant': PURPLE,
        'fast': ORANGE,
        'brute': BROWN,
        'boss': GRAY
    }
    color = colors.get(z['type'], RED)
    pygame.draw.rect(screen, color, (*z['pos'], z['size'], z['size']))
    max_health = {
        'normal': 3,
        'tank': 6,
        'mutant': 10,
        'fast': 2,
        'brute': 5,
        'boss': 30 + 10 * round_number
    }[z['type']]
    health_ratio = z['health'] / max_health
    pygame.draw.rect(screen, RED, (z['pos'][0], z['pos'][1] - 10, z['size'], 5))
    pygame.draw.rect(screen, GREEN, (z['pos'][0], z['pos'][1] - 10, z['size'] * health_ratio, 5))

def draw_powerups():
    for x, y, t in powerups:
        color = YELLOW if t == 'damage' else GREEN
        pygame.draw.rect(screen, color, (x, y, 20, 20))

def draw_health_bar():
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player_health / player_max_health), 20))

def draw_score():
    score_text = font.render(f"Puntuación: {score}  Mejor: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 40))

def draw_round():
    round_text = font.render(f"Ronda: {round_number}", True, BLACK)
    screen.blit(round_text, (WIDTH - 120, 10))

def main():
    global player_health, player_max_health, score, high_score, powerups, round_number

    show_menu()

    player_pos = [WIDTH // 2, HEIGHT // 2]
    bullets = []
    zombies = []
    powerups = []
    spawn_timer = 0
    bullet_timer = 0
    score = 0
    round_number = 1
    player_max_health = 10
    player_health = player_max_health
    damage_boost = False
    boost_timer = 0

    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())
    except:
        high_score = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        screen.fill(WHITE)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= 200 * dt
        if keys[pygame.K_s]: player_pos[1] += 200 * dt
        if keys[pygame.K_a]: player_pos[0] -= 200 * dt
        if keys[pygame.K_d]: player_pos[0] += 200 * dt

        if keys[pygame.K_SPACE] and bullet_timer <= 0:
            bullets.append(player_pos[:])
            bullet_timer = 0.2

        bullet_timer -= dt

        for b in bullets:
            b[1] -= 300 * dt

        bullets = [b for b in bullets if b[1] > 0]

        spawn_timer += dt
        if spawn_timer > 1.5:
            spawn_timer = 0
            zombie_type = random.choices(
                ['normal', 'tank', 'mutant', 'fast', 'brute'],
                weights=[50, 20, 10, 15, 5],
                k=1
            )[0]
            if round_number % 5 == 0:
                zombie_type = 'boss'
            size = 40 if zombie_type != 'boss' else 80
            health = {
                'normal': 3,
                'tank': 6,
                'mutant': 10,
                'fast': 2,
                'brute': 5,
                'boss': 30 + 10 * round_number
            }[zombie_type]
            speed = {
                'normal': 60,
                'tank': 40,
                'mutant': 80,
                'fast': 120,
                'brute': 70,
                'boss': 50
            }[zombie_type]
            zombies.append({
                'pos': [random.randint(0, WIDTH - size), -size],
                'type': zombie_type,
                'health': health,
                'speed': speed,
                'size': size
            })

        for z in zombies:
            dx = player_pos[0] - z['pos'][0]
            dy = player_pos[1] - z['pos'][1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                z['pos'][0] += z['speed'] * dt * dx / dist
                z['pos'][1] += z['speed'] * dt * dy / dist

        for z in zombies:
            for b in bullets:
                if (z['pos'][0] < b[0] < z['pos'][0] + z['size'] and
                    z['pos'][1] < b[1] < z['pos'][1] + z['size']):
                    z['health'] -= 2 if damage_boost else 1
                    bullets.remove(b)
                    break

        zombies = [z for z in zombies if z['health'] > 0]

        for z in zombies:
            zx, zy = z['pos']
            px, py = player_pos
            if abs(zx - px) < 30 and abs(zy - py) < 30:
                player_health -= 0.5 * dt

        if player_health <= 0:
            if score > high_score:
                with open("highscore.txt", "w") as f:
                    f.write(str(score))
            if show_game_over():
                main()
                return

        if random.random() < 0.001:
            powerups.append((random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), random.choice(['damage', 'health'])))

        for i, (x, y, t) in enumerate(powerups):
            if abs(x - player_pos[0]) < 40 and abs(y - player_pos[1]) < 40:
                if t == 'damage':
                    damage_boost = True
                    boost_timer = 5
                elif t == 'health':
                    player_health = min(player_max_health, player_health + 3)
                del powerups[i]
                break

        if damage_boost:
            boost_timer -= dt
            if boost_timer <= 0:
                damage_boost = False

        score += dt
        if int(score) // 20 + 1 > round_number:
            round_number += 1

        draw_player(player_pos)
        for b in bullets: draw_bullet(b)
        for z in zombies: draw_zombie(z)
        draw_powerups()
        draw_health_bar()
        draw_score()
        draw_round()

        pygame.display.flip()

if __name__ == "__main__":
    main()
    pygame.quit()
