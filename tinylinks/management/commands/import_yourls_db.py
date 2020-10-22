from __future__ import print_function

from typing import List

from django.core.management.base import BaseCommand, CommandError
from tinylinks.models import Tinylink, TinylinkLog
from tinylinks.management.commands import _queries, _config
import mysql.connector


class Command(BaseCommand):

    def get_tinylinks_query_data(self) -> List[tuple]:
        cnx = mysql.connector.connect(**_config.config)
        cursor = cnx.cursor()
        cursor.execute(_queries.TINYLINK_QUERY)
        data = [(str(long_url), short_url) for (long_url, short_url) in cursor]
        cnx.close()
        cursor.close()
        return data

    def insert_tinylinks(self):
        data = self.get_tinylinks_query_data()
        tinylinks_to_add = [
            Tinylink(long_url=long_url, short_url=shorturl)
            for long_url, shorturl in data
        ]
        Tinylink.objects.bulk_create(tinylinks_to_add)

    def get_tinylinks_logs_query_data(self) -> List[tuple]:
        cnx = mysql.connector.connect(**_config.config)
        cursor = cnx.cursor()
        cursor.execute(_queries.TINYLINKLOG_QUERY)
        data = [(referrer, user_agent, ip_address, click_time)
                for (referrer, user_agent, ip_address, click_time) in cursor]
        cnx.close()
        cursor.close()
        return data

    def insert_tinylinks_logs(self):
        data = self.get_tinylinks_logs_query_data()
        tinylinks_logs_to_add = [
            TinylinkLog(referrer=referrer, user_agent=user_agent,
                        remote_ip=remote_ip, datetime=datetime)
            for referrer, user_agent, remote_ip, datetime in data
        ]
        TinylinkLog.objects.bulk_create(tinylinks_logs_to_add)

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        parser.add_argument('paassword', nargs='+', type=str)
        parser.add_argument('dbname', nargs='+', type=str)

    def handle(self, *args, **options):
        _config.set_configs(user=options['username'][0],
                            password=options['paassword'][0],
                            database=options['dbname'][0])
        self.insert_tinylinks()
        self.insert_tinylinks_logs()










