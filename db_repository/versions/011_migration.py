from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cause = Table('cause', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('account_name', String(length=120)),
    Column('creation_date', DateTime),
    Column('cause_name', String(length=120), nullable=False),
    Column('cause_subtitle', String(length=120), nullable=False),
    Column('background_image', String(length=50)),
    Column('active_now', Boolean, default=ColumnDefault(False)),
    Column('goal', Integer, nullable=False),
    Column('current_amount', Integer, nullable=False),
    Column('stat1_icon', String(length=20)),
    Column('stat2_icon', String(length=20)),
    Column('stat3_icon', String(length=20)),
    Column('stat4_icon', String(length=20)),
    Column('stat1_number', String(length=20)),
    Column('stat2_number', String(length=20)),
    Column('stat3_number', String(length=20)),
    Column('stat4_number', String(length=20)),
    Column('stat1_text', String(length=20)),
    Column('stat2_text', String(length=20)),
    Column('stat3_text', String(length=20)),
    Column('stat4_text', String(length=20)),
    Column('quote1_text', String(length=300)),
    Column('quote1_person', String(length=50)),
    Column('quote1_image', String(length=50)),
    Column('quote2_text', String(length=300)),
    Column('quote2_person', String(length=50)),
    Column('quote2_image', String(length=50)),
    Column('quote3_text', String(length=300)),
    Column('quote3_person', String(length=50)),
    Column('quote3_image', String(length=50)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cause'].columns['creation_date'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cause'].columns['creation_date'].drop()
