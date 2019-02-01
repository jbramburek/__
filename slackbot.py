#!/usr/bin/env python3
import argparse
import asyncio

from boozebot import bartender, slack


async def handle_message(command, sender, channel):
    if command.lower().startswith('serve '):
        drink = command[6:].lower()
        bartender.serve(drink)
    else:
        await slack.post_message(
            channel,
            '<@{}>, I do not understand the command.'.format(sender['id']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', default='')
    args = parser.parse_args()

    slack.init(args.token, handle_message)
    loop = asyncio.get_event_loop()
    loop.create_task(slack.consumer())
    loop.create_task(slack.bot())
    loop.run_forever()


