from flask import Flask



def create_app():
    app = Flask (__name__)
    #sapp.config['SERECT_Key'] = 'ahhh bb&&**R'
   


    from .views import views
    
    
    app.register_blueprint(views, url_prefix='/')

    return app    