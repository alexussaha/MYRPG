from abc import ABC, abstractmethod
import pygame
import random
import typing
from ScreenEngine import ScreenHandle, GameSurface
import Logic


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class AbstractObject(ABC):
    @abstractmethod
    def draw(self, display):
        pass


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):
    def __init__(self, icon: typing.List[pygame.SurfaceType], action: callable, position: typing.Tuple[int, int]):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)

    def draw(self, display: GameSurface):
        display.draw_object(self.sprite[0], self.position)





class Creature(AbstractObject):
    AVAILABLE_STATS = {
        "strength": 1,
        "endurance": 1,
        "intelligence": 1,
        "luck": 1,
        "agility": 1,
        "perception": 1,
        "charisma": 1
    }

    def __init__(self, icon: typing.List[pygame.SurfaceType], stats, position):
        self.sprite = icon
        self.stats = self.AVAILABLE_STATS.copy()
        cleaned_stats = dict()
        for k, v in stats.items():
            cleaned_stats[k] = v
        self.stats.update(cleaned_stats)
        self.position = position
        self.max_hp = None
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2

    def draw(self, display: GameSurface):
        display.draw_object(self.sprite[0], self.position)


class Hero(Creature):

    def __init__(self, stats: dict, icon: pygame.SurfaceType):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__([icon], stats, pos)
        self.sprite = icon
        self.level_upper = self.level_up()

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp

    def draw(self, display: GameSurface):
        display.draw_object(self.sprite, self.position)


class Effect(Hero):
    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats['strength'] += 5
        self.stats['endurance'] += 5
        self.stats['agility'] += 5
        self.stats['luck'] += 5


class Blessing(Effect):
    def apply_effect(self):
        self.stats['strength'] += 2
        self.stats['endurance'] += 2
        self.stats['agility'] += 2
        self.stats['perception'] += 2
        self.stats['charisma'] += 2
        self.stats['intelligence'] += 2
        self.stats['luck'] += 2


class Weakness(Effect):
    def apply_effect(self):
        self.stats['strength'] -= 3
        self.stats['endurance'] -= 3
        self.stats['agility'] -= 3
        self.stats['intelligence'] -= 3


class Poisoning(Effect):
    def apply_effect(self):
        self.stats['strength'] -= 5
        self.stats['endurance'] -= 10
        self.stats['agility'] -= 5


class Enemy(Creature, Interactive):

    def __init__(self, icon: typing.List[pygame.SurfaceType], stats: dict, xp: int, position: typing.Tuple[int, int]):
        self.position = position
        self.exp = xp
        super().__init__(icon, stats, position)

    def draw(self, display: GameSurface):
        display.draw_object(self.sprite[0], self.position)

    def interact(self, engine: Logic.GameEngine, hero: Hero):
        hero.exp += self.exp
        damage = random.randint(0, max(1, int(self.stats['strength'] / hero.stats['strength'] * 50)))
        damage = min(hero.hp - 1, damage)
        hero.hp -= damage

        engine.notify(f"Earned {self.exp} XP")

        for message in hero.level_up():
            engine.notify(message)


class BestFriend(Effect):

    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] = 100
        self.stats["agility"] = 100