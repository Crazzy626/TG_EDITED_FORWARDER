"""
Telegram Messages Forwarder

[Version 2.0:]

    [07.07.2023] Added possibility to monitor "Edited Messages"

    First, potential Signal message appears in Channel - but it has no full Signal content yet
    We can filter potential Signal message using some logic:
    Example: First potential Signal message:
    ---------------------------------------
    SELL GOLD SIGNAL
    ---------------------------------------
    After a while (X minutes) - the message is edited and full Signal content is added
    Need to monitor such messages and retrieve Signal edited content (ex.: forward to message parser and positions create)

    Example: Potential Signal message that had been edited:

    ---------------------------------------
    SELL GOLD SIGNAL

    LOW RISK

    Entry: 1998.5

    TP1: 1996.5
    TP1: 1994.5

    SL: 2000.50
    ---------------------------------------

[Version 1.0:]

- Monitor a Telegram Channel messages
- Get Message Data
- Analyze message for a Signal
- Forward messages to other Channel

"""

import asyncio
import logging
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest, GetDialogsRequest
from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerEmpty
from termcolor import colored
import addons as ad
from __init__ import LOG_FOLDER, SETTINGS_DIR, TELEGRAM_CFG_FILE


# [LOG Init]
log = ad.init_log(f'main.log', LOG_FOLDER, "main")

# Updated in {new_message_handler} and then msg check occurs in {check_message_edit}
msg_edit_monitor_list = []

# Main OBJ to keep all Channels Data. Updated by {create_channels_data}
channels_data: dict = {}


async def new_message_handler(event):

    # region [New Message > Create Message OBJ]
    msg_obj = {}

    try:
        # msg_obj["message_obj"] = event.message
        msg_obj["channel_id"] = event.message.peer_id.channel_id
        msg_obj["message_txt"] = event.message.message
        msg_obj["message_id"] = event.message.id
        # Media Type: Will be OBJ: MessageMediaPhoto(photo=Photo(id=5440445674278731901 . . .age_obj.id
        msg_obj["message_media"] = None
        is_media_type = False
        if event.message.media is not None:
            msg_obj["message_media"] = event.message.media
            is_media_type = True
        msg_obj["message_reply_id"] = None
        if event.message.reply_to is not None:
            msg_obj["message_reply_id"] = event.message.reply_to.reply_to_msg_id
    except Exception as ex:
        print(f'[!] Exception - while decoding Message Event. ErrMsg: {ex}')
        log.exception(f'Exception - while decoding Message Event. ErrMsg: {ex}')
        return

    # endregion

    # region [Edited Messages Monitor]
    '''
    - Verify "is_monitor_edited" KEY in {channels_data} to see if this message needs to be monitored
    - See if message isa Potential Signal > add message to monitor list if it passes the filter by match string 
        {monitor_edited_filter_str} for this Channel
    - Using Channel ID to get the channel data from  {channels_data}
    - Add KEY: "checks_count" 
    - Add Message to {msg_edit_monitor_list}
    '''

    is_edit_monitored = False
    edit_monitor_str = 'False'

    channel_obj = channels_data[msg_obj["channel_id"]]

    if channel_obj["is_monitor_edited"]:                # Message needs to be monitored
        # See if passes filter
        if channel_obj["monitor_edited_filter_str"] in msg_obj["message_txt"]:        # Potential Signal message
            msg_obj["checks_count"] = 0
            msg_edit_monitor_list.append(msg_obj)
            log.info(f'Message [{msg_obj["message_id"]}] > is from "edit monitored" channel > added to edit monitor list')
            edit_monitor_str = 'True > passed filter'
            is_edit_monitored = True
        else:
            log.info(f'Message [{msg_obj["message_id"]}] > is from "edit monitored" channel, but not passed the string filter')
            edit_monitor_str = 'True > not passed filter'
    else:
        log.info(f'Message [{msg_obj["message_id"]}] > not from "edit monitored" channel')

    edit_monitor_str = f'--- {colored("edit monitor", "green")}{45 * "-"}\n{edit_monitor_str}'

    # endregion

    # [Logging]

    tmp_str = f'\n[{ad.get_str_timeprint()}]: {colored("NEW MESSAGE EVENT:", "light_green")}\n\n' \
              f'=== {colored("data", "light_yellow")} {53 * "="}\n' \
              f'    message_id:          {msg_obj["message_id"]}\n' \
              f'    channel_id:          {msg_obj["channel_id"]}\n' \
              f'    message_reply_id:    {msg_obj["message_reply_id"]}\n' \
              f'    message_media:       {is_media_type}\n' \
              f'--- {colored("message", "light_blue")} {50 * "-"}\n' \
              f'{msg_obj["message_txt"]}\n' \
              f'{edit_monitor_str}\n' \
              f'{62 * "="}\n'

    print(f'\n{tmp_str}')
    log.info(f'New Message:\n{msg_obj}')

    # If message is Edit Monitored - return here (will be forwarded later after edit check procedure)
    # If message is not Edit Monitored or Is Edit Monitored but not passed the Filter - just forward it as normal

    if is_edit_monitored:
        return

    # region [Message Forward]

    '''
    Initially {forward_txt} is the same message that we received
    Then check if this message is a "replied" type
    If it is replied message then {forward_txt} need to contain this actual message + replied message
    Replied Message need to be retrieved
    '''

    # Actual message - that will be updated with "replied" message if it is the case
    forward_txt = msg_obj["message_txt"]

    # region [Message ReplyType]

    '''    
    If this actual message is a Reply to other message > retrieve "Replied Message" {replied_message}
    Need to get "Chat Entity" - in order to retrieve "replied" message.
    Note: if need to get Chat Entity by Chat ID > await event.client.get_entity(chat_id)
    In our case - it is same chat (in this event) so can get chat entity > {await event.get_chat()}
    '''

    if msg_obj["message_reply_id"] is not None:

        print(f'[+] Message [ReplyType] detected: this message: [{msg_obj["message_id"]}] ---> replied to: [{msg_obj["message_reply_id"]}]')
        log.info(f'Message [ReplyType] detected: this message: [{msg_obj["message_id"]}] ---> replied to: [{msg_obj["message_reply_id"]}]')

        # [Chat Entity]

        chat_entity = None

        try:
            chat_entity = await event.get_chat()
            log.debug(f'Message [ReplyType]: "replied_message" Chat Entity retrieved success:\n{chat_entity}')
        except Exception as ex:
            print(f'[!] Exception - while getting "replied_message" Chat Entity. ErrMsg: {ex}')
            log.exception(f'Exception - while getting "replied_message" Chat Entity. ErrMsg: {ex}')

        # [Replied Message]

        # Retrieve Message OBJ by message by ID > Message(id=193, ... message='a', ...
        replied_message = None

        if chat_entity is not None:
            try:
                replied_message = await tgclient.get_messages(chat_entity, ids=msg_obj["message_reply_id"])
                log.info(f'Message [ReplyType]: "replied_message" Message OBJ retrieved success:\n{replied_message}')
            except Exception as ex:
                print(f'[!] Exception - while getting "replied_message" Message OBJ. ErrMsg: {ex}')
                log.exception(f'Exception - while getting "replied_message"  Message OBJ. ErrMsg: {ex}')

        # If {replied_message} could not be retrieved - log Warning and only "actual" message will be forwarded

        if replied_message is None:
            print(
                f'[!] Warning - "replied_message" Message OBJ could not be retrieved - only "actual" message will be forwarded')
            log.warning(
                f'[!] Warning - "replied_message" Message OBJ could not be retrieved - only "actual" message will be forwarded')
        else:
            # Log "replied_message" text
            print(f'--- replied message {50 * "-"}\n'
                  f'{replied_message.message}\n'
                  f'{70 * "-"}\n')

            # Create new {forward_txt} to contain replied message + this actual message
            forward_txt = f'{replied_message.message}\n{20 * "-"}\n{msg_obj["message_txt"]}'

    # endregion // Message ReplyType

    # region [Message Send]

    '''
    Forward "actual" message or "actual" + "replied_message" > according to all above processing
    
    List of channels where need to forward - find it on channel_obj by "forward_to" KEY
        
    '''

    await send_message(forward_txt, channel_obj, msg_obj)

    # endregion // Message Send

    # endregion // Message Forward


async def send_message(forward_txt, channel_obj, msg_obj):
    """
    Send message to all target channels
    :param forward_txt: text to be sent
    :param channel_obj: Channel OBJ
    :param msg_obj: Message OBJ
    :return:
    """

    for target_channel in channel_obj["forward_to_list"]:
        print(f'[+] Sending Message [{msg_obj["message_id"]}] '
              f'FROM: {channel_obj["chat_id"]} ({channel_obj["chat_name"]}) '
              f'TO:   {target_channel["chat_id"]} ({target_channel["chat_name"]})\n')

        # Add message header
        forward_txt = f'@@@{channel_obj["chat_id"]} ({channel_obj["chat_name"]})\n{forward_txt}'

        try:
            # await tgclient.send_message(target_map_obj[0], message=forward_txt)
            # Note: {file} param will be None - if no media detected.
            # If media - detected - then "MessageMediaPhoto" OBJ will be sent from (message_media = MessageMediaPhoto(photo=Photo(id=5440445674278731901 . . .)
            await tgclient.send_message(target_channel["chat_id"], file=msg_obj["message_media"], message=forward_txt)
            print(f'[+] Message sent OK\n')
        except Exception as ex:
            print(f'[!] Exception - while sending message [{msg_obj["message_id"]}]. ErrMsg: {ex}')
            log.exception(f'Exception - while sending message [{msg_obj["message_id"]}]. ErrMsg: {ex}')

        await asyncio.sleep(0.5)


async def channels_peer_update(tgclient, channels_data) -> bool | str:
    """
    Need to get Chanel Peer OBJ for channels where we need to retrieve messages history
    This applies to channels that has "is_monitor_edited" KEY

    Getting Chanel Peer by requesting all channels then selecting needed

    Update data for {channels_peer} dict
    Main aim is to update {peerOBJ} KEY for the monitored channels
    Using {GetDialogsRequest} method to retrieve ALL User's dialogs and search for the Target Channel there
    Returned OBJ will have "peer" OBJ that will be stored in {channels_peer} dict for this Channel

    :param tgclient:
    :param channels_data: is the main Channels Data list that stores all required data for all channels
    :return:
    """

    # Telethon Dialogs Request OBJ

    get_dialogs = GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=100,
        hash=0
    )
    try:
        dialogs_obj = await tgclient(get_dialogs)
    except Exception as ex:
        return f'[main]: Exception on "GetDialogsRequest" for channels peer OBJ update. ErrMsg: {ex}'

    if dialogs_obj is None or len(dialogs_obj.dialogs) == 0:
        return f'[main]: Failed to retrieve channels dialogs for channels peer OBJ update'

    print(f'[debug]:[main]: dialogs retrieved - total [{len(dialogs_obj.dialogs)}]')

    # Filter only needed channels - those which we will want to monitor for edited messages

    for ch_key, ch_data in channels_data.items():

        if not ch_data["is_monitor_edited"]:
            continue

        print(f'[debug]:[main]: searching Peer OBJ for channel [{ch_key}]')

        # Search channel by its ID and get Peer OBJ
        is_found = False
        for dlg_obj in dialogs_obj.dialogs:
            if dlg_obj.peer.channel_id == ch_key:
                ch_data["channel_peer_obj"] = dlg_obj.peer
                print(f'[debug]:[main]: Found Peer OBJ for channel [{ch_key}]')

                # DEBUG
                # print(dlg_obj)
                # print(dlg_obj.peer)
                # msg_data = await tgclient.get_messages(dlg_obj.peer, limit=1, ids=300)
                # print(msg_data)

                is_found = True
                break

        if not is_found:
            return f'[main]: Failed to retrieve Peer OBJ for channel [{ch_key}] - channel with such ID not found in dialogs list returned by "GetDialogsRequest"'

    return True


async def check_message_edit(tgclient, msg_obj, channel_peer_obj) -> bool | str:
    """
    - Check if message had been edited
    - If Edited - get new text
      Store message text in same {msg_obj}

    {msg_obj} is created in {new_message_handler} - see there all KEYS

    msg_obj = {
        "msg_id": XXX,
        "channel_id": YYY,
        "message_txt": "ZZZ",
        "checks_count": 0,
        ....
    }
       :param msg_obj:
       :return:
    """

    # Retrieve message by ID using Channel Peer OBJ

    msg_data = await tgclient.get_messages(channel_peer_obj, limit=1, ids=msg_obj['message_id'])

    if msg_data is None:
        return f'[debug]:[edit_monitoring]: Failed to retrieve Message [{msg_obj["msg_id"]}] from history'

    # [Message Edited]
    # Verify by {edit_date} KEY
    # If message was not edited - it will be None

    if msg_data.edit_date is not None:          # Message Edited
        last_edited = msg_data.edit_date
        print(f'[debug]:[edit_monitoring]: Message [{msg_obj["message_id"]}] > Edit time: [{last_edited}]  |  checks_count = {msg_obj["checks_count"]}')
        log.debug(f'[debug]:[edit_monitoring]: Message [{msg_obj["message_id"]}] > Edit time: [{last_edited}]  |  checks_count = {msg_obj["checks_count"]}')
        # Set Message OBJ with new edited message
        msg_obj["message_txt"] = msg_data.message
        return True
    else:
        msg_obj["checks_count"] += 1
        print(f'[debug]:[edit_monitoring]: Message [{msg_obj["message_id"]}] not edited  |  checks_count = {msg_obj["checks_count"]}')
        return False


async def main_loop(tgclient, channels_data, msg_edit_check_interval, msg_edit_max_checks):
    global msg_edit_monitor_list
    msg_edit_trigger_time = 0  # To know if time comes for edited messages check

    # region [ Main Infinite Loop ]

    '''
    [ ASYNCIO MAGIC :) ]
    Yielding control back to the event loop here (with `await`) is key.
    Giving an entire second to it to do anything it needs like handling updates, performing I/O, etc.
    
    [Messages Edit Monitor]

    - We have {msg_edit_q} that contains Message OBJ
      This messages needs to be monitored if they actually got edited

    - Every message is verified, for ex. 5 times every 1 minute, per {msg_edit_interval} and {msg_edit_max_checks}
      Means after 5 minutes message is removed

    - Message is removed if got edited (send to Signal Parser)  

    msg_obj = {
        "msg_id": XXX,
        "channel_id": YYY
        "checks_count": 0
    }
    
    '''

    while True:

        # region [Messages edit monitor]

        # See if Message Edit check time occurs

        if time.time() - msg_edit_trigger_time > msg_edit_check_interval:
            print(f'[debug]:[main_loop]: message edit check time > total messages: {len(msg_edit_monitor_list)}')
            log.debug(f'[main_loop]: message edit check time . . .')

            if len(msg_edit_monitor_list) > 0:
                temp_msg_edit_list = []

                for msg_obj in msg_edit_monitor_list:

                    # Get Channel Peer OBJ for Channel to which this message belongs by Channel ID
                    msg_check_res = await check_message_edit(tgclient, msg_obj, channels_data[msg_obj["channel_id"]]["channel_peer_obj"])

                    # Error
                    if type(msg_check_res) is str:
                        print(msg_check_res)
                        log.debug(msg_check_res)

                    # Message had been edited > forward it
                    elif msg_check_res is True:
                        print(f'[debug]:[main_loop]: message edit > forwarding edited message [{msg_obj["message_id"]}] . . .')
                        log.debug(f'[main_loop]: message edit > forwarding edited message [{msg_obj["message_id"]}] . . .')

                        # Logging

                        tmp_str = f'\n[{ad.get_str_timeprint()}]: {colored("EDITED MESSAGE EVENT:", "light_green")}\n\n' \
                                  f'=== {colored("data", "light_yellow")} {53 * "="}\n' \
                                  f'    message_id:          {msg_obj["message_id"]}\n' \
                                  f'    channel_id:          {msg_obj["channel_id"]}\n' \
                                  f'--- {colored("message", "light_blue")} {50 * "-"}\n' \
                                  f'{msg_obj["message_txt"]}\n' \
                                  f'{62 * "="}\n'

                        print(f'\n{tmp_str}')
                        log.info(f'Edited Message:\n{msg_obj}')

                        # region [Forward Edited Message]

                        await send_message(msg_obj["message_txt"], channels_data[msg_obj["channel_id"]], msg_obj)

                        # endregion

                    # Message edit check exceeds checks count > will not be kept in monitoring list
                    elif msg_obj["checks_count"] == msg_edit_max_checks:
                        print(f'[debug]:[main_loop]: message edit > message [{msg_obj["message_id"]}] exceeds max checks > removing from monitoring')
                        log.debug(f'[main_loop]: message edit > message [{msg_obj["message_id"]}] exceeds max checks > removing from monitoring')

                    # Keep message in monitoring list
                    else:
                        temp_msg_edit_list.append(msg_obj)

                msg_edit_monitor_list = temp_msg_edit_list

            msg_edit_trigger_time = time.time()

        # endregion

        # Per asyncio logic: Reserve some time to Process New TG Messages in handler {new_message_handler}
        await asyncio.sleep(1)

    # endregion


def create_tgclient(username, api_id, api_hash, chats_list: list) -> TelegramClient | str:
    """
    Init Telegram Client
    Also add new messages event handler with a list of chats id to be monitored {chats_list}

    :param username:
    :param api_id:
    :param api_hash:
    :param chats_list: list of chats id to be monitored
    :return:
    """

    tgclient = TelegramClient(username, api_id, api_hash)
    tgclient.add_event_handler(new_message_handler, events.NewMessage(chats=chats_list, incoming=True))

    try:
        tgclient.start()
    except Exception as ex:
        return f'[main]: Warning - failed to start Telegram Client. ErrMsg: {ex}'

    # print(f'\nTelegram Client authorized: {tgclient.is_user_authorized()}')
    # print(f'[main]: Telegram Client connected: {tgclient.is_connected()}\n')

    # ToDo - make sure Telegram Client is connected and authorized
    # ToDo - refactor authorization process (to be more clear + errors handler)

    if not tgclient.is_connected():
        if tgclient is not None:
            try:
                tgclient.disconnect()
            except:
                ...
        return f'[main]: Warning - telegram client not authorized or not connected'

    return tgclient


def create_channels_data(cfg: dict) -> dict | str:
    """
    Read "forward_map" KEY and check if all settings are correct
    Also add additional KEY to every Channel OBJ - see below {channels_data}

    Create final "Channels DATA OBJ" with all required data and KEYS
    Later those KEYs will be updated per needs and used for all tasks

    :param cfg: is the "telegram_cfg" dict that had been read from "TELEGRAM_CFG_FILE"
    :return: dict of "Channels DATA OBJ" with al global required KEYS / str - error string

    Note: KEY of the "channel_obj" is the "chat_id"
        In this way later we can retrieve this chat data by this KEY

    channels_data = {

        1526567406: {

            "chat_id": 1526567406,
            "chat_name": "TMMT-1",

            "forward_group_name": <"group_name" KEY>

            # This is the "forward_to" KEY from config file
            "forward_to_list": [
                { "chat_id": 1805165556, "chat_name": "TMMT-2" }
            ]

            # If need to monitor this chat for Message Edit Signal
            "is_monitor_edited": bool

            # Potential Signal Message to check against - if message contains this string - then it is a Potential Signal
            # and it will be moved to monitoring

            "monitor_edited_filter_str": "SELL GOLD SIGNAL"

            # If need to monitor this channel for edited messages - then will need to retrieve messages history from the Channel
            # in such case we need Channel Peer OBJ to be used in a telethon function called "get_messages"

            "channel_peer_obj": <OBJ>,

            # Stats

            "tot_msg_received": 0,
            "tot_msg_send": 0,
            "tot_receive_errs": 0,
            "tot_send_errs": 0,
            "tot_msg_with_replies": 0,
            "tot_msg_with_media": 0
        },

        {

        }
    }

    """

    if "forward_map" not in cfg:
        return 'Failed to read [forward_map] - the key is missing from telegram config file'

    channel_data = {}

    print('\n')

    for idx, a_group in enumerate(cfg["forward_map"], start=1):

        print('----------------------------------------------------')
        print(f'[{idx}] GROUP: {a_group["group_name"]}\n')
        log.info(f'[{idx}] GROUP: {a_group["group_name"]}\n')

        for idy, ch_from in enumerate(a_group["forward_from"], start=1):
            # Creating "channels_data" entry

            # region [Preparing some data]
            is_monitor_edited = False
            monitor_edited_filter_str = None

            if "is_monitor_edited" in ch_from and ch_from["is_monitor_edited"] is True:
                is_monitor_edited = True

                # Should contain this param as well
                if "monitor_edited_filter_str" not in ch_from:
                    return f'Warning - channel [{ch_from["chat_id"]}] setting missing the "monitor_edited_filter_str" param'

                if ch_from["monitor_edited_filter_str"] == '':
                    return f'Warning - channel [{ch_from["chat_id"]}] setting missing has unfilled "monitor_edited_filter_str" param'

                monitor_edited_filter_str = ch_from["monitor_edited_filter_str"]

            # endregion

            ch_obj_params = {
                "chat_id": ch_from["chat_id"],
                "chat_name": ch_from["chat_name"],
                "forward_group_name": a_group["group_name"],
                "forward_to_list": a_group["forward_to"],
                "is_monitor_edited": is_monitor_edited,
                "monitor_edited_filter_str": monitor_edited_filter_str,
                "channel_peer_obj": None,                               # Will be updated later
                "tot_msg_received": 0,
                "tot_msg_send": 0,
                "tot_receive_errs": 0,
                "tot_send_errs": 0,
                "tot_msg_with_replies": 0,
                "tot_msg_with_media": 0
            }

            channel_data[ch_from["chat_id"]] = ch_obj_params

            print(f'    [{idy}] MAP for chat [ {ch_from["chat_name"]} ({ch_from["chat_id"]}) ] OK')
            log.info(f'    [{idy}] MAP for chat [ {ch_from["chat_name"]} ({ch_from["chat_id"]}) ] OK')

    if len(channel_data) == 0:
        return 'Warning - no any channels maps created - check settings file'

    return channel_data


def validate_result(re_data, success_str):
    """
    Generic function to check if a "result" is of str type
    If a function executed and returned str type - means it fails and this str representing the ERROR MESSAGE
    :param re_data: is a result from a function execution
    :param success_str: message to log in case that no error
    """

    if type(re_data) is str:  # Error string
        print(re_data)
        log.exception(re_data)
        # ToDo - tier down before exit
        exit(-1)

    # If type is not str - means it success
    print(success_str)
    log.info(success_str)


if __name__ == '__main__':

    # region [ INIT ]
    # Note: some OBJ are init on top

    # region [ LOG ]
    validate_result(log, '[main]: [SESSION START] - log init OK')
    # endregion // LOG

    # region [ Telegram CFG ]
    telegram_cfg = ad.json_read_to_obj(f'{SETTINGS_DIR}/{TELEGRAM_CFG_FILE}')
    validate_result(telegram_cfg, '[main]: telegram cfg init OK')
    # endregion // Telegram CFG

    # region [ Channels Data ]
    channels_data = create_channels_data(telegram_cfg)
    print('\n')
    validate_result(channels_data, f'[main]: channels data init OK - total chats to monitor {len(channels_data)}')
    # endregion // Channels Data

    # region [ Telegram Client ]

    tgclient = create_tgclient(telegram_cfg["username"], telegram_cfg["api_id"], telegram_cfg["api_hash"], list(channels_data.keys()))
    validate_result(tgclient, '[main]: telegram client init OK')
    # endregion // Telegram Client

    # region [ Get Channels Peer OBJ ]
    # Needed for telethon get_messages function to retrieve history messages
    channels_peer_update = tgclient.loop.run_until_complete(channels_peer_update(tgclient, channels_data))
    validate_result(channels_peer_update, '[main]: channels peer obj init OK')
    # endregion // Get Channels Peer OBJ

    # endregion // INIT

    # region [ Main Loop (async) ]

    try:
        tgclient.loop.run_until_complete(
            main_loop(
                tgclient,
                channels_data,
                telegram_cfg["msg_edit_monitor_check_interval"],
                telegram_cfg["msg_edit_monitor_max_checks"]
            )
        )
    except KeyboardInterrupt:
        print(f'\n[main]: stopping . . .')
    finally:

        if tgclient is not None:
            try:
                tgclient.disconnect()
                print('[main]: telegram client disconnected OK')
            except:
                pass

            try:
                tgclient.loop.close()
                print('[main]: telegram client Loop - closed OK')
            except:
                pass

    # endregion

    print(f'\n[+] Finished!')
