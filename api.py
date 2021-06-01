#-------------------------------------------------------------------------
# Starter da API.
# --> Utilize para o ENTRYPOINT do orquestrador/cloud.
#-------------------------------------------------------------------------

from app import application # Carga do starter da aplicação

if __name__ == "__main__":
    # Executar com uwsgi para entrypoint do container...
    # >uwsgi --http :5000 -w api:application    
    application.run(debug=False)