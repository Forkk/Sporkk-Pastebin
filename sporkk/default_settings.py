# Default Sporkk config file.

SQLALCHEMY_DATABASE_URI = 'mysql://sporkk@127.0.0.1/sporkk'


# Length of generated short URLs
SHORTURL_LENGTH = 5

# Port number for test server.
SERVER_PORT = 5000


############################
#### ANTI-SPAM SETTINGS ####
############################

# How long (in seconds) a given IP must wait between posting things.
POST_COOLDOWN_TIME = 20

# When someone shortens a URL, if this is set to true, and the URL they're shortening has already been shortened, Sporkk will give them the URL it's already been shortened to, rather than generating another URL ID for it.
# This does help prevent spam, but it also adds an extra database lookup every time someone tries to shorten a URL.
SHORTEN_PREVENT_DUPE_IDS = True
