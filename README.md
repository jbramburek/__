# BoozeBot #

Drink serving bot for Raspberry Pi using 4 pumps controlled by GPIO


## HW
TBD

## SW

### Install


1. Make sure your Raspberry is up-to-date
    ```
    sudo apt-get update
    sudo apt-get dist-upgrade
    ```
2. Install build tools
    ```
    sudo apt-get -y install gcc make build-essential git python3-dev python3-pip
    ```
3. Install requirements 
    ```
    sudo pip3 install -r requirements.txt
    ```
4. Install gpiozero (kept separately from `requirements.txt` because it does not work in Python on Windows and Mac)
    ```
    sudo pip3 install gpiozero
    ```

### Run
1. Slack token
    ```
    export SLACK_TOKEN=xoxb-<YOUR BOT TOKEN>
    ```
2. Run the bot
    ```
    pyhon3 ./slackbot.py --token=$SLACK_TOKEN
    ```
3. Write a PM to the bot on Slack
    ```
    @<botname> serve cuba libre
    ```


## TODO
* recipe management using Slack
    * add
