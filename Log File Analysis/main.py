import argparse, logging, configparser
from log_parser import LogParser
from mysql_handler import MySQLHandler
from tabulate import tabulate

logging.basicConfig(level=logging.INFO)

def load_config(): #parser is a software component that analyzes text or data
    parser = configparser.ConfigParser()
    parser.read("config.ini")
    return dict(parser["mysql"])

def main():
    config = load_config()
    db = MySQLHandler(config)
    db.create_tables()
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    process_parser = subparsers.add_parser("process_logs")
    process_parser.add_argument("file_path")
    process_parser.add_argument("--batch_size", type=int, default=500)

    report_parser = subparsers.add_parser("generate_report")
    report_parser.add_argument("report_type", choices=["top_n_ips", "status_code_distribution", "hourly_traffic"])
    report_parser.add_argument("--n", type=int, default=5)

    args = parser.parse_args()

    if args.command == "process_logs":
        parser = LogParser()
        batch = []
        total = 0
        with open(args.file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parsed = parser.parse_line(line)
                if parsed:
                    batch.append(parsed)
                    if len(batch) >= args.batch_size:
                        db.insert_batch_log_entries(batch)
                        total += len(batch)
                        batch = []
                        logging.info(f"Processed {total} lines...")
        if batch:
            db.insert_batch_log_entries(batch)
            total += len(batch)
        logging.info(f"Finished. Total {total} lines processed.")
    
    elif args.command == "generate_report":
        if args.report_type == "top_n_ips":
            results = db.get_top_n_ips(args.n)
            print(tabulate(results, headers=["IP", "Requests"], tablefmt="grid"))
        elif args.report_type == "status_code_distribution":
            results = db.get_status_code_distribution()
            print(tabulate(results, headers=["Code", "Count", "Percent"], tablefmt="grid"))
        elif args.report_type == "hourly_traffic":
            results = db.get_hourly_traffic()
            print(tabulate(results, headers=["Hour", "Requests"], tablefmt="grid"))
    
    db.close()

if __name__ == "__main__":
    main()


