import environ
env = environ.Env()
env.read_env(".env")

config = {
    "user": env.str("YOURLS_MYSQL_USER", ""),
    "password": env.str("YOURLS_MYSQL_PASSWORD", ""),
    "host": env.str("YOURLS_MYSQL_HOSTNAME", "localhost"),
    "database": env.str("YOURLS_MYSQL_DATABASE", ""),
    "raise_on_warnings": env.bool("YOURLS_MYSQL_RAISE_ON_WARNING", False),
}


def set_configs(user=None, password=None, database=None):
    config["user"] = user
    config["password"] = password
    config["database"] = database
