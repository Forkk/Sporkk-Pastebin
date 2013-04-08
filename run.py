from sporkk import app

if __name__ == "__main__":
	app.run(app.config.get('SERVER_NAME'), app.config.get('SERVER_PORT'))
