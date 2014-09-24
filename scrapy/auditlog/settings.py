# -*- coding: utf-8 -*-

# Scrapy settings for auditlog project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'auditlog'

SPIDER_MODULES = ['auditlog.spiders']
NEWSPIDER_MODULE = 'auditlog.spiders'

SCHOOL = 'igbis'
OPEN_APPLY_URL = 'https://{}.openapply.com'.format(SCHOOL.lower())
OPEN_APPLY_LOGIN = OPEN_APPLY_URL + '/users/sign_in'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'auditlog (+{})'.format(OPEN_APPLY_URL)

ITEM_PIPELINES = {
        'auditlog.pipelines.AuditlogPipeline': 1
	}