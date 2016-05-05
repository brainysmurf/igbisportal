domain = 'igbis.edu.my'
target_groups = ["all.team", "ss.team", "es.team", 'wholeschool.parents', 'ta.team']
close_groups_str = "gam update group '{group}' who_can_post_message all_managers_can_post"
make_manager_str = "gam update group '{group}' update manager user '{user}'"
add_manager_str = "gam update group '{group}' add manager user '{user}'"
send_message_str = "gam update group '{group}' send_message_deny_notification true"
set_text_str = "gam update group '{group}' message_deny_notification_text '{text}'"
denied = "To whom it may concern: Your message has been denied as you do not have permissions. You may either use the Daily Notices to share the information it contains, or else seek a member of staff who has access to use group email. These people/positions are identified in the Communications Policy of the School. https://docs.google.com/document/d/1cFXpxc-2LJ2UEYbmMZNEUkyx1rJHUE18ZSWWrYNOY8c/edit. Thank you"

managers = [
	'anne.fowles',
	'lennox.meldrum',
	'claire.mccleod',
	'ben.hor',
	'wayne.demnar',
	'munchiew.looi',
	'usha.ranikrishnan',
	'rubavathy.bojan'
]
additions = {
	'all.team': [
		'kathy.mckenzie'
		],
}

for group in target_groups:
	print(close_groups_str.format(group=group))
	print(send_message_str.format(group=group))
	print(set_text_str.format(group=group, text=denied))

print('batch-commit')

for group in target_groups:
	for manager in managers:
		# Make sure they are in the group as a manager, either by adding or updating
		# Don't need to pause with batch-commit
		print(add_manager_str.format(group=group, user=manager))
		print(make_manager_str.format(group=group, user=manager))
	if group in list(additions.keys()):
		for manager in additions[group]:
			print(make_manager_str.format(group=group, user=manager))