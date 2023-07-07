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

import addons as ad
from __init__ import LOG_FOLDER, SETTINGS_DIR, TELEGRAM_CFG_FILE


# [LOG Init]
log = ad.init_log(f'main.log', LOG_FOLDER, "main")


def main():
    pass


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

    channel_data_obj = {}

    print('\n')

    for idx, a_group in enumerate(cfg["forward_map"], start=1):

        print('\n----------------------------------------------------')
        print(f'[{idx}] GROUP: {a_group["group_name"]}\n')

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

            channel_data_obj[ch_from["chat_id"]] = ch_obj_params

            print(f'    [{idy}] MAP for chat [ {ch_from["chat_name"]} ({ch_from["chat_id"]}) ] OK')
    #
    #
    # print(f'\n[+] Total chats to monitor: {len(chats_set)}')
    # log.info(f'Total chats to monitor: {len(chats_set)}')


if __name__ == '__main__':

    # region [ INIT ]
    # Note: some OBJ are init on top

    # region [ LOG ]

    if type(log) is str:  # Error string
        print(log)
        exit(-1)
    log.info('[main]: log init OK')

    # endregion // LOG

    # region [ Telegram CFG ]

    telegram_cfg = ad.json_read_to_obj(f'{SETTINGS_DIR}/{TELEGRAM_CFG_FILE}')
    if type(telegram_cfg) is str:   # Error string
        print(telegram_cfg)
        log.exception(telegram_cfg)
        exit(-1)
    log.info('[main]: telegram cfg init OK')

    # endregion // Telegram CFG

    # region [ Channels Data ]

    channels_data = create_channels_data(telegram_cfg)
    if type(channels_data) is str:   # Error string
        print(channels_data)
        log.warning(channels_data)
        exit(-1)
    log.info('[main]: channels data init OK')

    # endregion // Forward Map

    # endregion // INIT
