from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import pool

from alembic import context

from app.core.database import Base  
from app.models.user import Base as UserBase
from app.models.exercice import Base as ExerciceBase
from app.models.content import Base as ContentBase
from app.core.database import engine  

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Asegúrate de que sqlalchemy.url esté configurado correctamente
url = config.get_main_option("sqlalchemy.url")
print(f"SQLAlchemy URL: {url}")  # Agrega esta línea para depurar

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [UserBase.metadata, ExerciceBase.metadata, ContentBase.metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        future=True,
    ))

    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
