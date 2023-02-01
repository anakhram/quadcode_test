# Quadcode test

The script is designed to send events that occurred in the Telegram channel to Splank App.

run script<br/>
`python main_api_th.py -c config.json -v`

config.json must contain `api_id`, `api_hash`, telephone number/bot token from Telegram API, also `hec_token` from Splunk <br/>
Example of config.json:<br/>
`{`<br/>
 `    "API_ID" : "your api id",` <br/>
 `    "API_HASH" : "your api hash",`<br/>
 `    "TLPH_NUMBER" :  "your tlpn number",`<br/>
 `    "SPLUNK_HEC_TOKEN" : "your hec token"`<br/>
`}`<br/>

Answers:

The script sends events to the Splank in real time, this will help quickly respond to an incident. Saving all events in the Splank will help to identify violators even if the event is deleted in the Telegram channel.

As additional data, you can track various keywords (login, password, etc.) in messages.

Tracking of possible data leakage, tracking of unauthorized users in the channel.
