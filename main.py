import pygame
import pygame_gui
import random
import sys
import neat

pygame.init()

# Constants and window initialization
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Texture load
MARIO = [pygame.image.load("textures/mario_001.png"), pygame.image.load("textures/mario_002.png"), pygame.image.load("textures/mario_003.png")]
BACKGROUND = pygame.image.load("textures/background_large.png")
GROUND = pygame.image.load("textures/ground_large.png")
PIPE_SMALL = pygame.image.load("textures/pipe_short.png")
PIPE_LARGE = pygame.image.load("textures/pipe_long.png")

# UI Manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), "theme.json")
ui_text = pygame_gui.elements.UILabel(pygame.Rect((5, 0), (155, 22)), "H - Hide/Show HUD", manager)
score_text = pygame_gui.elements.UILabel(pygame.Rect((25, 620), (200, 20)), "SCORE: ", manager)
alive_text = pygame_gui.elements.UILabel(pygame.Rect((25, 640), (200, 20)), "PLAYERS ALIVE: ", manager)
generation_text = pygame_gui.elements.UILabel(pygame.Rect((25, 660), (200, 20)), "GENERATION: ", manager)
kill_text = pygame_gui.elements.UILabel(pygame.Rect((25, 680), (200, 20)), "K - KILL ALL PLAYERS", manager)
score_text.hide()
alive_text.hide()
kill_text.hide()
generation_text.hide()

# Global variables
game_speed, points,  = 10, 0
background_x, background_y = 0, 0
ground_x, ground_y = 0, 550
background_speed = 1
obstacles, players = [], []
ge, nets = [], []
pop = None
draw_hud = False
max_score = 10000


# Main player class
class Mario:
    def __init__(self, img):

        # Variables
        self.x = 110
        self.y = 470
        self.jump_height = 12.5
        self.animation_speed = 14

        # States
        self.running = True
        self.jumping = False

        # Internal variables
        self.jump_velocity = self.jump_height
        self.images = img
        self.image = self.images[0]
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_index = 0
        self.distance_to_next_pipe = 0
        self.next_pipe_type = 0

    # Update function
    def update(self):
        if self.running:
            self.run()

        if self.jumping:
            self.jump()

        # Update animation
        if self.step_index >= self.animation_speed:
            self.step_index = 0

        # Get distance and type of next pipe
        if obstacles[0].rect.centerx - self.rect.x > 0:
            self.distance_to_next_pipe = obstacles[0].rect.centerx - self.rect.x
            self.next_pipe_type = obstacles[0].pipe_type
        else:
            self.distance_to_next_pipe = obstacles[1].rect.centerx - self.rect.x
            self.next_pipe_type = obstacles[1].pipe_type

    # Jump function
    def jump(self):

        self.image = self.images[2]

        # Apply gravity
        if self.jumping:
            self.rect.y -= self.jump_velocity * 4
            self.jump_velocity -= 0.8

        # If on ground change to running state
        if self.jump_velocity <= -self.jump_height and self.rect.y >= self.y - 30:
            self.jumping = False
            self.running = True
            self.jump_velocity = self.jump_height

    # Run function
    def run(self):
        self.image = self.images[self.step_index // (self.animation_speed // 2)]
        self.rect.x = self.x
        self.rect.y = self.y
        self.step_index += 1

    # Onscreen draw function
    def draw(self):
        WINDOW.blit(self.image, (self.rect.x, self.rect.y))
        if draw_hud:
            pygame.draw.rect(WINDOW, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
            if obstacles[0].rect.centerx - self.rect.x > 0:
                pygame.draw.line(WINDOW, self.color, (self.rect.centerx, self.rect.centery), obstacles[0].rect.midtop, 2)
            else:
                pygame.draw.line(WINDOW, self.color, (self.rect.centerx, self.rect.centery), obstacles[1].rect.midtop, 2)


# Base class for pipe
class Pipe:
    def __init__(self, image, pipe_type):
        self.image = image
        self.pipe_type = pipe_type
        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_WIDTH + 50

    def update(self):
        self.rect.x -= game_speed

    def draw(self):
        WINDOW.blit(self.image, (self.rect.x, self.rect.y))


# Small pipe class
class SmallPipe(Pipe):
    def __init__(self, image):
        super().__init__(image, 1)
        self.rect.y = 422


# Large pipe class
class LargePipe(Pipe):
    def __init__(self, image):
        super().__init__(image, 2)
        self.rect.y = 358


# Pipe Generator Class
class PipeGenerator:
    def __init__(self):

        # Variables
        self.timeBetweenSpawn = 0
        self.startTimeBetweenSpawn = 1.5
        self.decreaseTime = 0.02
        self.minTime = 0.75

    def update(self):
        if self.timeBetweenSpawn <= 0:
            pipetype = random.randint(1, 2)
            if pipetype == 1:
                obstacles.append(SmallPipe(PIPE_SMALL))
            else:
                obstacles.append(LargePipe(PIPE_LARGE))

            # Make pipes spawn faster
            self.timeBetweenSpawn = self.startTimeBetweenSpawn + random.random() / 2
            if self.startTimeBetweenSpawn >= self.minTime:
                self.startTimeBetweenSpawn -= self.decreaseTime
        else:
            self.timeBetweenSpawn -= 0.016


# Function to update stats
def statistics():
    global players, pop
    score_text.set_text("SCORE: " + str(points))
    alive_text.set_text("PLAYERS ALIVE: " + str(len(players)))
    generation_text.set_text("GENERATION: " + str(pop.generation + 1))


# Function to update ground
def ground():
    global ground_x, ground_y, game_speed

    img_width = GROUND.get_width()
    WINDOW.blit(GROUND, (ground_x, ground_y))
    WINDOW.blit(GROUND, (img_width + ground_x, ground_y))

    if ground_x <= -img_width:
        ground_x = 0

    ground_x -= game_speed


# Function to update background
def background():
    global background_x, background_y, game_speed
    img_width = BACKGROUND.get_width()
    WINDOW.blit(BACKGROUND, (background_x, background_y))
    WINDOW.blit(BACKGROUND, (img_width + background_x, background_y))

    if background_x <= -img_width:
        background_x = 0

    background_x -= background_speed


# Function to remove player from players list
def remove(index):
    players.pop(index)
    ge.pop(index)
    nets.pop(index)


# Function to kill all players (saving their fitness)
def kill_players():
    global players, ge, nets
    players = []
    # Update fitness for remaining players
    for i in range(0, len(ge)):
        ge[i].fitness = points

    ge = []
    nets = []


# Main loop function
def eval_genomes(genomes, config):

    # Global variables
    global game_speed, points, obstacles, players, ge, nets, draw_hud

    clock = pygame.time.Clock()
    running = True
    deque_first_obstacle = False

    players = []
    obstacles = []
    ge = []
    nets = []
    points = 0

    pg = PipeGenerator()

    for genome_id, genome in genomes:
        players.append(Mario(MARIO))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    # Game loop
    while running:

        # Increment points
        points += 1

        # Exit condition
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                # Kill all players
                if event.key == pygame.K_k:
                    kill_players()
                # Activate/Remove HUD
                if event.key == pygame.K_h:
                    draw_hud = not draw_hud

        if points >= max_score:
            kill_players()

        # Draw background
        background()

        # Update pipe generator
        pg.update()

        # Foreach player check neural net to see if it needs to jump
        for i, player in enumerate(players):
            output = nets[i].activate((player.rect.y, player.distance_to_next_pipe, player.next_pipe_type))
            if output[0] >= 0.5 and player.rect.y == player.y:
                player.jumping = True
                player.running = False

        # If no more players, end generation
        if len(players) == 0:
            break

        # Update and draw obstacles
        for obstacle in obstacles:
            obstacle.draw()
            obstacle.update()

            # Delete obstacle if off-screen
            if obstacle.rect.x < -obstacle.rect.width - 10:
                deque_first_obstacle = True

            for i, player in enumerate(players):
                if player.rect.colliderect(obstacle.rect):
                    ge[i].fitness = points
                    remove(i)

        # Update and draw players
        for player in players:
            player.update()
            player.draw()

        # To avoid deque-ing in iteration flag when the first obstacle needs to be removed
        if deque_first_obstacle:
            obstacles.pop(0)
            deque_first_obstacle = False

        # Draw ground
        ground()

        if draw_hud:
            score_text.show()
            alive_text.show()
            kill_text.show()
            generation_text.show()
            statistics()
        else:
            score_text.hide()
            alive_text.hide()
            kill_text.hide()
            generation_text.hide()

        # Draw UI
        manager.draw_ui(WINDOW)
        manager.update(1)

        clock.tick(60)
        pygame.display.update()


# Neat setup
def run(path):
    global pop

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        path
    )

    # Run training
    pop = neat.Population(config)
    pop.run(eval_genomes, 20)


if __name__ == '__main__':
    pygame.display.set_caption("Mario Runner AI")

    config_path = "config.txt"
    run(config_path)

