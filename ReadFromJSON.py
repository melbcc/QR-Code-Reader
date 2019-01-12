#!/usr/bin/env python3

import json

with open('melbpc-members3.json', 'r') as file:
	members =  json.load(file)
	#print("Member count:", members['count'])
	#print(members)
	memberCount = members['count']
	members = members['values']
	#more = members['values']

for member in members.values():
	exp_date = None
	status_id = None
	values = member.get('api_Membership_get', {}).get('values', None)
	if values:
		exp_date = values[0].get('end_date', None)
		status_id = values[0].get('status_id', None)
	
	print((
		"Contact id: {contact_id} "
		"Name: {first_name} {last_name} "
		"Post Code: {postal_code} "
		"Membership No.: {custom_8} "
		"Expiry Date: {exp_date}"
		"Status ID: {status_id}"
	).format(
		exp_date=exp_date,
		status_id=status_id,
		**member
	))
	
#print(members)
#import pdb
#pdb.set_trace()

#print member
