#!/usr/bin/env python3
import logging

try:
    from gpiozero import OutputDevice
except Exception:
    from boozebot.fake_gpiozero import OutputDevice
import time


logger = logging.getLogger(__name__)
SMALL_SHOT = 1.5
BIG_SHOT = 2.8

_pumps = [
    {'name': 'rum', 'pin': OutputDevice(6)},
    {'name': 'cola', 'pin': OutputDevice(13)},
    {'name': 'gin', 'pin': OutputDevice(19)},
    {'name': 'tonic', 'pin': OutputDevice(26)}]
_drinks = [
    {
        'name': 'cuba libre',
        'ingredients': [
            {'name': 'rum', 'duration': 3}, {'name': 'cola', 'duration': 25}]},
    {
        'name': 'gin tonic',
        'ingredients': [
            {'name': 'gin', 'duration': 3},
            {'name': 'tonic', 'duration': 25}]}]


def turn_off():
    for p in _pumps:
        p['pin'].on()
    time.sleep(5)


def turn_on():
    for p in _pumps:
        p['pin'].off()
    time.sleep(5)


def _inventory(drink=None):
    missing = []
    unavailable = []
    for d in _drinks:
        if drink and d['name'] != drink:
            continue
        for i in d['ingredients']:
            if i['name'] not in ingredients():
                unavailable.append(d['name'])
                if i['name'] not in missing:
                    missing.append(i['name'])
    return unavailable, missing


def pour(ingredient, duration):
    for p in _pumps:
        if p['name'] == ingredient:
            logger.info('Pouring %s for %s seconds.', ingredient, duration)
            p['pin'].off()
            time.sleep(duration)
            p['pin'].on()
            logger.info('Poured %s for %s seconds.', ingredient, duration)


def serve(drink):
    logger.info('Pouring %s ...', drink)
    for r in _drinks:
        if r['name'] == drink:
            for i in r['ingredients']:
                pour(i['name'], i['duration'])
    logger.info('Poured %s.', drink)


def rename_pump(pump, ingredient):
    global _pumps
    p = _pumps[int(pump) - 1]
    _pumps[int(pump) - 1] = {'name': ingredient, 'pin': p['pin']}


def ingredients():
    return [p['name'] for p in _pumps]


def drinks():
    return _drinks


def remove_drink(drink):
    global _drinks
    for d in list(_drinks):
        if d['name'] == drink:
            _drinks.remove(d)


def add_drink(drink, ingredients):
    global _drinks
    _drinks.append({'name': drink, 'ingredients': ingredients})
