import os
import json

from flask import Flask, request

import py_api_consts as cst
import rest_products as rest
import py_api_functions as fns


# Define tipo do ambiente de execução...
in_production = (os.environ.get('IN_PRODUCTION') != None and os.environ['IN_PRODUCTION'] == 1)

application = Flask(__name__)
@application.route('/', methods=cst._HTTP_METHODS)
def api():   
    request_pars = {'httpMethod': request.method}    
    # Conversões & adaptações...
    if request.method == cst._GET:
        if 'queryStringParameters' in request.args:
             request_pars['queryStringParameters'] = request.args['queryStringParameters']   
        else:
             request_pars['queryStringParameters'] = json.dumps(request.args)   
    else:
        if 'body' in request.json:
             request_pars['body'] = request.json['body']   
        else:
             request_pars['body'] = request.json
    #
    return rest.handler(event=request_pars, context="", in_production=in_production)

if __name__ == '__main__':
    # run app in debug mode on port 5000
    # >python3 app.py
    application.run(debug=True, port=5000)    
