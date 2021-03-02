from aptamer_api.web.views import *
from aptamer_api import aptamer_factory

global app

app = aptamer_factory.create_app(__name__)
app.app_context().push()
aptamer_factory.register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=7026)

