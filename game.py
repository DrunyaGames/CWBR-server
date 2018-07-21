from twisted.internet import task
from easy_tcp.models import Message
from models import Cat
from errors import *
import random


class Chance:
    def __init__(self, powers, rand):
        self.powers = powers
        self.rand = rand

    def check(self):
        if random.randint(*self.rand) == random.randint(*self.rand):
            return random.randint(*self.powers)
        return False


class Game:

    update = 10
    chances = {
        'easy': Chance(
            (1, 10),
            (1, 10)
        ),
        'normal': Chance(
            (5, 15),
            (1, 20)
        ),
        'hard': Chance(
            (20, 30),
            (1, 100)
        )
    }

    def __init__(self, reactor):
        self.reactor = reactor

        self.task = task.LoopingCall(self.cat_finder)
        self.task.start(self.update)
        self.waiting_for_cat = {}

    def user_wait(self, user, mode):
        try:
            self.waiting_for_cat[user] = self.chances[mode]
        except KeyError:
            raise ModeError

    def cat_finder(self):
        for user, chance in self.waiting_for_cat.copy(), self.waiting_for_cat.copy().values():
            power = chance.check()
            if power:
                cat = Cat(power=power)
                user.add_cat(cat)
                user.send(Message('new_cat', cat.dump()))
                self.waiting_for_cat.pop(user)
