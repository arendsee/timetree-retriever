#!/usr/bin/env python3

import argparse
import httplib2
import sys
import re

__version__ = '0.0'
__prog__ = 'timetree-retriever'

URL = 'http://www.timetree.org/index.php?taxon_a=%s&taxon_b=%s&submit=Search'

def parser(argv=None):
    parser = argparse.ArgumentParser(
        prog=__prog__,
        usage="%s [options] <inputfile>" % __prog__,
        description="Retrieves divergence times from TimeTree"
    )
    parser.add_argument(
        '--version',
        help='Display version',
        action='version',
        version='%(prog)s {}'.format(__version__)
    )
    parser.add_argument(
        '-f', '--input',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='The taxon id of the ancestral node'
    )
    parser.add_argument(
        '--cache',
        help="Cache directory name",
    )
    parser.add_argument(
        '--print_http',
        help="Print all HTTP request",
        action="store_true",
        default=False
    )
    args = parser.parse_args(argv)
    return(args)

def prettyprint_http(response):
    d = dict(response.items())
    for k,v in d.items():
        print("\t%s: %s" % (k,v), file=sys.stderr)

if __name__ == '__main__':

    args = parser()

    if args.print_http:
        httplib2.debuglevel = 1

    h = httplib2.Http(args.cache)

    if args.print_http:
        prettyprint_http(response)

    for line in args.input:
        line = re.sub(' ', '+', line.strip())
        row = line.split('\t')
        url = URL % (row[0], row[1])
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
        taxon_a = re.sub('\\+', '_', row[0])
        taxon_b = re.sub('\\+', '_', row[1])
        out = '\t'.join((taxon_a, taxon_b, mean, median, expert))
        print(out)
