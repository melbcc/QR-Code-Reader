#!/usr/bin/env python

import os
import sys
import inspect
import re

import argparse
from flask import Flask, jsonify, abort, render_template, send_from_directory

# add ../lib folder
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'lib'))

from models import Member
from databases import local

# ----- Commandline Parameters
parser = argparse.ArgumentParser(description='Web Application.')

local.add_arguments(parser)

args = parser.parse_args()


# ----- Connect to Local Database
session = local.get_session(
	user=args.user,
	password=args.password,
	domain=args.domain,
	port=args.port,
	dbname=args.dbname,
)
from weblib.base import set_session
set_session(session)

# ----- Flask Application
from weblib.base import app
app.run(debug=True)
