#!/usr/bin/env python3
import argparse
import asyncio
import logging

from boozebot import bartender, slack

logging.basicConfig()


async def handle_serve(command, sender, channel):
    drink = command[6:].lower()
    await slack.post_message(
        channel, 'Preparing {} for <@{}> ...'.format(drink, sender['id']))
    bartender.serve(drink)
    await slack.post_message(
        channel, '<@{}>, your {} is ready.'.format(sender['id'], drink))


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


async def handle_drink_remove(command, sender, channel):
    drink = command[13:].lower()
    bartender.remove_drink(drink)
    await slack.post_message(channel, 'Drink {} removed.'.format(drink))


async def handle_drink_add(command, sender, channel):
    pass


commands = {
    'exact_matches': {
        'list ingredients': handle_ingredients,
        'drinks menu': handle_drinks},
    'startswith_matches': {
        'serve ': handle_serve,
        'rename pump ': handle_pump_rename,
        'remove drink ': handle_drink_remove,
        'add drink ': handle_drink_add}}


async def handle_message(command, sender, channel):
    handled = False
    for c, h in commands['exact_matches'].items():
        if c == command:
            await h(command, sender, channel)
            handled = True
    for c, h in commands['startswith_matches'].items():
        if command.startswith(c):
            await h(command, sender, channel)
            handled = True
    if not handled:
        c = []
        for m in ['exact_matches', 'startswith_matches']:
            for cmd in commands[m].keys():
                c.append(cmd)
        message = (
            '<@{}>, I am a very primitive AI. In fact, I am more artificial '
            'than intelligent. I might need a bit more help to understand '
            'what you mean. This is the list of phrases I know: {}.').format(
            sender['id'], ', '.join(c))
        await slack.post_message(channel, message)


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
