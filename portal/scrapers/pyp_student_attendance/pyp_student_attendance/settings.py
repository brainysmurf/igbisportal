# -*- coding: utf-8 -*-

#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import gns

BOT_NAME = 'mb_scraper'

SPIDER_MODULES = ['portal.scrapers.pyp_student_attendance.pyp_student_attendance.spiders']
NEWSPIDER_MODULE = 'portal.scrapers.pyp_student_attendance.pyp_student_attendance.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = gns.config.managebac.admin_username

ITEM_PIPELINES = {
    'portal.scrapers.pyp_student_attendance.pyp_student_attendance.pipelines.PYPClassReportsPipline': 1,
}

LOG_LEVEL = 'DEBUG'  # gns.config.scrapy.log_level
LOG_ENABLED = gns.config.scrapy.log_enabled
