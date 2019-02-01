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

pumps = [
    {'name': 'rum', 'pin': OutputDevice(6)},
    {'name': 'cola', 'pin': OutputDevice(13)},
    {'name': 'gin', 'pin': OutputDevice(19)},
    {'name': 'tonic', 'pin': OutputDevice(26)}]
receipts = [
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
    for p in pumps:
        p['pin'].on()
    time.sleep(5)


def turn_on():
    for p in pumps:
        p['pin'].off()
    time.sleep(5)


def pump(ingredient, duration):
    for p in pumps:
        if p['name'] == ingredient:
            logger.info('Pouring %s for %s seconds.', ingredient, duration)
            p['pin'].off()
            time.sleep(duration)
            p['pin'].on()
            logger.info('Poured %s for %s seconds.', ingredient, duration)


def serve(drink):
    logger.info('Serving %s', drink)
    for r in receipts:
        if r['name'] == drink:
            for i in r['ingredients']:
                pump(i['name'], i['duration'])
    logger.info('Served %s', drink)


def rename_pump(pump, ingredient):
    global pumps
    p = pumps[int(pump) - 1]
    pumps[int(pump) - 1] = {'name': ingredient, 'pin': p['pin']}


def ingredients():
    return [p['name'] for p in pumps]


def drinks():
    return receipts
