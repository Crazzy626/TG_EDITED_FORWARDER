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

    # endregion // INIT
