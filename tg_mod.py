import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
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

forwards_map = [
    {
        "from": (
            (1526567406, "TMMT-1"),
        ),

        "to": (1805165556, "TMMT-2")
    }
]

# FLORIAN LIVE -----------------------------------------------------------

# api_id = 21569205
# api_hash = "c3eb528e5b41a39dcf24512df627ee4e"
# name = 'Trading_Signals'
#
# forwards_map = [
#     {
#         "from": (
#             (1436688109, "Easy Pips VIP"),
#             (1465493909, "FxPremiere.com VIP"),
#             (1758700941, "Forex Signals")
#         ),
#         "to": (1616235936, "GS Forex")
#     },
#     {
#         "from": (
#             (1146640365, "Gold Forcaster (paid) - Elite"),
#             (1710836950, "GOLD Snipers VIP"),
#             (1701667638, "Clarity Forex Signals | GBPJPY & GOLD | MambaFX")
#         ),
#         "to": (1650002523, "GS Gold")
#     },
#     {
#         "from": (
#             (1520291354, "Crypto Chiefs - Premium"),
#         ),
#         "to": (1861897887, "GS Crypto")
#     }
# ]


# endregion

# Collect stats data during run

'''
1. How many messages captured form every Source Channel
2. How many messages sent to every Target Channel - success and fail

Stats data is a list of dict OBJ.
Every ITEM  -  is a Source channel - identified by {source_channel_id} KEY - while VALUE os dict of some data

@stats_data = 
{
    source_channel_id: {
        "channel_title": str,
        "tot_msg_received": int,
        "tot_msg_send": int,
        "tot_receive_errs": int,
        "tot_send_errs": int,
        "tot_msg_with_replies": int,
        "tot_msg_with_media": int,
    } 
}

'''

stats_data = {}

chats_set = []

tgclient = TelegramClient(name, api_id, api_hash)


class MessageEditThread(Thread):
    """
    Verify if
    """
    Thread.daemon = True
    def __init__(self, mods_cfg: dict):
        super(ParserThread, self).__init__()
        self.qqin = queue.Queue()           # tuple({sender_id}, {sender_title}, {message_str}, {message_id})
        self.stop_flag = False
        # Important!!!
        # This queue will be 'mapped' to MT5Thread {signals_qq} queue - from where it will create positions
        # Map will be performed by Main upon threads creation

        # Queue Item:
        # signalobj = {'pair_name': 'usdcad', 'symbol_id': None, 'trade_type': 'buy', 'tp_list': ['1.3340'], 'sl': 1.33}

        self.mt5_out_queue = None       # Send {signalobj} to MT5Thread Queue
        self.ctrade_out_queue = None    # Send {signalobj} to CTradeThread Queue

        self.mods_cfg = mods_cfg    # MT5/CTrade modules - to know if need to send Position create

    def run(self):
        log.info('[ParserThread]: Start . . .')
        print('[ParserThread]: Start . . .')

        '''
        Processing messages one by one - bit can use Thread Pool as well or at least async
        '''
        # ToDo - parse message sin ThreadPool or Async

        while self.stop_flag is False:
            try:
                self.tg_msg_parse_processor(self.qqin.get_nowait())
            except queue.Empty:
                continue


async def new_message_handler(event):
    """
    Receive-Send Telegram Message

    Types of messages:
        - "Simple Type" - when message is not a reply
        - "Reply Type"  - when message is a reply to other message
        - "Media Type"  - image


    [MESSAGE]
    Message(id=193, peer_id=PeerChannel(channel_id=1526567406)

    [ MEDIA ]
    MessageMediaPhoto(photo=Photo(id=5440445674278731901, access_hash=-1957852620330627719, file_reference=b'\x02Z\xfd\x91\xee\x00\x00\x00\xc8c\xef\xff\xf2p\xb8A\x82\xcc\x83\xddd?~\xf6b\xfe3\xbe\xde', date=datetime.datetime(2023, 2, 17, 22, 30, 10, tzinfo=datetime.timezone.utc), sizes=[PhotoStrippedSize(type='i', bytes=b'\x01\x16(\xa3\xf6\x8c\x7f\x00\xa7\x9b\xd2\x7f\xe5\x92\xd0\x02\x18\xce\xe1\xcf\x1c\xd2\xc4\x91\xf9\x84H\x06\x01"\x8d\x10\xdboq>\xd9\x9c~\xe9j8\x9c\xa9#\x83\xdf\x91\x9a\x96s\x1ae\x02\x8c\x8e\xe2\xa1\x88\xa6~r@\xf6\xa1\x04\x95\xb6\x15\xe4/\xd4\xfeB\x8aG\xd9\x91\xb0\x93\xc5\x14\xc9\'\xf3\x90\xc5\xb4\xa9\xcf\x00\x9aS,\x04\x8e\x1f\x03\x9e\x82\x8a)u\x19^r$\x99\xd9s\x82s\xcdG\xb6\x8a)\x88UZ(\xa2\x80?'), PhotoSize(type='m', w=320, h=174, size=16900), PhotoSizeProgressive(type='x', w=413, h=225, sizes=[1885, 5725, 11325, 15978, 24989])], dc_id=2, has_stickers=False, video_sizes=[]), ttl_seconds=None)

    [ REPLY ]
     MessageReplyHeader(reply_to_msg_id=197, reply_to_scheduled=False, reply_to_peer_id=None, reply_to_top_id=None)
    """

    # tmp_str = f'\n[{get_str_timeprint()}]: NEW MESSAGE EVENT . . .\n' \
    #           f'{20 * "-"}\n' \
    #           f'{event.raw_text}\n' \
    #           f'{20 * "-"}\n'
    #
    # print(tmp_str)
    # log.info(tmp_str)

    # region [ EVENT DECODE ]

    # [Chat OBJ and Message OBJ]

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

    tmp_str = f'\n[{get_str_timeprint()}]: {colored("NEW MESSAGE EVENT:" , "light_green")}\n\n' \
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

    # region [Message Forward]

    forward_txt = message_txt

    # [Message ReplyType]
    # If this actual message is a Reply to other message > retrieve "Replied Message" {replied_message}
    # Need to get "Chat Entity" - in order to retrieve "replied" message.
    # Note: if need to get Chat Entity by Chat ID > await event.client.get_entity(chat_id)
    # In our case - it is same chat (in this event) so can get chat entity > {await event.get_chat()}

    if message_reply_id is not None:

        print(f'[+] Message [ReplyType] detected: this message: [{message_id}] ---> replied to: [{message_reply_id}]')
        log.info(f'Message [ReplyType] detected: this message: [{message_id}] ---> replied to: [{message_reply_id}]')

        # [Chat Entity]

        chat_entity = None

        try:
            chat_entity = await event.get_chat()
            log.info(f'Message [ReplyType]: "replied_message" Chat Entity retrieved success:\n{chat_entity}')
        except Exception as ex:
            print(f'[!] Exception - while getting "replied_message" Chat Entity. ErrMsg: {ex}')
            log.exception(f'Exception - while getting "replied_message" Chat Entity. ErrMsg: {ex}')

        # [Replied Message]

        # Retrieve Message OBJ by message by ID > Message(id=193, ... message='a', ...
        replied_message = None

        if chat_entity is not None:
            try:
                replied_message = await tgclient.get_messages(chat_entity, ids=message_reply_id)
                log.info(f'Message [ReplyType]: "replied_message" Message OBJ retrieved success:\n{replied_message}')
            except Exception as ex:
                print(f'[!] Exception - while getting "replied_message" Message OBJ. ErrMsg: {ex}')
                log.exception(f'Exception - while getting "replied_message"  Message OBJ. ErrMsg: {ex}')

        # If {replied_message} could not be retrieved - log Warning and only "actual" message will be forwarded

        if replied_message is None:
            print(f'[!] Warning - "replied_message" Message OBJ could not be retrieved - only "actual" message will be forwarded')
            log.warning(f'[!] Warning - "replied_message" Message OBJ could not be retrieved - only "actual" message will be forwarded')
        else:
            # Log "replied_message" text
            print(f'--- replied message {50 * "-"}\n' 
                  f'{replied_message.message}\n'
                  f'{70 * "-"}\n')

            # Forward TXT
            forward_txt = f'{replied_message.message}\n{20 * "-"}\n{message_txt}'

    # endregion

    # region [Forward Map From-To]

    # Find MAP for this Channel (channel of this event we are in) and Forward "actual" message or
    # "actual" + "replied_message" > according to all above processing

    target_map_obj = None   # Will be tuple(chat_id, chat_name)
    source_map_obj = None

    for _map in forwards_map:
        if target_map_obj != None:
            break
        for a_from in _map["from"]:
            if channel_id == a_from[0]:
                source_map_obj = a_from
                target_map_obj = _map["to"]
                break

    # endregion

    # region [Send Message]

    print(f'[+] Sending Message . . .\n'
          f'    FROM: {source_map_obj[1]} ({source_map_obj[0]})\n'
          f'    TO:   {target_map_obj[1]} ({target_map_obj[0]})\n')

    # Add message header
    forward_txt = f'@@@{source_map_obj[0]} ({source_map_obj[1]})\n{forward_txt}'

    try:
        # await tgclient.send_message(target_map_obj[0], message=forward_txt)
        # Note: {file} param will be None - if no media detected.
        # If media - detected - then "MessageMediaPhoto" OBJ will be sent from (message_media = MessageMediaPhoto(photo=Photo(id=5440445674278731901 . . .)
        await tgclient.send_message(target_map_obj[0], file=message_media, message=forward_txt)
        print(f'[+] Message sent OK\n')
    except Exception as ex:
        print(f'[!] Exception - while sending message. ErrMsg: {ex}')
        log.exception(f'Exception - while sending message. ErrMsg: {ex}')

    # endregion


async def main_loop():

    # [print(itm) for itm in stats_data]
    print(stats_data)

    while True:

        # DO MORE STUFF HERE

        # [STATS] > Show some stats every X minutes

        # [ ASYNCIO MAGIC :) ]

        # IMPORTANT:
        # Yielding control back to the event loop here (with `await`) is key.
        # Giving an entire second to it to do anything it needs like handling updates, performing I/O, etc.
        await asyncio.sleep(1)


if __name__ == '__main__':

    # region [ Chats Forward Map; Stats Data ] > Chats to monitor: From-To

    for a_map in forwards_map:
        print('\n----------------------------------------------------')
        print(f'Source Chats:')
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

            chats_set.append(map_from[0])  # add chat_id to monitor/filter
            print(f'    {map_from[1]} ({map_from[0]})')

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

    # region [ Telegram Client INIT ]

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

    # tgclient.run_until_disconnected()

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

    print(f'\n[+] Finished!')
