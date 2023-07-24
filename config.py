from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5532/postgres",
)
APP_PORT = env.int("APP_PORT", default=8000)

SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES",
                                           default=30)

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default=("postgresql+asyncpg://"
             "postgres_test:postgres_test@0.0.0.0:5632/postgres_test"),
)

REDIS_HOST = env.str("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)


SMTP_HOST = env.str("SMTP_HOST", default="smtp.gmail.com")
SMTP_PORT = env.int("SMTP_PORT", default=465)
SMTP_USER = env.str("SMTP_USER", default="fomichev.ser.v@gmail.com")
SMTP_PASSWORD = env.str("SMTP_PASSWORD", default="awtiwpicfgdztfxi")
