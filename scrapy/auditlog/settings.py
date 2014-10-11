# -*- coding: utf-8 -*-

# Scrapy settings for auditlog project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ManageBacScraper'

SPIDER_MODULES = ['auditlog.spiders']
NEWSPIDER_MODULE = 'auditlog.spiders'

SCHOOL = 'igbis'
OPEN_APPLY_URL = 'https://{}.openapply.com'.format(SCHOOL.lower())
OPEN_APPLY_LOGIN = OPEN_APPLY_URL + '/users/sign_in'
MANAGEBAC_URL = 'https://{}.managebac.com'.format(SCHOOL.lower())
MANAGEBAC_LOGIN = MANAGEBAC_URL + '/login'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Adam Morris of IGBIS here, how ya doing? As for me, aight, just testing my special spider is all. (adam.morris@igbis.edu.my)'

ITEM_PIPELINES = {
#        'auditlog.pipelines.AuditlogPipeline': 2,
		'auditlog.pipelines.ClassPeriodsPipeline': 1
	}