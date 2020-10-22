TINYLINK_QUERY = """ SELECT url, keyword
                     FROM yourls_url;"""

TINYLINKLOG_QUERY = """ SELECT referrer, user_agent, ip_address, click_time
                        FROM yourls_log;"""