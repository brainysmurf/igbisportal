# -*- coding: utf-8 -*-

#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import gns

BOT_NAME = 'oa_scraper'

SPIDER_MODULES =  ['portal.scrapers.oa_scraper.oa_scraper.spiders']
NEWSPIDER_MODULE = 'portal.scrapers.oa_scraper.oa_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = gns.config.openapply.admin_username

ITEM_PIPELINES = {
		'portal.scrapers.oa_scraper.oa_scraper.pipelines.AuditLogPipeline': 1
	}
