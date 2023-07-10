# Telegram Messages Forwarder

Monitor Telegram Channel messages and forward them to other channel in real-time.

# [MAIN FEATURES]:

	- forward message right away when it appears in a Channel
 
	- monitor multiple lists of Channel and forward messages to multiple target Channels
 
  	- monitor message for edit event and forward it only after it had been edited

   	- filter edit monitored message by a pattern, before placing to edit monitoring list

# [DOC]

## [SETUP & RUN]:

	1. CD to destination folder:
	cmd:	cd home/<user>/my_app

	2. Clone repo (using Personal Acess Token):
	cmd:	git clone https://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@github.com/Crazzy626/TG_EDITED_FORWARDER.git

	* TG_EDITED_FORWARDER folder will be created inside my_app folder and project downloaded
	
	2. Configure settings /settings/telegram_config.json:

	3. Run: access TG_EDITED_FORWARDER folder where main.py is located
	cmd:	python3.10 main.py

	4. Check terminal and log.log for output

## [UPDATE]:
	
	cmd:	git pull origin master

## [Settings]:

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
	"monitor_edited_filter_str" - filter string applied before message is placed in momnitoring list. If message contains this string - it will be placed in edit monitor.
	"msg_edit_monitor_check_interval" - interval in seconds, between message edit check 
	"msg_edit_monitor_max_checks" - maximum number of checks, after which monitored message will be removed from message edit monitring list
	  
	Note: see [Message Edit Monitor] section
			
	"forward_to" - list of Channels where need to forward messages

 **Message Edite Monitor**

 	Allows to monitor messages from the history for "edit" event.
  	Example: an "initial message" is posted in the Channel and need to monitor if it will be edited sometime in the future.
   	"is_monitor_edited" setting allows to indicate in which Channel to use this feature.
	"monitor_edited_filter_str" allows to filter "initial message" by indicated string pattern in order to decide if it will be monitored or treated as simple message (non monitored)
	This is for the case if there is no need to mintor all messages, but only specific message sthat initially has a pattern.

[Use-case example]: 

	A Telegram Channel where Trading Signals are posted. 
 	But initial Signal message has no full content - it edited after 2-3 minutes and filled with full Signal data.
	There is no need to forward such initial message - cause it has no full content yet - need to wait untill it get edited and full Signal content is added, only after that to forward it.       

 	First, Initial Signal message is posted in a Channel:
      	-----------------
	BUY GOLD SIGNAL
 	-----------------

	After 2-3 minutes message is edited and content changed to: 

 	-----------------
	SELL GOLD SIGNAL

  	Entry: 1.5
   	SL: 1.4
	TP: 1.6
  	-----------------

   	In order to get the edit event - need to place such message sin "edit monitoring list"
	For that, first need to configure settings for this channel and set the "is_monitor_edited" KEY to true.
	Also need to configure "monitor_edited_filter_str" setting with a string pattern in this case string pattern is "GOLD SIGNAL", since inital posted message always contains this string.
	Any other messages that has no such strig - will not be monitored, but forwarded right away like any other message.

	Upon initial Signal message post, "monitor_edited_filter_str" will match and this message will be placed in edit monitoring list.
 	Every X seconds, per "msg_edit_monitor_check_interval" setting, message will be retrieved from Channel history and verified if it had been edited.
  	If message got edited - it will be forwarded.
   	Maximum number of such checks is determined by "msg_edit_monitor_max_checks" settings.
	If after this number of checks the mssage had not been edited - it will be removed from edit monitoring list.
	

## [Running]

![1](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/4a40a1ce-112b-44a1-b7e4-a67faa97dd8b)
![2](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/da5d6c46-146f-4f43-bd0b-9f5aff739082)
![3](https://github.com/Crazzy626/TG_EDITED_FORWARDER/assets/70648978/af28ff47-6ee0-44a9-a687-df67d94c849b)

# [Version 2.0:]

    [08.07.2023] Added possibility to monitor "Edited Messages"
	
# [Version 1.0:]

	Monitor multiple Telegram Channels messages and forward messages to multiple channels

