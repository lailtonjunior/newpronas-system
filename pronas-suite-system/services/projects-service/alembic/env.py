import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adicione o caminho do seu app para que o Alembic encontre seus modelos
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import Base  # Importe sua Base de modelos
from src.database import SQLALCHEMY_DATABASE_URL

# esta é a configuração do Alembic, que fornece acesso
# aos valores no arquivo .ini em uso.
config = context.config

# Interprete o arquivo de configuração para logging do Python.
# Esta linha assume um logger chamado "alembic" no seu alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# adicione aqui o objeto MetaData do seu modelo para suporte a 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Roda migrações no modo 'offline'.
    Isso configura o contexto com apenas uma URL
    e não um Engine, embora um Engine também seja aceitável aqui.
    Pulando a criação do Engine, não precisamos nem de um DBAPI disponível.
    """
    context.configure(
        url=SQLALCHEMY_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Roda migrações no modo 'online'.
    Neste cenário, precisamos criar um Engine
    e associar uma conexão com o contexto.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = SQLALCHEMY_DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()