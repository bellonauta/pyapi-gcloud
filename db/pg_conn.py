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
                       'host': '35.199.98.84',
                       'port': 5432,
                       'name': 'postgres',
                       'user': 'postgres',
                        'pwd': '7230PGGc'
                    }
}                                            