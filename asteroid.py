import os
import sys
import time
from vector import Vector2D
import math
import random
import pygame
import cProfile as profile

R = None


def load_image(name, scale=1, colorkey=None):
    fullname = os.path.abspath(name.replace('../', '../../res/'))
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    image = pygame.transform.scale(image, (int(image.get_width() * scale),
            int(image.get_height() * scale)))
    return image


def load_sliced_sprites(w, h, master_image):
    '''
    Specs :
        Master can be any height.
        Sprites frames width must be the same width
        Master width must be len(frames)*frame.width
    Assuming you ressources directory is named "."
    '''
    images = []

    #scalew = int(master_image.get_width() * scale)
    #scaleh = int(master_image.get_height() * scale)
    #master_image = pygame.transform.scale(master_image, (scalew, scaleh))

    master_width, master_height = master_image.get_size()
    for j in xrange(int(master_height/h)):
        images.append([])
        for i in xrange(int(master_width/w)):
            images[j].append(master_image.subsurface((i*w,j*h,w,h)))
    return images


class DUMMY(object):
    value = None


class Player(object):
    def __init__(self, pos=Vector2D(320, 240)):
        self.pos = pos
        side_length = 8
        self.rect = pygame.rect.Rect(0, 0, 2 * side_length, 2 * side_length)
        self.diag = math.sqrt(side_length ** 2 + (side_length / 2) ** 2)
        self.points = [pos, pos, pos]
        self.lspeed = 0.04
        self.despeed = self.lspeed / 2
        self.maxspeed = 2.0
        self.aspeed = math.pi / 135.0
        self.angle = 0
        self.velocity = Vector2D.zeros()
        self.color = pygame.Color('white')
        self.health = 100
        self.alive = True
        self.score = 0
        self.update(0.0)

    def get_health(self):
        return self.health

    def get_score(self):
        return self.score

    def get_direction(self):
        return Vector2D(0, -1).rotate(self.angle)

    def update(self, ms):
        if not self.alive:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and self.velocity.Y < self.maxspeed:
                self.velocity.Y += self.lspeed
        elif keys[pygame.K_UP] and self.velocity.Y > -self.maxspeed:
                self.velocity.Y -= self.lspeed
        else:
            if self.velocity.Y > 0:
                self.velocity.Y -= self.despeed
            elif self.velocity.Y < 0:
                self.velocity.Y += self.despeed

        if keys[pygame.K_LEFT]:
            self.angle -= self.aspeed
        elif keys[pygame.K_RIGHT]:
            self.angle += self.aspeed

        self.pos += self.velocity.rotate(self.angle)
        self.rect.center = self.pos
        self.points[0] = Vector2D(0, -self.diag).rotate(self.angle) + self.pos
        self.points[1] = Vector2D(self.diag, 2 * self.diag).rotate(self.angle) + self.pos
        self.points[2] = Vector2D(-self.diag, 2 * self.diag).rotate(self.angle) + self.pos

    def render(self, surface, ms):
        if self.alive:
            pygame.draw.lines(surface, self.color, True, self.points)


class Asteroid(object):
    def __init__(self, pos, radius_range):
        self.pos = pos
        self.radius = random.randint(radius_range[0], radius_range[1])
        xspeed = (random.random() * 2 - 1) / random.randint(1, 5)
        yspeed = (random.random() * 2 - 1) / random.randint(1, 5)
        self.velocity = Vector2D(xspeed, yspeed)
        num_sides = random.randint(5, 10)
        maxd = 2 * self.radius / num_sides
        a = 2 * math.pi / num_sides
        v = Vector2D(self.radius, 0.0)
        self.points = list()
        self.offsets = list()
        for i in range(num_sides):
            xy = random.randint(0, 1)
            d = random.randint(-maxd, maxd)
            if xy:
                offset = v + Vector2D(d, 0)
                self.offsets.append(offset)
                self.points.append(offset + self.pos)
            else:
                offset = v + Vector2D(0, d)
                self.offsets.append(offset)
                self.points.append(offset + self.pos)
            v = v.rotate(a)

        self.rect = pygame.rect.Rect(0, 0, int(self.radius * 1.9), int(self.radius * 1.9))
        self.rect.center = (self.pos.X, self.pos.Y)
        self.update(0.0)
        self.color = pygame.Color('white')
        self.alive = True

    def update(self, ms):
        self.pos += self.velocity
        self.rect.center = (self.pos.X, self.pos.Y)
        # just update each point comprising the asteroid
        for i, offset in enumerate(self.offsets):
            self.points[i] = offset + self.pos

    def render(self, surface, ms):
        #pygame.draw.circle(surface, self.color, (int(self.pos.X), int(self.pos.Y)), self.radius, 1)
        pygame.draw.lines(surface, self.color, True, self.points)

class AsteroidField(object):
    def __init__(self, count=15, viewport=pygame.rect.Rect(0,0,640,480)):
        self.viewport = viewport
        # Asteroid radius-related variables
        self.min_radius = (viewport.width + viewport.height) / 200
        self.max_radius = (viewport.width + viewport.height) / 40
        self.radius_range = self.max_radius - self.min_radius
        self.small = self.min_radius + self.radius_range / 3
        self.med = self.small + self.radius_range / 3
        self.big = self.max_radius

        self.asteroids = [
                        Asteroid(
                            Vector2D(
                                random.randint(0, viewport.width),
                                random.randint(0, viewport.height)
                            ),
                            (self.min_radius, self.max_radius)
                        )
                        for i in range(count)
        ]

    def update(self, ms):
        for a in self.asteroids:
            if not a.alive:
                self.asteroids.remove(a)
                del(a)
            else:
                if a.pos.X < self.viewport.left:
                    a.pos.X = self.viewport.right
                elif a.pos.X > self.viewport.right:
                    a.pos.X = self.viewport.left
                if a.pos.Y < self.viewport.top:
                    a.pos.Y = self.viewport.bottom
                elif a.pos.Y > self.viewport.bottom:
                    a.pos.Y = self.viewport.top
                a.update(ms)

    def render(self, surface, ms):
        for a in self.asteroids:
            a.render(surface, ms)


class Camera(object):
    def __init__(self, size, rect, lock):
        self.rect = pygame.Rect((0,0),size)
        self.bounds = rect
        self.lock = lock

    def update(self, ms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS]:
            self.rect.inflate_ip(2, 2)
        elif keys[pygame.K_MINUS]:
            self.rect.inflate_ip(-2, -2)
        self.rect.center = self.lock()
        self.rect.clamp_ip(self.bounds)


class HUD(object):
    def __init__(self, size, fontsize, funcs):
        self.width, self.height = size
        self.font = pygame.font.Font(None, fontsize)
        self.color = pygame.Color('white')
        self.bgcolor = pygame.Color('black')
        self.funcs = funcs
        #self.surfaces = range(len(funcs))
        self.surfaces = [None, None]

    def update(self, ms):
        #for i, func in enumerate(self.funcs):
        self.surfaces[0] = self.font.render("Health: " +
                str(int(self.funcs[0]())), 1, self.color)
        self.surfaces[1] = self.font.render("Score: " +
                str(int(self.funcs[1]())), 1, self.color)

    def render(self, surface, ms):
        for i, s in enumerate(self.surfaces):
            surface.blit(s, ((i + 1) * (self.width / (len(self.surfaces) + 2)), 0))


class Bullet(object):
    def __init__(self, center, direction):
        self.radius = 1
        self.color = pygame.Color('white')
        self.pos = center
        self.rect = pygame.rect.Rect(0, 0, 2*self.radius, 2*self.radius)
        self.rect.center = (center.X, center.Y)
        self.velocity = direction.normal() * 2
        self.alive = True
        self._age = 0
        self._lifetime = 2000

    def update(self, ms):
        if self.alive:
            self._age += ms

            #if self._age > self._lifetime:
            #    self.alive = False
            self.pos += self.velocity
            self.rect.center = (self.pos.X, self.pos.Y)

    def render(self, surface, ms):
        if self.alive:
            pygame.draw.circle(surface, self.color, (int(self.pos.X), int(self.pos.Y)), self.radius)


class Explosion(object):
    def __init__(self, image, center):
        self._images = image
        self.image = self._images[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.alive = True

        self._frameset = 0
        self._frame = 0
        self._delay = 99
        self._frame_timer = 0
        # determines whether sprite should look forward when not moving

    def prevent_collision(self, other):
        if self.rect.colliderect(other.rect) and not self.stunned:
            # direct player away from collision
            self.velocity -= 2 * self.velocity
            self.health -= 1
            self.stunned = True

    def update(self, ms):
        if self.alive:
            self._frame_timer += ms

            if self._frame_timer > self._delay:
                self._frame += 1
                if self._frame >= len(self._images[self._frameset]):
                    self._frame = 0
                    self.alive = False
                self.image = self._images[self._frameset][self._frame]
                self._frame_timer = 0

    def render(self, surface, ms):
        if self.alive:
            surface.blit(self.image, self.rect)


def main():
    pygame.init()
    pygame.font.init()
    size = (640, 480)
    s = 5
    screen = pygame.display.set_mode(size)
    viewport = pygame.rect.Rect((0,0),size)
    clock = pygame.time.Clock()
    player0 = Player(Vector2D(300, 200))

    afield = AsteroidField(10, viewport)

    small_explode_image = load_image('explosion-sprite.png', scale=1)
    small_explode_sprite = load_sliced_sprites(20, 20, small_explode_image)

    med_explode_image = load_image('explosion-sprite.png', scale=2)
    med_explode_sprite = load_sliced_sprites(40, 40, med_explode_image)

    big_explode_image = load_image('explosion-sprite.png', scale=3)
    big_explode_sprite = load_sliced_sprites(60, 60, big_explode_image)

    # temp "pool" for updating/rendering particles
    explosions = list()

    bullets = list()

    hud_items = [player0.get_health, player0.get_score]
    #for player in players:
    #    healths.append(player.get_health)
    hud = HUD(size, 32, hud_items)

    game_over_font = pygame.font.Font(None, 72)
    game_over_msg = game_over_font.render("GAME OVER", 1, pygame.Color('white'))
    offX = (viewport.width - game_over_msg.get_width()) / 2
    offY = (viewport.height - game_over_msg.get_height()) / 2

    #camera = Camera(size, tilemap0.rect, player0.get_pos)

    black = pygame.Color('black')
    screen.fill(black)
    pygame.display.update()

    game_over = False
    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_SPACE:
                    bullets.append(Bullet(player0.pos, player0.get_direction()))

        # kill bullets that have left the viewport
        for b in bullets:
            if not viewport.colliderect(b.rect):
                b.alive = False
            else:
                for a in afield.asteroids:
                    if a.rect.colliderect(b.rect):
                        b.alive = False
                        player0.score += 1
                        if a.radius < afield.small:
                            explosions.append(Explosion(small_explode_sprite, a.rect.center))
                        elif a.radius < afield.med:
                            explosions.append(Explosion(med_explode_sprite, a.rect.center))
                        else:
                            explosions.append(Explosion(big_explode_sprite, a.rect.center))
                        a.alive = False

        if len(afield.asteroids) == 0:
            game_over = True
        for a in afield.asteroids:
            if player0.alive and a.rect.colliderect(player0.rect):
                player0.health -= 1
                if player0.health <= 0:
                    explosions.append(Explosion(big_explode_sprite, player0.rect.center))
                    # game over
                    player0.alive = False
                    game_over = True

        if player0.pos.X < 0:
            player0.pos.X = size[0]
        elif player0.pos.X > size[0]:
            player0.pos.X = 0
        elif player0.pos.Y < 0:
            player0.pos.Y = size[1]
        elif player0.pos.Y > size[1]:
            player0.pos.Y = 0

        player0.update(clock.get_time())
        afield.update(clock.get_time())
        for bull in bullets:
            if not bull.alive:
                bullets.remove(bull)
                del(bull)
            else:
                bull.update(clock.get_time())
        for pop in explosions:
            if not pop.alive:
                explosions.remove(pop)
                del(pop)
            else:
                pop.update(clock.get_time())

        hud.update(clock.get_time())

        screen.fill(black)

        if game_over:
            screen.blit(game_over_msg, (offX, offY))

        for b in bullets:
            b.render(screen, clock.get_time())
        for p in explosions:
            p.render(screen, clock.get_time())
        afield.render(screen, clock.get_time())
        player0.render(screen, clock.get_time())
        hud.render(screen, clock.get_time())

        pygame.display.flip()
        clock.tick(60)
        #pygame.time.delay(100)

    # game over
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'profile':
        profile.run("main()")
    else:
        main()
