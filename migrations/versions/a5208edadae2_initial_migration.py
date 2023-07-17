"""initial migration

Revision ID: a5208edadae2
Revises: 
Create Date: 2023-05-08 20:28:35.762588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5208edadae2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=25), nullable=False),
    sa.Column('last_name', sa.String(length=25), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('phone_number', sa.String(length=10), nullable=False),
    sa.Column('date_of_birth', sa.String(length=20), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('membership', sa.Boolean(), nullable=False),
    sa.Column('membership_checkout', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Customers_id'), ['id'], unique=False)

    op.create_table('Discount',
    sa.Column('discount', sa.DECIMAL(scale=2), nullable=True),
    sa.PrimaryKeyConstraint('discount')
    )
    op.create_table('Employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=25), nullable=False),
    sa.Column('last_name', sa.String(length=25), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('phone_number', sa.String(length=10), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    with op.batch_alter_table('Employees', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Employees_id'), ['id'], unique=False)

    op.create_table('Facilities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('Facilities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Facilities_id'), ['id'], unique=False)

    op.create_table('Activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('booking_type', sa.Enum('BOOKING', 'SESSION', 'TEAMEVENT', name='bookingtypes'), nullable=False),
    sa.Column('price', sa.DECIMAL(scale=2), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('times', sa.String(length=255), nullable=False),
    sa.Column('facility_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['facility_id'], ['Facilities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Activities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Activities_id'), ['id'], unique=False)

    op.create_table('ArchivedSessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=False),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('number_of_people', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ArchivedSessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ArchivedSessions_id'), ['id'], unique=False)

    op.create_table('Sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=False),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('number_of_people', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Sessions_id'), ['id'], unique=False)

    op.create_table('ArchivedBookings',
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('number_of_people', sa.Integer(), nullable=False),
    sa.Column('cost', sa.DECIMAL(scale=2), nullable=False),
    sa.Column('checkout_session', sa.String(length=255), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activities.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['Customers.id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['Employees.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['ArchivedSessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ArchivedBookings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ArchivedBookings_id'), ['id'], unique=False)

    op.create_table('Bookings',
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('number_of_people', sa.Integer(), nullable=False),
    sa.Column('cost', sa.DECIMAL(scale=2), nullable=False),
    sa.Column('checkout_session', sa.String(length=255), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activities.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['Customers.id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['Employees.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['Sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Bookings_id'), ['id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Bookings_id'))

    op.drop_table('Bookings')
    with op.batch_alter_table('ArchivedBookings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ArchivedBookings_id'))

    op.drop_table('ArchivedBookings')
    with op.batch_alter_table('Sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Sessions_id'))

    op.drop_table('Sessions')
    with op.batch_alter_table('ArchivedSessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ArchivedSessions_id'))

    op.drop_table('ArchivedSessions')
    with op.batch_alter_table('Activities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Activities_id'))

    op.drop_table('Activities')
    with op.batch_alter_table('Facilities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Facilities_id'))

    op.drop_table('Facilities')
    with op.batch_alter_table('Employees', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Employees_id'))

    op.drop_table('Employees')
    op.drop_table('Discount')
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Customers_id'))

    op.drop_table('Customers')
    # ### end Alembic commands ###
