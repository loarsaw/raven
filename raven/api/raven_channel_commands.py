import frappe
from raven.api.raven_channel import get_peer_user

@frappe.whitelist()
def get_commands(channel_id:str):
	all_commands = {}
	is_dm = is_dm_to_bot(channel_id=channel_id)
	if is_dm:
			peer_user = get_peer_user(channel_id=channel_id , is_direct_message=is_dm)
			bot = frappe.get_doc("Raven Bot" , peer_user.user_id)
			commands = []
			dm_allowed = bot.allow_dm
			if dm_allowed:
				for row in bot.command_table:
					commands.append({
						"command_name":row.command_name,
						"command_description":row.command_description,
						"command_script":row.command_script

					})

				all_commands[peer_user.user_id] = commands

	else:
		# Lets assume there are mutiple bots installed and each bot in his/her/** command list has got multiple commands
		# will be listed through out the channel in which they are conjured up.  
		# need to remove or atleast verify List
		installed_bots = get_installed_bots(channel_id=channel_id)

		if not installed_bots:
			return None
		for bot_name in installed_bots:

			bot = frappe.get_doc("Raven Bot" , bot_name)
			commands = []
			if bot.allow_group_mention:
				for row in bot.command_table:
					commands.append({
						"command_name":row.command_name,
						"command_description":row.command_description,
					})

				all_commands[bot_name] = commands
	
	return all_commands

@frappe.whitelist()
def is_dm_to_bot(channel_id:str):
	try:
		channel = frappe.get_doc("Raven Channel" , channel_id)
		return channel.is_direct_message
	except frappe.DoesNotExistError:
		frappe.throw(f"Raven Channel with ID {channel_id} not found")



def get_installed_bots(channel_id):
	cache_key = f"install_bot_{channel_id}"
	# There are only two hard things in Computer Science Cache Invalidation and Naming Things ~ Some Important Guy
	# Perhaps lets throw these into shredder with a button on ui otherwise Underperfoming Cron JOB (TTL) is to cache invalidation what wrapper is to Linux Kernal Devs. 
	cached_bots = frappe.cache.get_value(cache_key)
	if cached_bots:
		return cached_bots
	raven_channel = frappe.get_doc("Raven Channel" , channel_id)
	installed_bots_table = raven_channel.bots_table
	bots = []
	if installed_bots_table:
		for bot in installed_bots_table:
			bots.append(bot.bot_name)
	else:
		# "No Bots" found try some MMORPG even players seems to be bots there
		bots = None
	if bots:
		frappe.cache.set_value(cache_key , bots)

	return bots
