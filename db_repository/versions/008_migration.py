from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cause = Table('cause', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('cause_name', VARCHAR(length=120), nullable=False),
    Column('cause_subtitle', VARCHAR(length=120), nullable=False),
    Column('background_image', VARCHAR(length=50)),
    Column('goal', INTEGER, nullable=False),
    Column('current_amount', INTEGER, nullable=False),
    Column('stat1_icon', VARCHAR(length=20)),
    Column('stat2_icon', VARCHAR(length=20)),
    Column('stat3_icon', VARCHAR(length=20)),
    Column('stat4_icon', VARCHAR(length=20)),
    Column('stat1_number', VARCHAR(length=20)),
    Column('stat2_number', VARCHAR(length=20)),
    Column('stat3_number', VARCHAR(length=20)),
    Column('stat4_number', VARCHAR(length=20)),
    Column('stat1_text', VARCHAR(length=20)),
    Column('stat2_text', VARCHAR(length=20)),
    Column('stat3_text', VARCHAR(length=20)),
    Column('stat4_text', VARCHAR(length=20)),
    Column('quote1_text', VARCHAR(length=300)),
    Column('quote1_person', VARCHAR(length=50)),
    Column('quote1_image', VARCHAR(length=50)),
    Column('quote2_text', VARCHAR(length=300)),
    Column('quote2_person', VARCHAR(length=50)),
    Column('quote2_image', VARCHAR(length=50)),
    Column('quote3_text', VARCHAR(length=300)),
    Column('quote3_person', VARCHAR(length=50)),
    Column('quote3_image', VARCHAR(length=50)),
    Column('active', BOOLEAN),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['cause'].columns['active'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['cause'].columns['active'].create()
