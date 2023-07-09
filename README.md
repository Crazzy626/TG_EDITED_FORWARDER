# Telegram Messages Forwarder

Monitor Telegram Channel messages and forward them to other channel in real-time.

Main features:

	- forward message right away when it appears in a Channel
 
	- multiple lists of Channel sources and targets
 
  	- monitor message for edit event and forward it only after it had been edited

# [DOC]

## [Settings]:
	Configure settings /settings/telegram_config.json

**Telegram settings:** 
	get from your Telegram account (see telegram api docs) 
   	"username" / "api_id" / "api_hash"

**Messages forward rules:** are set within "forward_map"

	Every entry is a Froward Group - indicate from which Channels to forward messages to which Channels
   
	"group_name" - any name for the group
	"forward_from" - list of Channels from which need to forward messages. Every entry is a set of parameters for this channel
	"chat_id" - Channel ID as it on Telegram
	"chat_name" - Channel Name as it on Telegram
	"is_monitor_edited" - true if messages form this Channel needs to be monitored for edit event 
	"monitor_edited_filter_str" - filter string applied before message is placed in momnitoring list

	Note: see [Message Edit Monitor] section
			
	"forward_to" - list of Channels where need to forward messages

 **Message Edited Monitor**

 	Allows to monitor messages from the history for "edit" event.
  	Example: an "initial message" is posted in the Channel and need to monitor if it will be edited somewhere in the future.
   	"is_monitor_edited" setting allows to indicate in which Channel to use this feature.
    	"monitor_edited_filter_str" allows to filter "initial message" by indicated string pattern in order to decide if it will be monitored or treated as simple message (non monitored)
     	This is for the case if there is no need to mintor all messages, but only specific message sthat initially has a pattern.

     	Example: A Telegram Channel where trading signals are posted. But initial Signal message has no full content.
      	First, only initial Signal message is posted and after 2-3 minutes the message is edited and filled with full Signal data.

 	First, initial message is issued in a Channel
      	-----------------
	BUY GOLD SIGNAL
 	-----------------

	After 2-3 minutes message is edited and content changed to 

 	-----------------
	SELL GOLD SIGNAL

  	Entry: 1.5
   	SL: 1.4
    	TP: 1.6
  	-----------------

   	To 

 	"msg_edit_monitor_check_interval" - interval in seconds, between message edit check 
	"msg_edit_monitor_max_checks" - maximum number of checks, after which monitored message will be removed from message edit monitring list

 

3. log.txt will be created under /logs

## [Running]

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

