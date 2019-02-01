#!/usr/bin/env python3
import argparse
import asyncio

from boozebot import bartender, slack


async def handle_serve(command, sender, channel):
    drink = command[6:].lower()
    bartender.serve(drink)


async def handle_ingredients(command, sender, channel):
    await slack.post_message(
        channel,
        'Available ingredients: {}'.format(', '.join(bartender.ingredients())))


async def handle_pump_rename(command, sender, channel):
    # @boozebot Rename pump 1-4 apple juice
    params = command.split()
    ingredient = ''.join(params[3:])
    pump = params[2]
    bartender.rename_pump(pump, ingredient)
    await slack.post_message(
        channel, 'Pump {} ingredient set to {}.'.format(pump, ingredient))


async def handle_drinks(command, sender, channel):
    drinks = bartender.drinks()
    message = 'Today\'s drink menu:'
    for d in drinks:
        message += '\n{} ({})'.format(
            d['name'],
            ', '.join(
                ['{} - {}s'.format(
                    i['name'], i['duration']) for i in d['ingredients']]))
    await slack.post_message(channel, message)


commands = {
    'exact_matches': {
        'list ingredients': handle_ingredients,
        'drinks menu': handle_drinks},
    'startswith_matches': {
        'serve ': handle_serve,
        'rename pump ': handle_pump_rename}}


async def handle_message(command, sender, channel):
    handled = False
    for c, h in command['exact_matches']:
        if c == command:
            await h(command, sender, channel)
            handled = True
    for c, h in command['startswith_matches']:
        if c.startswith(command):
            await h(command, sender, channel)
            handled = True
    if not handled:
        await slack.post_message(
            channel,
            '<@{}>, I do not understand the command.'.format(sender['id']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', default='')
    args = parser.parse_args()

    slack.init(args.token, handle_message)
    bartender.turn_off()
    loop = asyncio.get_event_loop()
    loop.create_task(slack.consumer())
    loop.create_task(slack.bot())
    loop.run_forever()
