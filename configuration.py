from exceptions import ModuleError
from database import PostgresManager

default_config = {'db_config': None}


def configure_orm(config):
    default_config.update(config)

    db_config = config.get('db_config', None)
    if not db_config:
        raise ModuleError(
            'Imposible to configure without database configuration!'
        )

    loop = config.get('loop', None)
    if not loop:
        raise ModuleError(
            'Imposible to configure without main loop!'
        )
    db_config['loop'] = loop

    dm = PostgresManager(db_config)
    config.update({'dm': dm})

    return config
