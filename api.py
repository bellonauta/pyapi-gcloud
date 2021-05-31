from app import application

if __name__ == "__main__":
    # Executar com uwsgi para entrypoint do container...
    # >uwsgi --http :5000 -w api:application    
    application.run(debug=False)