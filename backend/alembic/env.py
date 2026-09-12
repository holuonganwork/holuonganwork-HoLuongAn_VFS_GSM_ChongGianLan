from logging.config import fileConfig

from alembic import context
from alembic.autogenerate.api import AutogenContext
from app.core.config import get_settings
from app.db.base import Base, UTCDateTime
from app.models import entities  # noqa: F401
from sqlalchemy import JSON, create_engine, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def render_item(kind: str, value: object, autogen: AutogenContext) -> str | bool:
    """Keep generated revisions self-contained, including custom UTC/JSON variants."""
    if kind == "type" and isinstance(value, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    if kind == "type" and isinstance(value, JSON):
        autogen.imports.add("from sqlalchemy.dialects import postgresql")
        return 'sa.JSON().with_variant(postgresql.JSONB(), "postgresql")'
    return False


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")
    if connection is not None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
