import json
from aptamer_api.providers.temp_article_provider import TempArticleProvider
def populate(db, models, providers):
    provider = TempArticleProvider()
    with open('data/temp_articles.json') as file:
        data = json.load(file)
        for datum in data:
            provider.add(datum)
