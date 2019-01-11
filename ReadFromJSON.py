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
	for api_Membership_get in member.items():
        print((
            "Contact id: {contact_id} "
            "Name: {first_name} {last_name} "
            "Post Code: {postal_code} "
            "Membership No.: {custom_8} "
            "Expiry Date: {membership_type_id}"
        ).format(**member))
  #print(members)
