from django.core.management.base import BaseCommand
from openedxstats.apps.sites.models import AccessLogAggregate, FilenameLog
import boto
import io
import gzip
from urllib import parse

"""
fetch_referrer_logs.py (based off load_logo_referrers_summary.py)

Script to automate fetching logo logs, and counting the number of referrers.
This program will use download all logo logs from the S3 edx-static-cloudfront
bucket, and parse them to discover any new logs and save the referrer data.
All data is saved in the Django DB.

This script should be run on a scheduled basis.

Suggested queries (mySQL):

select domain, min(date) from access_log_aggregate where domain not like '%.amazonaws.com' and domain not rlike '([[:digit:]]+\\.){3}[[:digit:]]+:?' and domain not rlike ':[[:digit:]]+' and domain not like '%.edx.org' group by domain order by min(date);

"""

# 0 = mimimal output, 1 = verbose output
DEBUG = 0


class Command(BaseCommand):
    help = 'Fetches AWS Open edX logo referrer logs and save any new logs to a database.'

    def add_arguments(self, parser):
        parser.add_argument('--verbose',
                            dest='verbose',
                            action='store_true',
                            default=False,
                            help='Enable verbose output, useful for debugging.')

    def handle(self, *args, **options):
        if options['verbose']:
            global DEBUG
            DEBUG=1
        run_command()


class LogLine(object):
    def __init__(self, line):
        self.parts = line.split("\t")
        self.parsed = parse.urlparse(self.parts[9])

    @property
    def host(self):
        return self.parsed.netloc

    @property
    def client_ip(self):
        return self.parts[4]

    @property
    def uri(self):
        return self.parts[7]

    @property
    def date(self):
        return self.parts[0]

    @property
    def time(self):
        return self.parts[1]


class HostInfo(object):
    def __init__(self):
        self.hits = 0
        self.ips = set()

    def add(self, logline):
        self.hits += 1
        self.ips.add(logline.client_ip)


def is_in_filename_log(log_name):
    file_exists = FilenameLog.objects.filter(filename=log_name).count()
    if file_exists:
        return True
    else:
        return False


def add_to_filename_log(log_name):
    file_to_add = FilenameLog(filename=log_name)
    file_to_add.save() #FIXME: Change to commit=false until entire program runs through?


def process_log_file(gz_file, log_name):
    if DEBUG:
        print("Processing %s ..." % log_name)
    line_counter = {}
    aggregate_logs = []

    for line in gz_file.splitlines():
        if line.startswith('#'):
            continue

        logline = LogLine(line)
        if logline.uri.startswith("/openedx-logos"):
            line_key = "|".join((logline.host, logline.date, log_name))
            if line_key in line_counter:
                line_counter[line_key] += 1
            else:
                line_counter[line_key] = 1

    for aggregate_line_key in line_counter:
        (host, date, log_name) = aggregate_line_key.split("|")
        line_count = line_counter[aggregate_line_key]
        new_aggregate_log = AccessLogAggregate(
            domain=host,
            access_date=date,
            filename=log_name,
            access_count=line_count
        )
        aggregate_logs.append(new_aggregate_log)
    for log_to_save in aggregate_logs: #TODO: Change to commit=false until entire program runs through?
        log_to_save.save()


def get_accessible_keys(bucket, prefix="edx-static-cloudfront"):
    accessible_keys = []
    for key in bucket.list(prefix=prefix):
        if key.storage_class != "GLACIER":
            accessible_keys.append(key)

    if DEBUG:
        print("Accessible keys len: %s" % len(accessible_keys))

    return accessible_keys


def process_keys(accessible_keys):
    num_files_processed = 0
    for key in accessible_keys:
        # Create an in-memory bytes IO buffer
        with io.BytesIO() as b:
            key.get_file(b)
            b.seek(0)
            gzf = gzip.GzipFile(None, 'rb', fileobj=b)
            file_content = gzf.read().decode('utf-8')
        # Process in-memory file
        gz_name = key.name
        if not is_in_filename_log(gz_name):
            if DEBUG:
                print("%s not found, adding!" % gz_name)
            add_to_filename_log(gz_name)
            process_log_file(file_content, gz_name)
            num_files_processed += 1
    return num_files_processed


# TODO: Get most recent date already in table, and start next search there - will save time searching

def run_command():
    conn = boto.connect_s3()
    bucket = conn.get_bucket("edx-s3-logs", validate=False)

    print("Gathering accessible keys...")
    accessible_keys = get_accessible_keys(bucket)

    print("Processing keys...")
    num_files_processed = process_keys(accessible_keys)

    print("Finished! New files processed: %s" % num_files_processed)
