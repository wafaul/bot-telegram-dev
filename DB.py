from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Boolean
import configparser

def ConfigSectionMap(section):
    dict1 = {}
    options = cfg.options(section)
    for option in options:
        try:
            dict1[option] = cfg.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

cfg = configparser.ConfigParser()
cfg.read("config.cfg")
mysql_cfg = ConfigSectionMap("mysql")

Base = declarative_base()


class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    user_id = Column(String, nullable=False)
    chat_id = Column(String, nullable=False)
    is_bot = Column(Boolean, nullable=False)

    email = Column(String)
    language_code = Column(String)
    loc_long = Column(String)
    loc_lat = Column(String)   
    def __init__(self, language_code='en'):
        self.language_code = language_code


class Main():
    def __init__(self):
        pass

    def __del__(self):
        pass

    def run(self):
        #   INSERT
        if not session.query(exists().where(User.email == 'test@example.net')).scalar():
            u1 = Profile()
            u1.username = "test"
            u1.first_name = "Test"
            u1.last_name = "User"
            u1.email = "test@example.net"


            session.add(u1)
            session.commit()

        #   test, jestli v DB dany zaznam existuje:
        #print session.query(Address).filter_by(city='City WTF').count()
        #print bool( session.query(Address).filter_by(city='City WTF').count() )

        #   SELECT
        #   UPDATE
        if session.query(exists().where(Profile.email == 'test@example.net')).scalar():
            session.query(Profile).filter_by(email='test@example.net').update({"last_name": "a"})
            session.commit()

        if session.query(exists().where(Profile.email == 'test@example.net')).scalar():
            u = session.query(Profile).filter_by(email='test@example.net').first()
            u.last_name = "b"
            session.commit()


        #   DELETE
        if session.query(exists().where(Profile.email == 'test@example.net')).scalar():
            session.query(Profile).filter_by(email='test@example.net').delete()
            session.commit()


if __name__ == '__main__' or __name__ == 'Test':    # http://stackoverflow.com/a/419986/1974494
                                                    #  __main_ - spusteni jako skript, 'Test' - jako modul
    connection_str = 'mysql://'+mysql_cfg['user']+':'+mysql_cfg['password']+'@'+mysql_cfg['host']+':'+mysql_cfg['port']+'/'+mysql_cfg['db']
    engine = create_engine(connection_str,echo=False)
    #engine = create_engine('mysql://test:test@localhost:3306/test', echo=False)
    #engine = create_engine('sqlite:///db.sqlite3')
    '''
        sqlite:///:memory: (or, sqlite://)
        sqlite:///relative/path/to/file.db
        sqlite:////absolute/path/to/file.db
    '''
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    Main().run()

    connection.close()
