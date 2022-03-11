from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="CONF",
    environments=True,
    load_dotenv=True
)
