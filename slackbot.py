#!/usr/bin/env python3

from bartender import serve_drink

import os
import time
import re
from slackclient import SlackClient

# CONSTANTS
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
SLACK_BOT_TOKEN_ENV = 'SLACK_BOT_TOKEN'

def main():
    token = getSlackToken()
    slack_client = SlackClient(token)
    command_executor = CommandExecutor()

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read(), starterbot_id)
            if command:
                handle_command(command, channel, slack_client, command_executor)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


class CommandExecutor(object):
    def __init__(self):
        self.commands = {
            "serve" : self.serve,
            "help" : self.help
        }

    def handle_command(self, command):
        response = ""
        cmd_list = command.split(" ")
        cmd = cmd_list[0]
        cmd_args = []

        if len(cmd_list) > 1:
            cmd_args = cmd_list[1:]

        if cmd in self.commands:
            response += self.commands[cmd](cmd_args)
        else:
            response += "Sorry I don't understand the command: " + command + ". " + self.help()

        return response

    def serve(self, name):
        drink_name = name[0]
        serve_drink(drink_name)
        return "Your {0} is ready, enjoy!".format(drink_name)

    def help(self):
        response = "Currently I support the following commands:\r\n"

        for command in self.commands:
            response += command + "\r\n"

        return response


def parse_bot_commands(slack_events, bot_id):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            print(event)
            if user_id == bot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel, slack_client, executor):
    """
        Executes bot command if the command is known
    """
    response = executor.handle_command(command)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def getSlackToken():
    slack_bot_token = os.environ.get(SLACK_BOT_TOKEN_ENV)
    if slack_bot_token is None:
        print('Env var {0} is not defined!!!'.format(SLACK_BOT_TOKEN_ENV))
    return slack_bot_token


if __name__ == "__main__":
    main()
