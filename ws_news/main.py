from ws_news.common.classes import EstadaoNews
from ws_news.common.database import create_tables, get_connection


if __name__ == "__main__":
    create_tables()

    en = EstadaoNews()
    articles = en.get_articles("Tarcisio")
    print(articles[0].upsert_article())
    en.go_to_next_page()
