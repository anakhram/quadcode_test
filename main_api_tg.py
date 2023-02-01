#!/usr/bin/python3
from telethon import TelegramClient, sync, events, tl
import json, datetime, requests
import sys, argparse, logging

def send2splunk(event):
    data = {
        "index" : "main",
        "event" : event,
    }
    
    response = requests.post(
        "http://localhost:8088/services/collector/event",
        headers={"Authorization": "Splunk {}".format(config['SPLUNK_HEC_TOKEN'])},
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
    )
    logging.info(f"Status code: {response.status_code}")


async def message_cb(event):
    date = str(event.date.day) + '.' + str(event.date.month) + '.' + str(event.date.year)
    time = str(event.date.hour) + ':' + str(event.date.minute) + ':' + str(event.date.second)
    ev = { "action": "new_message", "message": event.message.text, "time": time, "date": date, "author": event.message.post_author}

    send2splunk(json.dumps(ev, ensure_ascii=False))


async def channel_event_cb(event):
    if event.new_title:
        date = str(event.action_message.date.day) + '.' + str(event.action_message.date.month) + '.' + str(event.action_message.date.year)
        time = str(event.action_message.date.hour) + ':' + str(event.action_message.date.minute) + ':' + str(event.action_message.date.second)
        new_title = event.action_message.action.title
        ev = {"action" : "new_title", "new_title" : new_title, "time": time, "date": date}
        
    if event.new_pin:
        if (type(event.original_update) == tl.types.UpdatePinnedChannelMessages):
            unpinned_message = await event.get_pinned_message()
            now = datetime.datetime.now()
            date_now = str(now.day) + '.' + str(now.month) + '.' + str(now.year)
            time_now = str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
            ev = {"action" : "unpin", "message" : unpinned_message.message, "time" : time_now, 
                "date" : date_now}
            
        if (type(event.original_update) == tl.types.UpdateNewChannelMessage):
            date = str(event.action_message.date.day) + '.' + str(event.action_message.date.month) + '.' + str(event.action_message.date.year)
            time = str(event.action_message.date.hour) + ':' + str(event.action_message.date.minute) + ':' + str(event.action_message.date.second)
            pinned_message = await event.get_pinned_message()
            ev = { "action" : "pin", "message" : pinned_message.message, "time" : time, "date" : date} 
    if ev:
        send2splunk(json.dumps(ev, ensure_ascii=False))

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-v', '--verbose', nargs='?')

    return parser

if __name__ == '__main__':

    parser = createParser()
    options = parser.parse_args()
   
    with open(options.config) as file:
        config = json.load(file)

    if options.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    client = TelegramClient('main_session', config['API_ID'], config['API_HASH'])
    
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(config['TLPH_NUMBER'])
        me = client.sign_in(config['TLPH_NUMBER'], input('Enter the code: '))
    
    client.add_event_handler(message_cb, events.NewMessage)
    client.add_event_handler(channel_event_cb, events.ChatAction)

    client.run_until_disconnected()
