from sporkk import app
app.run(app.config.get('SERVER_NAME'), app.config.get('SERVER_PORT'))
