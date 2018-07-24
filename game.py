from twisted.internet import task
from easy_tcp.models import Message
from models import Cat
from errors import *
import random
import logging


log = logging.getLogger('GAME')


class Chance:
    debug = False

    def __init__(self, powers, rand):
        self.powers = powers
        self.rand = rand

    def check(self):
        if self.debug:
            return random.randint(*self.powers)
        a, b = random.randint(*self.rand), random.randint(*self.rand)
        log.debug('%s, %s' % (a, b))
        if a == b:
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
        ),
        'legendary': Chance(
            (20, 35),
            (1, 5)
        )
    }

    def __init__(self):
        self.waiting_for_cat = {}
        self.task = task.LoopingCall(self.cat_finder)
        self.task.start(self.update)

    def user_wait(self, user, mode):
        try:
            self.waiting_for_cat[user] = self.chances[mode]
            user.is_mining = True
        except KeyError:
            raise ModeError

    def cat_finder(self):
        copy = self.waiting_for_cat.copy()
        for user, chance in zip(copy.keys(), copy.values()):
            power = chance.check()
            if power:
                cat = Cat(power=power)
                user.add_cat(cat)
                user.is_mining = False
                user.send(Message('new_cat', cat.dump()))
                self.waiting_for_cat.pop(user)
                log.debug('User %s find new cat %s' % (user, cat))
