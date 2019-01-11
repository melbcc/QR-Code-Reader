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
		print("Contact id:", member['contact_id'], " Name:", member['first_name'], member['last_name'], "Post Code:", member['postal_code'], "membership No.:", member['custom_8'], "Expiry Date:", member['membership_type_id'])
	for api_Membership_get in member.items():
  #print(members)
