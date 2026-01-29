from ws_news.article import CNNArticle

# from ws_news.news import CNNNews, EstadaoNews, GUmNews
from ws_news.database import create_tables, get_connection


if __name__ == "__main__":
    create_tables()

    # en = EstadaoNews()
    # en.run("Tarcisio")
    # g1 = GUmNews()
    # g1.run("Tarcisio")
    # cnn = CNNNews()
    # cnn.run("Tarcisio")

    cnn = CNNArticle(
        url="https://www.cnnbrasil.com.br/blogs/jussara-soares/eleicoes/kassab-ja-liberou-psd-nos-estados-diz-otto-alencar/",
        headline="Kassab já liberou PSD nos Estados, diz Otto Alencar",
    )
    print(cnn.get_article_text())
