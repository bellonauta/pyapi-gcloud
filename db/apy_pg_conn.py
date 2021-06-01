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
                       'host': '35.199.98.84', # Gcloud
                       'port': 5432,
                       'name': 'gcloud',
                       'user': 'postgres',
                        'pwd': '03*1966pggc'
                    }
}                                            