#--------------------------------------------------------------------
# Exemplo de parâmetros para conexão com o PostgreSQL.
#  ---> Copie esse arquivo para um de nome "pg_conn.py".
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
                       'host': '35.36.37.38',
                       'port': 5432,
                       'name': 'pyapi',
                       'user': 'postgres',
                        'pwd': '123321'
                    }
}                                            