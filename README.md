# QR-Code-Reader

Includes code for download from CiviCRM's API to a local database, a script for reading a QR code swipe and using it to update an attendance record local DB

## Design

**The intention of this section** is to document the work to create a local copy of the membership database from CiviCRM data.

We have mapped out some user stories for the project in a Trello board https://trello.com/b/tOOTKhYW/2018-12-qr-code-reader

but you possibly cannot see this without me getting an authorisation organized.

In broad terms the project was to

    1. create a local copy of some fields of the CiviCRM membership database (and have it updated daily to check for member expiry)
    2. have a card reader scan member card for member ID number when arriving for a meeting at Moorabbin
    3. look up local DB and alert if membership had expired
    4. create an attendance record for each member in a local attendance DB
    5. upload the attendance DB records for the meeting to CiviEvents for later review


I hope that is clearer as a project description.

The php could be hosted on a Raspberry Pi web server as could the other components of the system.

**The php script I am looking to develop is around items 2, 3 and 4. **

Python could be used to handle 1 and 4. 

Item 1 seems best achieved as a rest api query from CiviCRM as it is quite quick.  A table join to get two additional fields adds to the complexity but we can pull the data into a JSON file and from there into a MariaDB on the Pi.  Maybe there is a more efficient, direct way of doing this.



This is the CiviCRM API generated URL but **does not work**.

```
https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Membership&action=get&api_key=userkey&key=sitekey&json={"sequential":1,"return":"contact_id.id,contact_id.last_name,contact_id.first_name,contact_id.postal_code,contact_id.custom_8,end_date,status_id.name"}
```

What works is
```
https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Contact&action=get&api_key=userKey&key=sitekey&json=contact_id&return=contact_id,last_name,first_name,postal_code,custom_8&api.Membership.get[custom_8,end_date,status_id.name]&options[limit]=0
```

Result is a JSON file with content like this per member:
```json
{
  "855": {
    "contact_id": "855",
    "first_name": "Robert",
    "last_name": "Brown",
    "contact_is_deleted": "0",
    "address_id": "837",
    "postal_code": "3124",
    "civicrm_value_membership_information_4_id": "811",
    "custom_8": "45170",
    "id": "855",
    "api_Membership_get": {
      "is_error": 0,
      "version": 3,
      "count": 1,
      "id": 842,
      "values": [
        {
          "id": "842",
          "contact_id": "855",
          "membership_type_id": "1",
          "join_date": "2006-12-14",
          "start_date": "2017-01-02",
          "end_date": "2020-01-01",
          "status_id": "2",
          "is_test": "0",
          "is_pay_later": "0",
          "membership_name": "Individual",
          "relationship_name": "Child of"
        }
      ]
    }
  }
}
```

With the api_Membership_get part arising from the table join to get the required fields.

Which is messy because of the table join to get 'end_date' and 'status_id'.

I then use
```
wget -O members-list.json https://www.melbpc.org.au ...
```
to create a local copy.

I was intending to use a python script to load the required fields and write them to a MariaDB file on the Rasp Pi from this but is made difficult (for me) because of the joined fields.

See [`ReadFromJSON.py`](ReadFromJSON.py) 

Another option to pursue is to use this query
'https://www.melbpc.org.au/index.php/qrcheck/?contact_id=855'
and python's Beautiful Soup and requests but to pull in from 3000 records could be very slow.  150 records took  a couple of minutes whereas the API route is very quick.
