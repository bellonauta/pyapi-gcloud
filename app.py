#-------------------------------------------------------------------------
# Starter da aplicação.
# --> Execute diretamente quando para debug.
#-------------------------------------------------------------------------

import os
import json

import py_api_consts as cts
import rest_products as rest
import py_api_functions as fns

from flask import Flask, request

# Define tipo do ambiente de execução...
in_production = (os.environ.get('IN_PRODUCTION') != None and os.environ['IN_PRODUCTION'] == "1")

application = Flask(__name__)
@application.route('/', methods=cts._HTTP_METHODS)
def api():   
    request_pars = {'httpMethod': request.method}    
    # Conversões & adaptações...
    request_pars['body'] = ''
    if request.method == cts._GET:
        if type(request.json) is dict and 'queryStringParameters' in request.json:
            request_pars['body'] = json.dumps(request.json['queryStringParameters'])
        else:
            request_pars['body'] = json.dumps(request.values.to_dict())
    elif type(request.json) is dict:
        if 'body' in request.json:
            request_pars['body'] = request.json['body']   
        else:
            request_pars['body'] = request.json
    #   
    response = rest.handler(request=request_pars, in_production=in_production)      
    #
    return response

if __name__ == '__main__':
    # Quando esse script é executado diretamente(__main__), será em debug mode na porta 5000.
    # >python3 app.py
    application.run(debug=True, port=5000)    
