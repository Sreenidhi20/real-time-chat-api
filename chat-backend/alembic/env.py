from alembic import context
from sqlalchemy import create_engine, pool

from app.config import DATABASE_URL
from app.models import message as _message
from app.models import user as _user

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))

target_metadata = _message.Message.metadata
if _user.User.metadata is not target_metadata:
	raise RuntimeError("Alembic models must share the same metadata")


def run_migrations_offline() -> None:
	context.configure(
		url=DATABASE_URL,
		target_metadata=target_metadata,
		literal_binds=True,
		compare_type=True,
	)

	with context.begin_transaction():
		context.run_migrations()


def run_migrations_online() -> None:
	connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=target_metadata,
			compare_type=True,
		)

		with context.begin_transaction():
			context.run_migrations()


if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()