from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import BaseModel


def add_arguments(parser):
    """
    Adds arguments to an <argparse.ArgumentParser> instance
    """
    group = parser.add_argument_group('Local Database Options')
    group.add_argument(
    	'--user', '-U', dest='user', default='postgres',
    	help="database service username",
    )
    group.add_argument(
    	'--password', '-P', dest='password', default='secret',
    	help="database service password",
    )
    group.add_argument(
    	'--domain', '-D', dest='domain', default='localhost',
    	help="database service domain, host name, or IP address",
    )
    group.add_argument(
    	'--port', '-p', dest='port', type=int, default=5432,
    	help="database service port",
    )
    group.add_argument(
    	'--dbname', '-d', dest='dbname', default='mydb',
    	help="database name",
    )


def get_session(user, password, domain, port, dbname):
    engine = create_engine(
    	'postgresql+psycopg2://{user}:{password}@{domain}/{dbname}?port={port}'.format(
    		user=user,
    		password=password,
    		domain=domain,
    		port=port,
    		dbname=dbname,
    	),
    	#pool_recycle=3600,
    )

    # TODO: can 1 python process contain more than one session?
    # ie: should this be a singleton implementation...
    # it's not that important right now
    # to test, just call this twice and see if each session works independently

    BaseModel.metadata.create_all(engine)  # creates tables if they don't already exist
    BaseModel.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()
