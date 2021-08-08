from __future__ import print_function

from typing import List

import mysql.connector
from django.core.management.base import BaseCommand
from tinylinks.management.commands import _config, _queries
from tinylinks.models import Tinylink, TinylinkLog


TINYLINK_QUERY = "SELECT url, keyword FROM yourls_url LIMIT %s, %s;"
TINYLINKLOG_QUERY = "SELECT referrer, user_agent, ip_address, click_time FROM yourls_log LIMIT %s, %s;"


class Command(BaseCommand):
    def get_tinylinks_query_data(self, start) -> List[tuple]:
        cnx = mysql.connector.connect(**_config.config)
        cursor = cnx.cursor()
        cursor.execute(TINYLINK_QUERY, (start, self.chunk_length))
        data = [(long_url.decode('utf-8'), short_url) for (long_url, short_url) in cursor]
        cnx.close()
        cursor.close()
        return data

    def insert_tinylinks(self):
        start = 0
        data = self.get_tinylinks_query_data(start)
        while data:
            tinylinks_to_add = [
                Tinylink(long_url=long_url, short_url=shorturl)
                for long_url, shorturl in data
            ]
            Tinylink.objects.bulk_create(tinylinks_to_add)
            start += self.chunk_length
            data = self.get_tinylinks_query_data(start)

    def get_tinylinks_logs_query_data(self, start) -> List[tuple]:
        cnx = mysql.connector.connect(**_config.config)
        cursor = cnx.cursor()
        cursor.execute(TINYLINKLOG_QUERY, (start, self.chunk_length))
        data = [
            (referrer, user_agent, ip_address, click_time)
            for (referrer, user_agent, ip_address, click_time) in cursor
        ]
        cnx.close()
        cursor.close()
        return data

    def insert_tinylinks_logs(self):
        start = 0
        data = self.get_tinylinks_logs_query_data(start)
        while data:
            tinylinks_logs_to_add = [
                TinylinkLog(
                    referrer=referrer,
                    user_agent=user_agent,
                    remote_ip=remote_ip,
                    datetime=datetime,
                )
                for referrer, user_agent, remote_ip, datetime in data
            ]
            TinylinkLog.objects.bulk_create(tinylinks_logs_to_add)
            start += self.chunk_length
            data = self.get_tinylinks_logs_query_data(start)

    def add_arguments(self, parser):
        parser.add_argument("username", nargs=1, type=str)
        parser.add_argument("password", nargs=1, type=str)
        parser.add_argument("dbname", nargs=1, type=str)
        parser.add_argument("chunk-length", nargs="?", type=int, default=100)

    def handle(self, *args, **options):
        _config.set_configs(
            user=options["username"][0],
            password=options["password"][0],
            database=options["dbname"][0],
        )
        self.chunk_length = options.get("chunk-length")
        self.insert_tinylinks()
        self.insert_tinylinks_logs()
