# __ #

Dunder

## Getting started ##

### Setup environment ###

- Install `python3`
- install virtualenv
  - `pip3 install virtualenv`
- create virtualenv `dunder`
  - `virtualenv ../../envs/dunder`
  - `source ../../envs/dunder/bin/activate`
- install dependencies
  - `pip3 install -r requirements.txt`
  
### Run dunder ###

```bash
export SLACK_BOT_TOKEN=<BOT_TOKEN>
pyhon3 ./slackbot.py
```
