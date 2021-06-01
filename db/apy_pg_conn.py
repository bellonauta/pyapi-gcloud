#--------------------------------------------------------------------
# Biblioteca de constantes para conexão com o PostgreSQL.
#--------------------------------------------------------------------

# Constantes de conexão com o banco de dados...
_PG_CONNECTION = {
                    'devel': {
                       'host': 'localhost',
                       'port': 5432,
                       'name': 'pyapi',
                       'user': 'postgres',
                        'pwd': 'postgres'
                    },
                    'production': {
                       'host': 'mycloud.com',
                       'port': 5432,
                       'name': 'pyapi',
                       'user': 'postgres',
                        'pwd': 'postgress'
                    }
}                                            