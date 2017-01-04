# -*- coding: utf-8 -*-

#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import gns

BOT_NAME = 'mb_scraper'

SPIDER_MODULES = ['portal.scrapers.mb_scraper.mb_scraper.spiders']
NEWSPIDER_MODULE = 'portal.scrapers.mb_scraper.mb_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = gns.config.managebac.admin_username

ITEM_PIPELINES = {
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classperiods.ClassPeriodsPipeline': 1,
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.ClassReportsPipeline': 2,
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.PYPClassReportsPipline': 3,
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.PYPTeacherAssignments': 4,
		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.PYPStudentAttendance': 5,
 		'portal.scrapers.mb_scraper.mb_scraper.pipelines.classreports.SecHRPipeline': 6,
		'scrapy.pipelines.files.FilesPipeline': 7,
 		#'portal.scrapers.mb_scraper.mb_scraper.pipelines.classperiods.GradeBookDump': 8,
	}

FILES_STORE = "/home/vagrant/data_dump/grade_reports"
LOG_LEVEL = gns.config.scrapy.log_level
LOG_ENABLED = gns.config.scrapy.log_enabled