import asyncio
import json
import logging
import random
import re
import sys

import aiohttp

logger = logging.getLogger(__name__)
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
_channel = asyncio.Queue()
_bot_id = None
_token = None
_command_handler = None
_roles = {'admin': ['i314650']}
_rnd = random.Random()


async def _api_call(method, data=None):
    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', _token)
            url = 'https://slack.com/api/{0}'.format(method)
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning('Api call %s with %s failed.', method, data)
                    return None
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.warning(
            'Api call %s with %s error.', method, data, exc_info=True)


def parse_direct_mention(message_text):
    m = re.search(MENTION_REGEX, message_text)
    return (m.group(1), m.group(2).strip()) if m else (None, None)


async def sender_info(sender):
    if not sender:
        return
    s = await _api_call('users.info', {'user': sender})
    if isinstance(s, dict) and s.get('ok') is True:
        roles = []
        for r, u in _roles.items():
            if s['user']['name'] in u:
                roles.append(r)
        return {
            'id': s['user']['id'],
            'roles': roles,
            'name': s['user']['name'],
            'real_name': s['user']['real_name'],
            'first_name': s['user']['profile'].get('first_name'),
            'last_name': s['user']['profile'].get('last_name'),
            'email': s['user']['profile'].get('email'),
            'profile_real_name': s['user']['profile'].get('real_name'),
            'profile_real_name_normalized':
                s['user']['profile'].get('real_name_normalized'),
            'display_name': s['user']['profile'].get('display_name'),
            'display_name_normalized':
                s['user']['profile'].get('display_name_normalized')}
    s = await _api_call('bots.info', {'bot': sender})
    if isinstance(s, dict) and s.get('ok') is True:
        return {'id': s['bot']['id'], 'name': s['bot']['name']}


def has_role(user, role):
    return role in user.get('roles', [])


async def post_message(channel, text, username=None):
    payload = {
        'id': _rnd.randint(0, sys.maxsize), 'type': 'message',
        'as_user': username is None, 'channel': channel, 'text': text}
    if username:
        payload['username'] = username
    await _api_call('chat.postMessage', payload)


async def process_message(msg):
    message = json.loads(msg['data'])
    if message['type'] == 'message' and 'subtype' not in message:
        user_id, text = parse_direct_mention(message['text'])
        sender = await sender_info(message.get('user'))
        if user_id == _bot_id:
            if has_role(sender, 'admin'):
                if _command_handler:
                    await _command_handler(text, sender, message['channel'])


async def consumer():
    logger.info('Consumer starting.')
    while True:
        msg = await _channel.get()
        try:
            if msg['type'] == aiohttp.WSMsgType.TEXT:
                await process_message(msg)
        except asyncio.CancelledError:
            logger.info('Consumer cancelled.')
            break
        except Exception:
            logger.warning('Error processing message. %s', msg, exc_info=True)


async def bot():
    logger.info('Bot starting.')
    while True:
        rtm = await _api_call('rtm.start')
        if isinstance(rtm, dict) and rtm.get('ok') is True:
            break
        logger.warning('Error starting RTM.')
        await asyncio.sleep(1)
    logger.info('RTM started.')

    while True:
        logger.info('Authenticating.')
        b = await _api_call("auth.test")
        if b is not None and isinstance(b, dict) and 'user_id' in b:
            global _bot_id
            _bot_id = b['user_id']
            break
        logger.warning('Error reading id.')
        await asyncio.sleep(1)
    logger.info('Bot Id %s', _bot_id)

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                logger.info('Connecting to RTM.')
                async with session.ws_connect(rtm['url']) as ws:
                    logger.info('Connected to RTM.')
                    async for msg in ws:
                        await _channel.put(
                            {'type': msg.type, 'data': msg.data})
            except asyncio.CancelledError:
                logger.info('Bot cancelled.')
                break
            except Exception:
                logger.warning('Bot error.', exc_info=True)
                await asyncio.sleep(1)


def init(token, command_handler):
    global _token
    _token = token
    global _command_handler
    _command_handler = command_handler
