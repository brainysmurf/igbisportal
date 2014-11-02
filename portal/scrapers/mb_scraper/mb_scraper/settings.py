# -*- coding: utf-8 -*-

#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from portal.settings import get
import gns

get('USER', 'username', required=True)

BOT_NAME = 'mb_scraper'

SPIDER_MODULES = ['portal.scrapers.mb_scraper.mb_scraper.spiders']
NEWSPIDER_MODULE = 'portal.scrapers.mb_scraper.mb_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = gns.settings.username

ITEM_PIPELINES = {
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classperiods.ClassPeriodsPipeline': 1,
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.ClassReportsPipeline': 2
	}
