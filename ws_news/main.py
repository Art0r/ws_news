from ws_news.database import create_tables
from ws_news.news import CNNNews, GUmNews

if __name__ == "__main__":
    create_tables()

    cnn = CNNNews(maximum_depth=1)
    g1 = GUmNews(maximum_depth=2)

    for i in [g1]:
        i.fetch_articles("Lula")
        articles = i.get_articles_queue()

        while not articles.empty():
            article = articles.get()
            article.insert_article()
