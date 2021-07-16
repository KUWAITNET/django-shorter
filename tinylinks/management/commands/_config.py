import environ
env = environ.Env()
env.read_env(".env")

config = {
    "user": env.str("MYSQL_USER", ""),
    "password": env.str("MYSQL_PASSWORD", ""),
    "host": env.str("MYSQL_HOSTNAME", ""),
    "database": env.str("MYSQL_DATABASE", ""),
    "raise_on_warnings": env.bool("MYSQL_RAISE_ON_WARNING", ""),
}


def set_configs(user=None, password=None, database=None):
    config["user"] = user
    config["password"] = password
    config["database"] = database
