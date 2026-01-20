from ws_news.common.classes import EstadaoNews, GUmNews
from ws_news.common.database import create_tables, get_connection


if __name__ == "__main__":
    create_tables()

    # en = EstadaoNews()
    # en.run("Tarcisio")
    g1 = GUmNews()
    g1.run("Tarcisio")
