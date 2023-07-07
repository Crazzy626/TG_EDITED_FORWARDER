import asyncio
import logging
import time
from queue import Queue
from datetime import datetime
from telethon import TelegramClient, events
from telethon import functions
from telethon.tl.functions.messages import GetHistoryRequest, GetDialogsRequest
from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerEmpty
from termcolor import colored


# region [ INIT; FUNCTIONS ]


def get_str_timeprint():
    """
    Suitable only for console/log print
    Not suitable for filenames (since contains ':' '/' symbol)
    :return:
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def init_log(log_file_name, log_path, log_alias) -> logging.Logger | None:
    try:
        _log = logging.getLogger(log_alias)
        _log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(f'{log_path}/{log_file_name}', encoding='utf-8')
        formatter = logging.Formatter('[%(asctime)s : %(levelname)s : %(name)s ]:  %(message)s')
        file_handler.setFormatter(formatter)
        _log.addHandler(file_handler)
        return _log
    except Exception as e:
        print(f'[Exception]: Can not create log. ErrMsg: {e}')
        return None


log = init_log("log.log", ".", "main")
if log is None:
    print('[!] Failed to init log')
    exit(0)

log.info('START')

# endregion


# region [ CREDENTIALS; From-To MAp ]

# ALEX TEST --------------------------------------------------------------
# ALEX_TEST_CHANNEL: -1001850783314

api_id = 10652401
api_hash = "13cc03d844ec7cf75d20ed0bee7a687b"
name = 'Alex2'

# Channels to Monitor and Forward

forwards_map = [
    {
        "from": (
            (1526567406, "TMMT-1"),
        ),

        "to": (1805165556, "TMMT-2")
    }
]

# Collect only Chats_ID to be monitored - used in
chats_set = []

# Statistics for every monitored Channel
stats_data = {}

# For monitored Channels - need to get the Peer OBJ, in order to be able to read later message history
# Using dict for this - where KEY is the channel ID and value is the Peer OBJ

'''
channels_peer = {
    1526567406: {
        "name": "TMMT-1",
        "peerOBJ": <peer_object_for_this_channel>
    }
}
'''

channels_peer = {}

# Queue to hold messages to monitor for edit
msg_edit_q = Queue()
msg_edit_list = []
msg_edit_check_interval = 20
msg_edit_max_checks = 3

# TG Client OBJ
tgclient = TelegramClient(name, api_id, api_hash)


async def update_channels_peer_data() -> bool:
    """
    Update data for {channels_peer} dict
    Main aim is to update {peerOBJ} KEY for the monitored channels
    Using {GetDialogsRequest} method to retrieve ALL User's dialogs and search for the Target Channles there
    Returned OBJ will have "peer" OBJ that will be stored in {channels_peer} dict for this Channel
    :return:
    """

    # Get User Dialogs

    get_dialogs = GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=100,
        hash=0
    )

    try:
        dialogs = await tgclient(get_dialogs)
    except Exception as ex:
        print(f'[!] Exception on "GetDialogsRequest". ErrMsg: {ex}')
        log.exception(f'Exception on "GetDialogsRequest". ErrMsg: {ex}')
        return False

    # Find needed Channels - retrieve Peer OBJ

    for ch_key, ch_val in channels_peer.items():
        for dlg in dialogs.dialogs:
            if dlg.peer.channel_id == ch_key:
                ch_val["peerOBJ"] = dlg.peer
                break

    # Verify if all Channels are updated with peer OBJ ("peerOBJ" KEY)

    for ch_key, ch_val in channels_peer.items():
        if channels_peer[ch_key]["peerOBJ"] is None:
            print(f'[!] Warning - Peer OBJ not found for Channel [{channels_peer[ch_key]["name"]}]')
            log.warning(f'[!] Warning - Peer OBJ not found for Channel [{channels_peer[ch_key]["name"]}]')
            return False

    return True


async def new_message_handler(event):
    """
    Handler for TG Client to catch new Messages
    :param event:
    :return:
    """
    # region [ EVENT DECODE ]

    # [Chat OBJ and Message OBJ]
    message_txt = ''
    try:
        message_obj = event.message
        channel_id = message_obj.peer_id.channel_id
        message_txt = message_obj.message
        message_id = message_obj.id
        # Media Type: Will be OBJ: MessageMediaPhoto(photo=Photo(id=5440445674278731901 . . .
        is_media_type = False
        message_media = message_obj.media
        if message_media is not None:
            is_media_type = True
        message_reply_id = None
        if message_obj.reply_to is not None:
            message_reply_id = message_obj.reply_to.reply_to_msg_id
    except Exception as ex:
        print(f'[!] Exception - while decoding Message Event. ErrMsg: {ex}')
        log.exception(f'Exception - while decoding Message Event. ErrMsg: {ex}')
        return

    # [Logging]

    tmp_str = f'\n[{get_str_timeprint()}]: {colored("NEW MESSAGE EVENT:", "light_green")}\n\n' \
              f'=== {colored("data", "light_yellow")} {53 * "="}\n' \
              f'    message_id:          {message_id}\n' \
              f'    channel_id:          {channel_id}\n' \
              f'    message_reply_id:    {message_reply_id}\n' \
              f'    message_media:       {is_media_type}\n' \
              f'--- {colored("message", "light_blue")} {50 * "-"}\n' \
              f'{message_txt}\n' \
              f'{62 * "="}\n'

    print(f'\n{tmp_str}')
    # To file log write FULL EVENT + DECODED
    log.info(f'Message Event Decoded:\n{tmp_str}\nMessage Event OBJ:\n{message_obj}')

    # endregion

    # region [ Message Edit Monitoring ]

    # Identify if message is a potential Signal

    if message_txt.startswith("GOLD"):
        print(f'[edit_monitoring]: Message [{message_id}] = potential Signal, added to edit monitor queue')
        msg_edit_list.append({
            "msg_id": message_id,
            "checks_count": 0,
            "channel_id": channel_id
        })

    '''
    - Put message OBJ into "Message Edit Monitor" Threaded Queue for EDIT MONITORING: (message_id, message_text)
    - Every X minutes - check if message got EDITED: by comparing the Message Text
      ToDo - compare by HASH instead by TEXT
    - Actual compare: Message OBJ has "edit_date=None" KEY- check using it  
      After edit this KEY will be:
      edit_date=datetime.datetime(2023, 7, 5, 11, 55, 46, tzinfo=datetime.timezone.utc)
    - If Message Edited > Check if SIGNAL > Forward as usual  
      ToDo - use "Message Forwarder" Threaded Queue  
        
        
    Message(
        id=6806, 
        peer_id=PeerChannel(channel_id=1526567406), 
        date=datetime.datetime(2023, 7, 5, 11, 53, 9, tzinfo=datetime.timezone.utc), 
        message='AAA_EDIT_1', 
        out=False, 
        mentioned=False, 
        media_unread=False, 
        silent=False, 
        post=True, 
        from_scheduled=False, 
        legacy=False, edit_hide=False, pinned=False, noforwards=False, from_id=None, fwd_from=None, via_bot_id=None, 
        reply_to=None, media=None, reply_markup=None, entities=[], views=1, forwards=0, replies=None, 
        edit_date=datetime.datetime(2023, 7, 5, 11, 55, 46, tzinfo=datetime.timezone.utc), 
        post_author=None, grouped_id=None, reactions=None, restriction_reason=[], ttl_period=None
    )
          
    Get Messages Variants
    
    [Get Messages - V1]

    result = await tgclient(GetHistoryRequest(
        peer=ch_peer,
        limit=10,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0))

    [Get Messages - V2] for Groups only ???
    result = await tgclient(functions.channels.GetMessagesRequest(id=message_id))
          
    '''
    #
    # sleep_time = 10
    # last_edited = None
    #
    # for count in range(3):
    #
    #     print(f'[edit_monitoring]: Sleeping [{sleep_time} s.] before history check message [{message_id}]. . .')
    #     await asyncio.sleep(sleep_time)
    #
    #     # Retrieve message by ID using Per OBJ of this channel
    #     # Get Peer OBJ for this channel from {channels_peer} where KEY is Channel ID
    #
    #     msg_data = await tgclient.get_messages(channels_peer[channel_id]["peerOBJ"], limit=1, ids=message_id)
    #
    #     # [Message Edited]
    #     # Verify by {edit_date} KEY
    #
    #     is_edited = False
    #     if msg_data.edit_date != last_edited:
    #         last_edited = msg_data.edit_date
    #         is_edited = True
    #
    #     print(f'[edit_monitoring]: Message [{message_id}] > Edited: {is_edited} [{last_edited}] ({count + 1})')

    # endregion

    # region [Forward Map From-To]

    # try:
    #     # await tgclient.send_message(target_map_obj[0], message=forward_txt)
    #     # Note: {file} param will be None - if no media detected.
    #     # If media - detected - then "MessageMediaPhoto" OBJ will be sent from (message_media = MessageMediaPhoto(photo=Photo(id=5440445674278731901 . . .)
    #     await tgclient.send_message(forward_to[0], file=message_media, message=message_txt)
    #     print(f'[+] Message sent OK\n')
    # except Exception as ex:
    #     print(f'[!] Exception - while sending message. ErrMsg: {ex}')
    #     log.exception(f'Exception - while sending message. ErrMsg: {ex}')

    # endregion


async def main_loop():
    global msg_edit_list
    msg_edit_trigger_time = 0  # To know if time comes for edited messages check

    # region [Channels Per OBJ]

    print(f'[+] Creating Channels Peer data . . .')
    log.info(f'Creating Channels Peer data . . .')

    peer_upd_proc = await update_channels_peer_data()

    if peer_upd_proc is False:
        return False

    print(f'[+] Channels Peer data retrieved successfully.')
    log.info(f'Channels Peer data retrieved successfully.')

    # endregion

    # region [ Main Infinite Loop ]

    '''
    [ ASYNCIO MAGIC :) ]
    Yielding control back to the event loop here (with `await`) is key.
    Giving an entire second to it to do anything it needs like handling updates, performing I/O, etc.
    '''

    while True:

        # region [Messages edit monitor]
        '''
        [Logic]
        
        - We have {msg_edit_q} that contains Message OBJ
          This messages needs to be monitored if they actually got edited
        
        - Every message is verified 5 times every 1 minute, per {msg_edit_interval} and {msg_edit_max_checks}
          Means after 5 minutes message is removed
        
        - Message is removed if got edited (send to Signal Parser)  
        
        Message OBJ = {
            "msg_id": XXX,
            "channel_id": YYY
            "checks_count": 0,
        }
        
        '''

        # See if Message Edit check time occurs

        if time.time() - msg_edit_trigger_time > msg_edit_check_interval:
            if len(msg_edit_list) > 0:
                print(f'[main_loop]: Message edit: check trigger > total messages: {len(msg_edit_list)}')

                temp_msg_edit_list = []

                for msg_obj in msg_edit_list:
                    if await check_message_edit(msg_obj) is True:
                        # Send to Signal Parser > Message will not be kept in monitoring list
                        print(f'[main_loop]: Message edit > edited message [{msg_obj["msg_id"]}] > send to Signal Parser . . .')
                    elif msg_obj["checks_count"] == msg_edit_max_checks:
                        # Message checks count exceed number of checks > will not be kept in monitoring list
                        print(f'[main_loop]: Message edit > message [{msg_obj["msg_id"]}] exceeds max checks > removing from monitoring')
                    else:
                        # Keep message in monitoring list
                        temp_msg_edit_list.append(msg_obj)

                msg_edit_list = temp_msg_edit_list
                print(f'[main_loop]: Message edit: total messages left: {len(msg_edit_list)}')
            msg_edit_trigger_time = time.time()

        # endregion

        # Per asyncio logic: Reserve some time to Process New TG Messages in handler {new_message_handler}
        await asyncio.sleep(1)

    # endregion


async def check_message_edit(msg_obj) -> bool:
    """
    Message OBJ = {
        "msg_id": XXX,
        "channel_id": YYY
        "checks_count": 0,
    }
    :param msg_obj:
    :return:
    """
    # Retrieve message by ID using Per OBJ of this channel

    msg_data = await tgclient.get_messages(channels_peer[msg_obj["channel_id"]]["peerOBJ"], limit=1, ids=msg_obj['msg_id'])

    # [Message Edited]
    # Verify by {edit_date} KEY

    if msg_data.edit_date is not None:          # If message was not edited - it will be None
        last_edited = msg_data.edit_date
        print(f'[debug]:[edit_monitoring]: Message [{msg_obj["msg_id"]}] > Edited: [{last_edited}]  |  checks_count = {msg_obj["checks_count"]}')
        return True
    else:
        msg_obj["checks_count"] += 1
        return False


if __name__ == '__main__':

    # region [ Chats Forward Map; Stats Data ] > Chats to monitor: From-To

    for a_map in forwards_map:
        print('\n----------------------------------------------------')
        print(f'Analyzing Chats . . .')
        for map_from in a_map["from"]:
            # Create stats data entry for this channel
            stats_data[map_from[0]] = {
                "channel_title": map_from[1],
                "tot_msg_received": 0,
                "tot_msg_send": 0,
                "tot_receive_errs": 0,
                "tot_send_errs": 0,
                "tot_msg_with_replies": 0,
                "tot_msg_with_media": 0
            }

            # Add chat_id to monitor/filter list
            chats_set.append(map_from[0])
            print(f'    {map_from[1]} ({map_from[0]})')

            # Create "peer" entry
            channels_peer[map_from[0]] = {
                "name": map_from[1],
                "peerOBJ": None  # To be updated later in {update_channels_peer_data()}
            }

        # Target chats
        print(f'Target Chats:')
        print(f'    {a_map["to"][1]} ({a_map["to"][0]})')

    if len(chats_set) == 0:
        print('Warning - no any chats filtered to monitor')
        log.warning('Warning - no any chats filtered to monitor')
        exit(-1)

    print(f'\n[+] Total chats to monitor: {len(chats_set)}')
    log.info(f'Total chats to monitor: {len(chats_set)}')

    # endregion

    # region [ INIT TG ]

    tgclient.add_event_handler(new_message_handler, events.NewMessage(chats=chats_set, incoming=True))
    tgclient.start()

    if tgclient is None:
        print(f'\n[!] Warning - Telegram Client is None')
        log.warning(f'Warning - Telegram Client is None')
        exit(-1)

    # print(f'\nTelegram Client authorized: {tgclient.is_user_authorized()}')
    # log.info(f'\nTelegram Client authorized: {tgclient.is_user_authorized()}')
    print(f'[+] Telegram Client connected: {tgclient.is_connected()}\n')
    log.info(f'Telegram Client connected: {tgclient.is_connected()}\n')

    if not tgclient.is_connected():
        print(f'\n[!] Warning - Telegram Client not authorized or not connected')
        log.warning(f'\n[!] Warning - Telegram Client not authorized or not connected')

        if tgclient is not None:
            try:
                tgclient.disconnect()
            except:
                ...

        exit(-1)

    print(f'[+] Telegram Client OK\n')
    log.info(f'Telegram Client OK')

    # endregion

    # region [ Main Loop ]

    try:
        tgclient.loop.run_until_complete(main_loop())
    except KeyboardInterrupt:
        print(f'\n[+] Stopping . . .')
    finally:
        if tgclient is not None:
            try:
                tgclient.disconnect()
                print('[+] Client - disconnected OK')
            except:
                pass

            try:
                tgclient.loop.close()
                print('[+] Client Loop - closed OK')
            except:
                pass

    # endregion

    print(f'\n[+] Finished!')
