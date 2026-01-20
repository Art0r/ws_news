from ws_news.common.classes import EstadaoNews
from ws_news.common.database import create_tables, get_connection


if __name__ == "__main__":
    create_tables()

    en = EstadaoNews()
    en.run("Tarcisio")
