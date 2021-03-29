import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from myinvestorsbank.items import Article


class MyinvestorsbankSpider(scrapy.Spider):
    name = 'myinvestorsbank'
    start_urls = ['https://www.myinvestorsbank.com/Community/News-Events']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-events-item"]')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('./div[@class="date"]/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@id="main-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
