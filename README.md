# PyApi - API REST de Pedidos de Venda em Python 

É uma aplicação exclusivamente de nível backend que se propõe
apresentar uma implementação, conteinerizada com docker, de uma API REST em Python.

Está baseada no atendimento ao processo de pedidos de vendas.
Permitirá em seu último release:
- CRUD de produtos;
- CRUD de fabricantes;
- CRUD de pedidos;
- CRUD de clientes.

Nesse primeiro release, estão implementados somente os CRUDs para produtos e fabricantes.

# VSCode - Docker Desktop - WSL2 - Google Cloud Run
Toda a implementação foi realizada no VSCode e o conteiner gerado está configurado para
ser "dockado" no Google Cloud Run.

---
## Dependências
- Python >= 3.7
    - typing (+AbstractSet e Union)
    - json
    - jsonschema (+validate)
    - psycopg2 (+extras)
    - abc (+abstractmethod)
    - unittest

- PostgreSQL >= 9.6    

- VSCode
- WSL2 (Desenvolvido no distro Debian)
- Docker & Docker Desktop(Windows)
- Google cloud run

---
## Testes
### Do container
Abrir o projeto no container e executar no terminal:\
<font color='grey'>$ python3 app.py</font>

### Unitários
Os testes unitários foram implementados com o framework unittest, e estão no script "tdd/py_api_test_product.py".\
Execute no terminal:\
<font color='grey'>$ python3 -m unittest tdd/py_api_test_product.py</font>

### Da API
Os testes de chamadas remotas para a API, podem ser feitos pelo https://www.postman.com/ ou pela biblioteca CURL ou qualquer outra aplicação/biblioteca.

---
## Deploy
A API foi desenvolvida para dockagem no Google Cloud Run, com a
extensão "Cloud Code" do VSCode.

Antes do deploy, verifique:

- Se a configuração de acesso ao banco PostgreSQL está corretamente definida no script "db/pg_conn.py". Esse script deve ser criado através da cópia do script de exemplo "db/pg_conn_sample.py";
- Se a porta do entrypoint está corretamente configurada no Dockerfile de deploy(na pasta raiz do projeto), no "CMD", conforme sua configuração no Google Cloud Run. O padrão é a resposta da API na porta tcp 8080.

---
## CRUDs de produtos e fabricantes

- **PUT** - Inclusão de produtos
    - Solicitação tipo 1 - Com associação de fabricante já cadastrado ao produto:
      <pre>
      {    
         "name": "Grape juice",
         "description": "Natural grape juice",
         "barcode": "7002085002679",
         "manufacturer": {
             "id": 2
         },
         "unitPrice": 25.89
      }
      </pre>

      - Solicitação tipo 2 - Com inclusão de fabricante para o produto:
      <pre>
      {    
         "name": "Grape juice",
         "description": "Natural grape juice",
         "barcode": "7002085002679",
         "manufacturer": {
             "name": "New manufacturer & Co."
         },
         "unitPrice": 25.89
      }
      </pre>

    - Retorno:
        - Sucesso:
          <pre>   
          {  "statusCode": 200,
             "body": { 
                 "id": 359,
                 "name": "Grape juice",
                 "description": "Natural grape juice",
                 "barcode": "7002085002679",
                 "manufacturer": {
                     "id": 2,
                     "name": "Quality farm goods"
                 },    
                 "unitPrice": 25.89
             }    
          }
          </pre>
        - Falha:
          <pre>
          {  "statusCode": HTTP status code(!= 200)
             "body: {
                 "message": "Descrição da falha/erro."
             }
          }  
          </pre>  

- **POST** - Alteração de produtos
    - Solicitação tipo 1 - Com troca de fabricante(já cadastrado) do produto:
      <pre>
      {    
         "id": 359, 
         "name": "Orange juice",
         "description": "Natural orange juice",
         "barcode": "7002085001213",
         "manufacturer": {
             "id": 3
         },
         "unitPrice": 20.89
      }
      </pre>

      - Solicitação tipo 2 - Com inclusão de fabricante para o produto:
      <pre>
      {    
         "name": "Orange juice",
         "description": "Natural Orange juice",
         "barcode": "7002085001213",
         "manufacturer": {
             "name": "New orange manufacturer & Co."
         },
         "unitPrice": 20.89
      }
      </pre>

    - Retorno:
        - Sucesso:
          <pre>   
          {  "statusCode": 200,
             "body": { 
                 "id": 359,
                 "name": "Orange juice",
                 "description": "Natural Orange juice",
                 "barcode": "7002085001213",
                 "manufacturer": {
                     "id": 3,
                     "name": "New orange manufacturer & Co."
                 },    
                 "unitPrice": 20.89
             }    
          }
          </pre>
        - Falha:
          <pre>
          {  "statusCode": 404 Quando chave inexistente
             "body: {
                 "message": "Descrição da falha/erro."
             }
          }   
        </pre>           

- **DELETE** - Exclusão de produtos \
Cabe ressaltar que um produto ou fabricante nunca é excluído, mas somente marcado(s) como inativo(s). Isso se faz necessário para se manter a fidelidade, história e consistência dos dados.

    - Solicitação tipo 1 - Com troca de fabricante(já cadastrado) do produto:
      <pre>
      {    
         "id": 359 
      }
      </pre>

    - Retorno:
        - Sucesso:
          <pre>   
          {  "statusCode": 200,
             "body": { 
                 "id": 359,
                 "name": "Orange juice",
                 "description": "Natural Orange juice",
                 "barcode": "7002085001213",
                 "manufacturer": {
                     "id": 3,
                     "name": "New orange manufacturer & Co."
                 },    
                 "unitPrice": 20.89
             }    
          }
          </pre>
        - Falha:
          <pre>
          {  "statusCode":  404 Quando chave inexistente
             "body: {
                 "message": "Descrição da falha/erro."
             }
          }    
          </pre>                    

- **GET** - Consultas aos produtos 

    - Solicitação(Query parameters) tipo 1 - Consultar os detalhes de um produto em específico:
      <pre>
        ?id=359
      </pre>      

        - Retorno:
             - Sucesso:
               <pre>   
               {  "statusCode": 200,
                  "body": { 
                      "id": 359,
                      "name": "Orange juice",
                      "description": "Natural Orange juice",
                      "barcode": "7002085001213",
                      "manufacturer": {
                          "id": 3,
                          "name": "New orange manufacturer & Co."
                      },    
                      "unitPrice": 20.89
                  }    
               }
               </pre>
             - Falha:
               <pre>
               {  "statusCode": HTTP status code(!= 200)
                  "body: {
                      "message": "Descrição da falha/erro."
                  }
               }    
               </pre>                              

    - Solicitação(Query parameters) tipo 2 - Listagem de todos os produtos cadastrados. A listagem é paginada e ordenada conforme o informado nos parâmetros:
      <pre>
        ?page=2&order=name or id
      </pre>      

        - Retorno:
             - Sucesso - Com produtos na página solicitada:
               <pre>   
               {  "statusCode": 200,                 
                  "body": { 
                      "maxRowsPerPage": 50,
                      "page": 2,
                      "rows": [{
                         "id": 359,
                         "name": "Orange juice"
                      },{
                         "id": 358,
                         "name": "Other Orange juice"
                      }, ... ]  
                  }    
               }
               </pre>
             - Sucesso - Sem produtos na página solicitada:
               <pre>   
               {  "statusCode": 200,                 
                  "body": { 
                      "maxRowsPerPage": 50,
                      "page": 2,
                      "rows": []
                  }    
               }
               </pre>  
             - Falha:
               <pre>
               {  "statusCode": HTTP status code(!= 200)
                  "body: {
                      "message": "Descrição da falha/erro."
                  }
               }    
               </pre>          
---
## Tabelas
Se desejar a criação automática das tabelas, restaure o arquivo "db/pg_db.backup" sobre o banco que você criou.
- Produtos:
  <pre>
  CREATE TABLE schema_name.product
  (
      id integer NOT NULL DEFAULT nextval('product_id_seq'::regclass),
      name character varying(60) COLLATE pg_catalog."default",
      description character varying COLLATE pg_catalog."default",
      barcode character varying(100) COLLATE pg_catalog."default",
      unitprice numeric(11,2),
      active character varying(1) COLLATE pg_catalog."default",
      CONSTRAINT product_pkey PRIMARY KEY (id)
  )
  </pre>

- Fabricantes:
  <pre>
  CREATE TABLE schema_name.manufacturer
  (
      id integer NOT NULL DEFAULT nextval('manufacturer_id_seq'::regclass),
      name character varying(60) COLLATE pg_catalog."default",
      CONSTRAINT manufacturer_pkey PRIMARY KEY (id)
  )
  </pre>

- Clientes:
  <pre>
  CREATE TABLE schema_name.consumer
  (
      id integer NOT NULL DEFAULT nextval('consumer_id_seq'::regclass),
      name character varying(60) COLLATE pg_catalog."default",
      phone character varying(15) COLLATE pg_catalog."default",
      email character varying(100) COLLATE pg_catalog."default",
      active character varying(1) COLLATE pg_catalog."default",
      CONSTRAINT consumer_pkey PRIMARY KEY (id)
  )
  </pre>

- Fabricantes por produto:
  <pre>
  CREATE TABLE schema_name.productmanufacturer
  (
      product_id integer NOT NULL,
      manufacturer_id integer NOT NULL,
      active character varying(1) COLLATE pg_catalog."default",
      CONSTRAINT productmanufacturer_pkey PRIMARY KEY (product_id, manufacturer_id)
  )
  </pre>

- Pedidos:
  <pre>
  CREATE TABLE schema_name."order"
  (
      id integer NOT NULL DEFAULT nextval('order_id_seq'::regclass),
      status character varying(30) COLLATE pg_catalog."default",
      consumer integer,
      payment_mode character varying(30) COLLATE pg_catalog."default",
      payment_amount numeric(12,2),
      payment_installments integer,
      payment_installment_value numeric(11,2),
      delivery_mode character varying(40) COLLATE pg_catalog."default",
      CONSTRAINT order_pkey PRIMARY KEY (id)
  )
  </pre>  

- Produtos dos pedidos:
  <pre>
  CREATE TABLE schema_name.orderproduct
  (
      order_id integer NOT NULL,
      product_id integer,
      product_units numeric(7,3),
      product_unit_price numeric(11,2),
      product_unit_amount numeric(12,2),
      CONSTRAINT orderproduct_pkey PRIMARY KEY (order_id, product_id)
  )
  </pre>   

---
## ToDo
- CRUD dos clientes;
- CRUD dos pedidos;


