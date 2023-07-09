# Telegram Messages Forwarder

# [DOC]

1. Configure settings on /settings/telegram_config.json
2. log.txt will be created under /logs

![1](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/4a40a1ce-112b-44a1-b7e4-a67faa97dd8b)
![2](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/da5d6c46-146f-4f43-bd0b-9f5aff739082)
![3](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/af28ff47-6ee0-44a9-a687-df67d94c849b)

# [Version 2.0:]

    [08.07.2023] Added possibility to monitor "Edited Messages"

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

# [Version 1.0:]

- Monitor multiple Telegram Channel messages and forward messages to multiple channels

