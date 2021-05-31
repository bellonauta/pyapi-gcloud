#--------------------------------------------------------------------
# Biblioteca de classes base para o desafio TOTVS.
#--------------------------------------------------------------------

from typing import AbstractSet, Union
import json
import psycopg2
import psycopg2.extras
import abc
from abc import abstractmethod

import jsonschema
from jsonschema import validate

import py_api_functions as fns
import py_api_consts as cts

class ErrorHandlerClass:
    """ Classe base para outras que precisam gerenciar/registrar erros/falhas. """
    
    def __init__(self):
        # Privates...
        self.__error = False
        self.__error_message = ''
        self.__error_code = 0

    def set_error(self, msg, code=400):    
        '''Seta mensagem(msg) e código do erro na classe.'''
        self.__error = True
        self.__error_message = msg
        self.__error_code = code
        
    def get_error(self) -> bool: 
        return self.__error          

    def get_error_message(self) -> str:       
        return self.__error_message
    
    def get_error_code(self):       
        return self.__error_code   

    def no_errors(self):    
        """Elimina o erro registrado."""
        self.__error = False
        self.__error_message = ''
        self.__error_code = 0                      
#---------------------------------------------------------------------------------      


class DatabaseInterface(ErrorHandlerClass):    
    """ Interface para wrapper de banco de dados. """
    
    @abstractmethod
    def readable_exception(self, exception_err):
        """
        Formata e retorna uma mensagem de erro, pela exception
        ocorrida, mais legível.
        """ 
        pass
    
    @abstractmethod
    def key_not_found(self) -> bool:
        pass    
   
    @abstractmethod
    def connect(self, connParameters:dict) -> bool:
        pass
    
    @abstractmethod
    def get_connection(self):
        pass
    
    @abstractmethod
    def close_connection(self, pars: dict) -> bool:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass
    
    @abstractmethod
    def commit(self) -> bool:
        pass
    
    @abstractmethod
    def start_transaction(self) -> bool:
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        pass
    
    @abstractmethod
    def in_transaction(self) -> bool:
        pass        
    
    @abstractmethod
    def query(self, sql:str, pars:Union[dict,list], commit:False):
        pass
    
    @abstractmethod
    def fetch(self, clause:str, cursor) -> bool:
        """
        Busca o retorno da query executada e popula na propriedade __rows.
        Retorna bool True/False: Quanto ao sucesso na execução.        
        """     
        pass
    
    @abstractmethod
    def insert(self, table:str, fields:dict, sufix:str=''):
        """
        Executa a inclusão de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela para incluir o registro
           dict fields: Um dict com os campos e valores para inclusão no formato {nome_campo: value,...}
           str sufix: SQL command, opcional, que será adicionado no final da clásula de inclusão gerada
        """     
        pass
    
    @abstractmethod
    def update(self, table:str, pk:dict, fields:dict):
        """
        Executa a alteração de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela para alterar o registro
           dict pk: Um dict com os campos e valores da PK da tabela no formato {nome_col: value,...}
           dict fields: Um dict com os campos e valores para inclusão no formato {nome_col: value,...}.
        """     
        pass
    
    @abstractmethod
    def delete(self, table:str, pk:dict):
        """
        Executa a exclusão de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela para excluir o registro
           dict pk: Um dict com os campos e valores da PK da tabela no formato {nome_col: value,...}
        """     
        pass
    
    @abstractmethod
    def count_all(self, table:str, condition:dict):
        """
        Executa uma query de contagem de rows com uma determinada condição. 
        Parâmetros:
           str table: Nome da tabela para a contagem
           dict condition: Um dict com os campos e valores da condição no formato {nome_col: value,...}
        Retorna:
           Inicializa a propriedade "__rows" com com um dict com o total da contagem 
           no rótulo "count".(Ex: Para acessar, use: db.get_rows()[0]['count'])
        """     
        pass
    
    @abstractmethod
    def get_rows(self) -> list:
        pass
 
   
class DBPostgres(DatabaseInterface):
    
    def __init__(self) -> None:
        super().__init__()     
        #
        self.__rows = []
        self.__connection = None
        self.__in_transaction = False
        
        self.__key_not_found = False                                           
        
    def readable_exception(self, exception_err):
        """
        Formata e retorna uma mensagem de erro PG, pela exception
        ocorrida, mais legível.
        """ 
        ret = ''
        if exception_err:
            if exception_err.pgcode:
                ret = fns.to_str(exception_err.pgcode) 
            if exception_err.pgerror:
                ret += ('' if ret == '' else ' - ') + exception_err.pgerror
            if ret == '':
                try: 
                   ret = str(exception_err)
                except Exception as error:
                   ret = str(error)              
        else:
            ret = 'Exception desconhecida.' 
        #       
        return ret  
    
    def key_not_found(self) -> bool:
        """ 
        Retornar True logo após a tentativa de uma operação de 
        alteração/exclusão de chave/registro não existente.
        """        
        return self.__key_not_found    
          
    def connect(self, conn_pars:dict) -> bool:
        """ 
        Tenta a conexão com o banco PostgreSQL.
        Parâmetros:
          dict conn_pars: Um dicionário com os atributos para a conexão:
                            str name - Nome do banco                            
                            str host - Host do banco
                            int port - Porta do serviço do banco no host
                            str user - Usuário de login
                            str pwd - Senha do usuário
        Retorna:
          bool True/False quanto ao sucesso da conexão
        """
        try:
            dsn = "dbname='{}' user='{}' password='{}' host='{}' port='{}'".format(conn_pars['name'],
                                                                                   conn_pars['user'],
                                                                                   conn_pars['pwd'],
                                                                                   conn_pars['host'],
                                                                                   conn_pars['port'])
            #
            self.__connection = psycopg2.connect(dsn)
            self.__connection.set_session(readonly=False, 
                                          autocommit=False, 
                                          isolation_level=psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
        except psycopg2.Error as error:           
            self.__connection = None
            self.set_error(msg='Falha na conexão com o banco. [{}]'.format(self.readable_exception(error)))
        #
        return not self.get_error()  
    
    def get_connection(self):
        return self.__connection
    
    def is_connected(self) -> bool:
        return not fns.is_empty(self.__connection)
    
    def close_connection(self, pars: dict) -> bool:
        if self.is_connected():
            try: 
                self.__connection.close() 
            finally:
                self.__connection = None 
                
    def start_transaction(self) -> bool:
        self.no_errors()
        self.__in_transaction = self.is_connected()
        return self.__in_transaction
    
    def in_transaction(self) -> bool:
        return self.__in_transaction
    
    def commit(self) -> bool:
        self.no_errors()
        if self.__in_transaction:
            try:
                self.__connection.commit();          
            except psycopg2.Error as error:
                self.set_error(msg='Erro finalizando transação. [{}]'.format(self.readable_exception(error)))       
        #
        self.__in_transaction = False
        #
        return not self.get_error()
    
    def rollback(self) -> bool:
        self.no_errors()
        if self.__in_transaction:
            try:
                self.__connection.rollback();          
            except psycopg2.Error as error:
                self.set_error(msg='Erro cancelando transação. [{}]'.format(self.readable_exception(error)))             
        #
        self.__in_transaction = False    
        #
        return not self.get_error()
    
    def fetch(self, clause:str, cursor) -> bool:
        """
        Busca o retorno da query executada e popula na propriedade __rows.
        Retorna bool True/False: Quanto ao sucesso na execução.
        """        
        self.__rows = []     
        try: 
            if clause == 'select':
                if type(cursor) is psycopg2.extras.DictCursor and cursor.rowcount > 0:
                    self.__rows = cursor.fetchall()
            elif clause == 'insert' and type(cursor) is psycopg2.extras.DictCursor:
                # O INSERT pode retornar valores, por exemplo, quando
                # insere um novo registro e retorna a PK... 
                # Tenta ler(safe-mode) o retorno da query...
                try: 
                    self.__rows = cursor.fetchone() 
                except Exception as error:
                    self.__rows = []   
        except psycopg2.Error as error:
            self.set_error(msg='Falha no fetch da query. [{}]'.format(self.readable_exception(error)))        
        #                 
        return not self.get_error()        
        
    
    def query(self, sql:str, pars:Union[dict,list], commit:False):
        """
        Executar queries no Postgres.
        Parâmetros:
          str sql: SQL para execução.
          mixed pars: Um list/dict com parâmetros e/ou valores dos filtros/colunas(SQL INJECTION SAFE)
          connection conn: Handler de conexão com o banco
          bool commit: Passe True quando o commit deva ser executado após a execução da query.
        Retorna bool True/False: Quanto ao sucesso na execução.
        """
        self.no_errors()
        self.__rows = []        
        #
        if self.is_connected():
            cursor = self.__connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                sql_clause = sql[:6].strip().lower()
                cursor.execute(sql, pars)
                self.fetch(clause=sql_clause, cursor=cursor)
                #   
                if commit or (not self.__in_transaction and sql_clause == 'select'):
                    # Auto-commit...
                    self.commit()
            except psycopg2.Error as error:
                self.set_error(msg='Falha em execução de query. [{}]'.format(self.readable_exception(error)))
            finally:                      
                if cursor:
                    cursor.close()
                    del cursor
        else:       
            self.set_error(msg='Sem conexão com o banco.')            
        #                 
        return not self.get_error()
    
        
    def insert(self, table:str, fields:dict, sufix:str=''):
        """
        Executa a inclusão de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela par incluir o registro
           dict fields: Um dict com os campos e valores para inclusão no formato {nome_col: value,...}
           str sufix: SQL command, opcional, que será adicionado no final da clásula de inclusão gerada
        """       
        #
        sql = 'INSERT INTO ' +table+ ' ('+fns.implode(',',list(fields.keys()))+') VALUES (%(' + fns.implode(')s,%(',list(fields.keys())) + ')s)'
        #
        if sufix != '':
           sql += ' ' + sufix                  
        #     
        self.query(sql=sql, pars=fields, commit=False)                           
        #     
        return not self.get_error() 
    
    def update(self, table:str, pk:dict, fields:dict):
        """
        Executa a alteração de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela par incluir o registro
           dict pk: Um dict com os campos e valores da PK da tabela no formato {nome_col: value,...}
           dict fields: Um dict com os campos e valores para inclusão no formato {nome_col: value,...}.
        """   
        self.__key_not_found = False  
        self.count_all(table=table, condition=pk)
        if self.get_rows()[0]['count'] == 0:
            self.__key_not_found = True
            self.set_error('Tentativa de alterar registro não existente na tabela.')
        else:             
            parameters = {}           
            sets = ''
            pkwhere = ''
            pkcols = list(pk.keys())           
            setcols = list(fields.keys())
            p = 0
            #
            for c in pkcols:
                p += 1
                parameters['p'+str(p)] = pk[c]
                pkwhere += (' and ' if pkwhere != '' else '') + c + ' = %(' + 'p'+str(p) + ')s'
            #    
            for c in setcols:
                p += 1
                parameters['p'+str(p)] = fields[c]    
                sets += ('' if sets == '' else ', ') + c + ' = %(' + 'p'+str(p) + ')s'   
            #                        
            sql = 'UPDATE '+ table +' SET '+ sets +' WHERE '+ pkwhere
            #
            self.query(sql=sql, pars=parameters, commit=False)                           
        #     
        return not self.get_error()    
    
    def delete(self, table:str, pk:dict):
        """
        Executa a exclusão de um registro em uma tabela. 
        Parâmetros:
           str table: Nome da tabela para excluir o registro
           dict pk: Um dict com os campos e valores da PK da tabela no formato {nome_col: value,...}
        """    
        self.__key_not_found = False  
        self.count_all(table=table, condition=pk)
        if self.get_rows()[0]['count'] == 0:
            self.__key_not_found = True
            self.set_error('Tentativa de excluir registro não existente na tabela.')
        else: 
            pkwhere = ''
            pkcols = list(pk.keys()) 
            parameters = {}  
            p = 0
            #
            for c in pkcols:
                p += 1
                parameters['p'+str(p)] = pk[c]   
                pkwhere += (' and ' if pkwhere != '' else '') + c + ' = %(' + 'p'+str(p) + ')s'     
            #                        
            sql = 'DELETE FROM '+ table +' WHERE '+ pkwhere
            #
            self.query(sql=sql, pars=parameters, commit=False)                           
        #     
        return not self.get_error()    
    
    def count_all(self, table:str, condition:dict):
        """
        Executa uma query de contagem de rows com uma determinada condição. 
        Parâmetros:
           str table: Nome da tabela para a contagem
           dict condition: Um dict com os campos e valores da condição no formato {nome_col: value,...}
        Retorna:
           Inicializa a propriedade "__rows" com com um dict com o total da contagem 
           no rótulo "count".(Ex: Para acessar, use: db.get_rows()[0]['count'])
        """     
        where = ''
        cond_cols = list(condition.keys())   
        p = 0   
        parameters = {}     
        #
        for c in cond_cols:
            p += 1
            parameters['p'+str(p)] = condition[c]
            where += (' and ' if where != '' else '') + c + ' = %(' + 'p'+str(p) + ')s'     
        #   
        sql = 'SELECT COUNT(*) AS count FROM '+ table +' WHERE '+ where
        #
        self.query(sql=sql, pars=parameters, commit=False)                           
        #     
        return not self.get_error()              

    
    def get_rows(self) -> list:
        return self.__rows
        
#---------------------------------------------------------------------------------              
       

class CheckRequest(ErrorHandlerClass):
   
     def __init__(self, httpMethod: str, body:Union[str,dict], db: DatabaseInterface):
        super().__init__() 

        # Privates...
        self.__body = body
        self.__request = {}
        self.__db = db
        self.__http_method = httpMethod        

     def get_http_method(self):
         return self.__http_method

     def set_body(self, value: Union[str,dict]):
         if type(self.__body) is dict:
             self.__body = value
         else:   
             self.__body = value.strip()
     
     def get_body(self) -> Union[str,dict]:
         return self.__body
     
     def get_db(self):
         return self.__db
     
     def get_request(self) -> dict:
         """ Retorna o json decode(dict) do body(str json encode ou dict). """
         return self.__request
     
     @abstractmethod
     def get_schema(self) -> dict:
         """ Schema json de validação. """
         pass
     
     @abstractmethod
     def check(self) -> bool:
         """ Validação dos atributos do request. """
         pass

     def execute(self):
         # Consistências...
         if self.__http_method not in cts._HTTP_METHODS:
             self.set_error('Método inválido')
         elif self.__db is None:
             self.set_error('A conexão com o banco não foi estabelecida.')
         elif fns.is_empty(self.__body):
             self.set_error('O body/query da requisição está vazio(a).')    
         elif type(self.__body) is dict:
             self.__request = self.__body   
         else:    
             # JSON decode do body do request...
             try:                 
                 self.__request = json.loads(self.__body)                             
             except Exception as err:
                 self.set_error('Falha em json decode. [{}]'.format(str(err)))
         #                    
         # Validação do schema...
         if not self.get_error():
            if len(self.__request.keys()) == 0:
                self.set_error('Requisição vazia.')
            else:     
                self.check()                   
         #
         return not self.get_error()   
 
#---------------------------------------------------------------------------------    
     
class CRUDInterface(ErrorHandlerClass):
    """ Interface para CRUD de registros no banco. """
    
    @abstractmethod   
    def set_primary_key(self, value: dict):
        """ Setar um dicionário com os atributos e valores da chave primária em operação. """
        pass

    @abstractmethod
    def get_primary_key(self) -> dict:
        """ Retornar um dicionário com os atributos e valores da chave primária em operação. """
        pass      
    
    @abstractmethod
    def get_db(self) -> DatabaseInterface:
        """ Retornar a interface atual com o banco de dados. """
        pass
    
    @abstractmethod     
    def execute(self) -> bool:    
        """ 
        Tenta executar a operação com os registros no banco.
        Retorna: bool True/False
        """
        pass        
    
class CRUDWithSchemaValidation(CRUDInterface):
    """ 
    Classe base para operações de inclusão, alteração, exclusão 
    e consulta de registros, na(s) tabela(s), com validação do schema json do request.
    """
    def __init__(self, schema:dict, request:dict, db:DatabaseInterface):
         super().__init__()
         
         self.__schema = schema
         self.__request = request
         self.__db = db       
         self.__primary_key = {}  
    
    def set_primary_key(self, value: dict):
        self.__primary_key = value
        
    def get_primary_key(self) -> dict:
        return self.__primary_key        
        
    def get_schema(self) -> dict:
        return self.__schema
    
    def set_request(self, value:dict):        
        self.__request = value
        
    def get_request(self) -> dict:
        return self.__request
    
    def get_db(self) -> DatabaseInterface:
        return self.__db
    
    def execute(self) -> bool:    
        """
        Tenta a operação com os registros no banco.        
        Retorna: bool True/False
        """     
        if len(self.get_schema().keys()) == 0:            
            self.set_error(msg="O esquema de validação de request está vazio.")
        elif len(self.get_request().keys()) == 0:
            self.set_error(msg="O request está vazio.")    
        #
        return not self.get_error()                       
    
class CRUDWithoutSchemaValidation(CRUDInterface):
    """ 
    Classe base para operações de inclusão, alteração e exclusão 
    de registros, da(s) tabela(s), SEM validação do schema json do request.
    """

    def __init__(self, db:DatabaseInterface):
         super().__init__()         
     
         self.__db = db       
         self.__primary_key = {}  
    
    def set_primary_key(self, value: dict):
        self.__primary_key = value
        
    def get_primary_key(self) -> dict:
        return self.__primary_key
   
    def get_db(self) -> DatabaseInterface:
        return self.__db
    
    def execute(self) -> bool:    
        """
        Tenta a operação com os registros no banco.        
        Retorna: bool True/False
        """        
        return not self.get_error()                           
    
#-----------------------------------------------------------------------------    
     
class InsertMasterRecord(CRUDWithSchemaValidation):
    """
    Classe base para inclusão(PUT) de registros em tabela com
    validação do schema do request.
    """             
    def execute(self) -> bool:   
        """
        Tenta a inclusão de registros no banco.
        Retorna: bool True/False
        """              
        return super().execute()    
    
    
class UpdateMasterRecord(CRUDWithSchemaValidation):
    """ 
    Classe base para atualização(POST) de registros em tabela master com
    validação do schema do request.
    """    
    def execute(self) -> bool:    
        """
        Tenta a alteração de registros no banco.
        Retorna: bool True/False
        """
        return super().execute()
    
    
class DeleteMasterRecord(CRUDWithSchemaValidation):
    """ 
    Classe base para exclusão(DELETE) de registros em tabela master com
    validação do schema do request.
    """       
    def execute(self) -> bool:    
        """
        Tenta a exclusão de registros no banco.
        Retorna: bool True/False
        """
        return super().execute()   
    
class GetMasterRecord(CRUDWithSchemaValidation):
    """ 
    Classe base para consultas(GET) de registros em tabela master com
    validação do schema do request.
    """       
    def execute(self) -> bool:    
        """
        Tenta a consulta de registros no banco.
        Retorna: bool True/False
        """
        return super().execute()       
    
#---------------------------------------------------------------------------------        

class InsertDetailRecord(CRUDWithoutSchemaValidation):
    """ 
    Classe base para inclusão(PUT) de registros em tabela detail, sem
    validação do schema do request.
    """       
    def execute(self) -> bool:   
        """
        Tenta a inclusão de registros no banco.
        Retorna: bool True/False
        """              
        return super().execute()    
    
    
class UpdateDetailRecord(CRUDWithoutSchemaValidation):
    """ 
    Classe base para atualização(POST) de registros em tabela detail, sem
    validação do schema do request.
    """    
    def execute(self) -> bool:    
        """
        Tenta a alteração de registros no banco.
        Retorna: bool True/False
        """
        return super().execute()
    
    
class DeleteDetailRecord(CRUDWithoutSchemaValidation):
    """
    Classe base para exclusão(DELETE) de registros em tabela detail, sem
    validação do schema do request.
    """   
    def execute(self) -> bool:    
        """
        Tenta a exclusão de registros no banco.
        Retorna: bool True/False
        """
        return super().execute() 
    
class GetDetailRecord(CRUDWithSchemaValidation):
    """
    Classe base para consultas(GET) de registros em tabela detail, COM
    validação do schema do request.
    """   
    def execute(self) -> bool:    
        """
        Tenta a exclusão de registros no banco.
        Retorna: bool True/False
        """
        return super().execute()       
    
#---------------------------------------------------------------------------------        