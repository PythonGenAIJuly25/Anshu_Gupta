import mysql.connector
from mysql.connector import errorcode
import logging

class MySQLHandler:
    def __init__(self, config):
        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()

    def create_tables(self, sql_path="sql/create_tables.sql"):
        with open(sql_path, 'r') as f:
            for stmt in f.read().split(';'):
                stmt = stmt.strip()
                if stmt:
                    self.cursor.execute(stmt)
        self.conn.commit()

    def _get_or_create_user_agent(self, ua_string):
        self.cursor.execute("SELECT id FROM user_agents WHERE user_agent_string = %s", (ua_string,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        os, browser, device = "Unknown", "Unknown", "Desktop"
        if "Windows" in ua_string: os = "Windows"
        if "Chrome" in ua_string: browser = "Chrome"
        self.cursor.execute(
            "INSERT INTO user_agents (user_agent_string, os, browser, device_type) VALUES (%s, %s, %s, %s)",
            (ua_string, os, browser, device)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_batch_log_entries(self, entries):
        log_data = []
        for e in entries:
            ua_id = self._get_or_create_user_agent(e['user_agent'])
            log_data.append((
                e['ip_address'], e['timestamp'], e['method'], e['path'],
                e['status_code'], e['bytes_sent'], e['referrer'], ua_id
            ))
        self.cursor.executemany("""
            INSERT INTO log_entries 
            (ip_address, timestamp, method, path, status_code, bytes_sent, referrer, user_agent_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, log_data)
        self.conn.commit()

    def get_top_n_ips(self, n):
        self.cursor.execute("""
            SELECT ip_address, COUNT(*) as count
            FROM log_entries GROUP BY ip_address
            ORDER BY count DESC LIMIT %s
        """, (n,))
        return self.cursor.fetchall()

    def get_status_code_distribution(self):
        self.cursor.execute("""
            SELECT status_code, COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM log_entries), 2) AS percentage
            FROM log_entries
            GROUP BY status_code ORDER BY count DESC
        """)
        return self.cursor.fetchall()

    def get_hourly_traffic(self):
        self.cursor.execute("""
            SELECT DATE_FORMAT(timestamp, '%H:00') AS hour, COUNT(*) as count
            FROM log_entries
            GROUP BY hour ORDER BY hour
        """)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
