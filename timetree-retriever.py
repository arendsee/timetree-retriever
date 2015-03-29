#!/usr/bin/env python3

import argparse
import httplib2
import sys
import re
import time

__version__ = '0.0'
__prog__ = 'timetree-retriever'

URL = 'http://www.timetree.org/index.php?taxon_a=%s&taxon_b=%s&submit=Search'

def parser(argv=None):
    parser = argparse.ArgumentParser(
        prog=__prog__,
        usage="%s [options] <taxon_a> <taxon_b>" % __prog__,
        description="retrieves divergence times from TimeTree"
    )
    parser.add_argument(
        '--version',
        help='display version',
        action='version',
        version='%(prog)s {}'.format(__version__)
    )
    parser.add_argument(
        'taxa',
        nargs='*',
        help='two input taxa with "+" substituted for spaces'
    )
    parser.add_argument(
        '-f', '--file-input',
        type=argparse.FileType('r'),
        help='TAB-delimited file containing input taxa'
    )
    parser.add_argument(
        '-d', '--header',
        help='print header',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '-s', '--sleep',
        help="politely wait N seconds between downloads",
        metavar="N",
        type=int,
        default=0
    )
    parser.add_argument(
        '--cache',
        help="cache directory name",
    )
    parser.add_argument(
        '--print_http',
        help="print all HTTP request",
        action="store_true",
        default=False
    )
    args = parser.parse_args(argv)
    return(args)

def prettyprint_http(response):
    d = dict(response.items())
    for k,v in d.items():
        print("\t%s: %s" % (k,v), file=sys.stderr)

def retrieve(taxon_a, taxon_b):
    url = URL % (taxon_a, taxon_b)
    response, content = h.request(url)
    if args.print_http:
        prettyprint_http(response)
    res = re.sub('\n', '', content.decode())
    mean, median, expert = '-', '-', '-'
    for tr in re.findall('<tr.*?</tr', res):
        try:
            age = re.search('(\d+\.\d*) Mya', tr).groups()[0]
            if '>Mean:<' in tr:
                mean = age
            elif '>Median:<' in tr:
                median = age
            elif '>Expert Result:<' in tr:
                expert = age
        except AttributeError:
            pass
    taxon_a = re.sub('\\+', '_', taxon_a)
    taxon_b = re.sub('\\+', '_', taxon_b)
    out = '\t'.join((taxon_a, taxon_b, mean, median, expert))
    return(out)

if __name__ == '__main__':

    args = parser()

    if args.print_http:
        httplib2.debuglevel = 1

    h = httplib2.Http(args.cache)

    if args.print_http:
        prettyprint_http(response)

    header = '\t'.join(('taxon_a', 'taxon_b', 'mean', 'median', 'expert'))
    if args.file_input:
        is_first = True
        for line in args.file_input:
            line = re.sub('[ _]', '+', line.strip())
            row = line.split('\t')
            out = retrieve(row[0], row[1])
            if is_first and args.header:
                print(header, file=sys.stdout)
                is_first = False
            print(out, file=sys.stdout)
            sys.stdout.flush()
            time.sleep(args.sleep)
    elif args.taxa:
        if len(args.taxa) == 2:
            taxon_a, taxon_b = args.taxa
            print(header, file=sys.stdout)
            print(retrieve(taxon_a, taxon_b), file=sys.stdout)
        else:
            print("You must provide two taxa with NO SPACES", file=sys.stderr)
