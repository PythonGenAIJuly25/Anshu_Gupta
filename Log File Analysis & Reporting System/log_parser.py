import re
from datetime import datetime

class LogParser:
    # LOG_PATTERN = re.compile(
    #     r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+|-)'
    # )
    LOG_PATTERN = re.compile(
        r'(?P<ip>\S+)\s+'                         # IP address
        r'\S+\s+\S+\s+'                           # Remote logname and user
        r'\[(?P<timestamp>[^\]]+)\]\s+'           # Timestamp
        r'"(?P<request>[^"]+)"\s+'                # Request line
        r'(?P<status>\d{3})\s+'                   # Status code
        r'(?P<size>\S+)\s+'                       # Size of the response
        r'"(?P<referrer>[^"]*)"\s+'               # Referrer
        r'"(?P<user_agent>[^"]*)"'                # User agent
    )

    
    def parse_line(self, line):
        match = self.LOG_PATTERN.match(line)
        if match:
            ip = match.group(1)
            ts = datetime.strptime(match.group(2), '%d/%b/%Y:%H:%M:%S %z')
            request_parts = match.group(3).split()
            method = request_parts[0] if len(request_parts) > 0 else None
            path = request_parts[1] if len(request_parts) > 1 else None
            status = int(match.group(4))
            bytes_sent = int(match.group(5)) if match.group(5) != '-' else 0
            referrer = match.group(6)
            user_agent = match.group(7)
            return {
                'ip_address': ip,
                'timestamp': ts,
                'method': method,
                'path': path,
                'status_code': status,
                'bytes_sent': bytes_sent,
                'referrer': referrer,
                'user_agent': user_agent
            }
        else:
            print("Skiipped line",line.strip())
            return None



