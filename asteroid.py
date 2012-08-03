import os
import sys
import time
from vector import Vector2D
import math
import random
import pygame
import cProfile as profile

# GLOBALS
LEVEL = 0

#########

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
        side_length = 4
        self.rect = pygame.rect.Rect(0, 0, 2 * side_length, 2 * side_length)
        self.diag = math.sqrt(side_length ** 2 + (side_length / 2) ** 2)
        self.points = [pos, pos, pos]
        self.aspeed = math.pi / 45.0
        self.angle = 0
        self.maxspeed = 2.0
        self.speed = Vector2D(0, -0.05)
        self.velocity = Vector2D.zeros()
        self.color = pygame.Color('white')
        self.ret_color = pygame.Color(24, 24, 24)
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

        # increase current_speed, and therefore velocity
        # only rotate player's velocity when accelerating
        #if keys[pygame.K_UP] and self.velocity.Y > -self.maxspeed:
        #        self.current_speed -= self.lspeed
        #        self.velocity.Y = self.current_speed
        #        self.velocity = self.velocity.rotate(self.angle)
        if keys[pygame.K_UP]:
            new = self.velocity + self.speed.rotate(self.angle)
            if not new.length() > self.maxspeed:
                self.velocity = new

        # turn the player with right/left keys
        if keys[pygame.K_LEFT]:
            self.angle -= self.aspeed
        elif keys[pygame.K_RIGHT]:
            self.angle += self.aspeed

        # update the player's position
        self.pos += self.velocity
        self.rect.center = self.pos

        # update the lines that form our ship, they are always rotated with
        #   respect to the player's angle
        self.points[0] = Vector2D(0, -self.diag).rotate(self.angle) + self.pos
        self.points[1] = Vector2D(self.diag, 2 * self.diag).rotate(self.angle) + self.pos
        self.points[2] = Vector2D(-self.diag, 2 * self.diag).rotate(self.angle) + self.pos

    def render(self, surface, ms):
        if self.alive:
            pygame.draw.lines(surface, self.color, True, self.points)
            # draw a 'reticle'
            #direction = Vector2D(0, -512).rotate(self.angle)
            #pygame.draw.line(surface, self.ret_color, self.pos, self.pos + direction, 1)



class Asteroid(object):
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.radius = random.randint(size - (size / 10), size + (size / 10))
        xspeed = (random.random() * 2 - 1) / random.randint(1, 4)
        yspeed = (random.random() * 2 - 1) / random.randint(1, 4)
        self.velocity = Vector2D(xspeed, yspeed)
        num_sides = random.randint(8, 16)
        maxd = self.radius / 2
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
    def __init__(self, level, viewport, forbidden_rect):
        self.viewport = viewport
        # Asteroid radius-related variables
        self.min_radius = (viewport.width + viewport.height) / 200
        self.max_radius = (viewport.width + viewport.height) / 40
        self.radius_range = self.max_radius - self.min_radius
        self.small = self.min_radius
        self.med = self.small + self.radius_range / 2
        self.big = self.max_radius
        self.big_offsets = [
                Vector2D(self.med, self.med),
                #Vector2D(self.med, -self.med),
                #Vector2D(-self.med, self.med),
                Vector2D(-self.med, -self.med)
        ]
        self.med_offsets = [Vector2D(self.med, 0), Vector2D(-self.med, 0)]

        count = level + 4

        self.asteroids = [
                        Asteroid(
                            Vector2D(
                                random.randint(0, viewport.width),
                                random.randint(0, viewport.height)
                            ), self.big
                        )
                        for i in range(count)
        ]
        # move each asteroid if it initially collides with the player
        for i, a in enumerate(self.asteroids):
            if a.rect.colliderect(forbidden_rect):
                a.pos.X += forbidden_rect.centerx + a.radius
                a.pos.Y += forbidden_rect.centery + a.radius
                a.update(0.0)   # must call update to properly update its pos

    def kill(self, a):
        if a.size == self.big:
            children = [
                        Asteroid(Vector2D(a.pos.X, a.pos.Y) + off, self.med)
                        for off in self.big_offsets
            ]
            self.asteroids.extend(children)
        elif a.size == self.med:
            children = [
                        Asteroid(Vector2D(a.pos.X, a.pos.Y) + off, self.small)
                        for off in self.med_offsets
            ]
            self.asteroids.extend(children)

        # remove/delete the destroyed asteroid
        self.asteroids.remove(a)
        del(a)

    def update(self, ms):
        for a in self.asteroids:
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
    """heads up display shows Health, Score and Level"""
    def __init__(self, size, fontsize, funcs):
        assert(len(funcs) == 3)
        self.width, self.height = size
        self.font = pygame.font.Font(None, fontsize)
        self.color = pygame.Color('white')
        self.bgcolor = pygame.Color('black')
        self.funcs = funcs
        self.num_items = len(funcs)
        self.surfaces = [None for i in range(self.num_items)]

    def update(self, ms):
        #for i, func in enumerate(self.funcs):
        self.surfaces[0] = self.font.render("Health: " +
                str(int(self.funcs[0]())), 1, self.color)
        self.surfaces[1] = self.font.render("Score: " +
                str(int(self.funcs[1]())), 1, self.color)
        self.surfaces[2] = self.font.render("Level: " +
                str(int(self.funcs[2]())), 1, self.color)


    def render(self, surface, ms):
        for i, s in enumerate(self.surfaces):
            surface.blit(s, ((i + 1) * (self.width / (self.num_items + 2)), 0))


class Bullet(object):
    def __init__(self, center, direction):
        self.radius = 1
        self.color = pygame.Color('white')
        self.pos = center
        self.rect = pygame.rect.Rect(0, 0, 2*self.radius, 2*self.radius)
        self.rect.center = (center.X, center.Y)
        self.velocity = direction.normal() * 5
        self.alive = True
        self._age = 0
        self._lifetime = 2000

    def update(self, ms):
        if self.alive:
            self._age += ms

            # kill itself if it reaches its max lifetime
            if self._age > self._lifetime:
                self.alive = False
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


def get_level():
    """Hack to return the current level."""
    return LEVEL

def main():
    global LEVEL
    pygame.init()
    pygame.font.init()
    size = (640, 480)
    s = 5
    screen = pygame.display.set_mode(size)
    viewport = pygame.rect.Rect((0,0),size)
    clock = pygame.time.Clock()
    player0 = Player(Vector2D(300, 200))

    LEVEL = 1

    afield = AsteroidField(LEVEL, viewport, player0.rect)

    dirname = os.path.dirname(os.path.abspath(__file__))
    explosion_image = os.path.join(dirname, 'explosion-sprite.png')

    small_explode_image = load_image(explosion_image, scale=1)
    small_explode_sprite = load_sliced_sprites(20, 20, small_explode_image)

    med_explode_image = load_image(explosion_image, scale=2)
    med_explode_sprite = load_sliced_sprites(40, 40, med_explode_image)

    big_explode_image = load_image(explosion_image, scale=3)
    big_explode_sprite = load_sliced_sprites(60, 60, big_explode_image)

    # temp "pool" for updating/rendering particles
    explosions = list()

    bullets = list()

    hud_items = [player0.get_health, player0.get_score, get_level]
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
                if e.key == pygame.K_SPACE and player0.alive:
                    bullets.append(Bullet(player0.pos, player0.get_direction()))

        for b in bullets:
            # kill bullets that have left the viewport
            #if not viewport.colliderect(b.rect):
            #    b.alive = False
            #else:
            if b.pos.X < 0:
                b.pos.X = size[0]
            elif b.pos.X > size[0]:
                b.pos.X = 0
            elif b.pos.Y < 0:
                b.pos.Y = size[1]
            elif b.pos.Y > size[1]:
                b.pos.Y = 0
            # brute force collision checking for each bullet -> each asteroid
            for a in afield.asteroids:
                if a.rect.colliderect(b.rect):
                    b.alive = False
                    player0.score += 1
                    afield.kill(a)
                    if a.radius < afield.small:
                        explosions.append(Explosion(small_explode_sprite, a.rect.center))
                    elif a.radius < afield.med:
                        explosions.append(Explosion(med_explode_sprite, a.rect.center))
                    else:
                        explosions.append(Explosion(big_explode_sprite, a.rect.center))

        if len(afield.asteroids) == 0:
            LEVEL += 1
            afield = AsteroidField(LEVEL, viewport, player0.rect)
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

        player0.render(screen, clock.get_time())
        for b in bullets:
            b.render(screen, clock.get_time())
        for p in explosions:
            p.render(screen, clock.get_time())
        afield.render(screen, clock.get_time())
        hud.render(screen, clock.get_time())

        pygame.display.flip()
        clock.tick(60)
        pygame.time.delay(10)

    # game over
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'profile':
        profile.run("main()")
    else:
        main()
