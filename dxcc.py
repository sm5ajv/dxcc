# dxcc.py
from __future__ import print_function
# import sys
import argparse
import logging
import re


class Dxcc:
    dxcc = {}
    prefixes = {}

    def __init__(self):
        self.read_cty()

    def read_cty(self):
        cty_file = open('cty.dat')
        main_prefix = ''
        while True:
            line = cty_file.readline()
            if not line:
                break
            if line[0:1] != ' ':
                line = line.rstrip()
                line = line.split(':')
                main_prefix = line[7].strip()
                self.dxcc[main_prefix] = list(map(str.strip, line[0:7]))
            else:
                line = line.strip()
                line = line.rstrip(';')
                line = line.rstrip(',')
                line = line.split(',')
                if main_prefix in self.prefixes:
                    pfx = list(map(str.strip, line))
                    for p in pfx:
                        self.prefixes[main_prefix].append(p)
                else:
                    self.prefixes[main_prefix] = list(map(str.strip, line))

    def dxcc_info(self, call):
        if len(call) == 0:
            return '', ''
        test_call = call
        test_call = test_call.upper()
        match_chars = 0
        match_prefix = ''
        match_dxcc = ''
        for main_prefix in self.dxcc:
            for test in self.prefixes[main_prefix]:
                length = len(test)
                test_itu = ''
                test_waz = ''
                ix = 0
                if (length > 5) and ((test.find('(') > -1) or (test.find('[') > -1)):
                    ix1 = test.find('(')
                    ix2 = test.find('[')
                    if ix1 > 0 and ix2 > 0:
                        ix = min([ix1, ix2])
                        test_waz = test[ix1 + 1: test.find(')')]
                        test_itu = test[ix2 + 1: test.find(']')]
                    elif ix1 < 0 < ix2:
                        ix = ix2
                        test_itu = test[ix2 + 1: test.find(']')]
                    elif ix2 < 0 < ix1:
                        ix = ix1
                        test_waz = test[ix1 + 1: test.find(')')]
                    try:
                        test = test[0:ix]
                        length = len(test)
                    except Exception as e:
                        logging.exception(e)
                        logging.error('Bad ix! ix =', ix, ' ix1=', ix1, ' ix2=', ix2)

                if test[0] == '=':
                    test = test[1:]
                    length = len(test)
                if (test_call[0:length] == test[0:length]) and (match_chars <= length):
                    match_chars = length
                    match_prefix = main_prefix
                    match_dxcc = self.dxcc[main_prefix]
                    if len(test_waz) > 0:
                        match_dxcc[1] = test_waz
                    if len(test_itu) > 0:
                        match_dxcc[2] = test_itu
        if len(match_prefix) > 0:
            return match_prefix, match_dxcc
        else:
            return '', ''


def is_hamradio(call):
    regex_all = '[A-Z0-9]{1,3}[0123456789][A-Z0-9]{0,3}[A-Z]'
    regex_non_us = '\b(?!K)(?!N)(?!W)(?!A[A-L])[A-Z0-9][A-Z0-9]?[A-Z0-9]?[' \
                   '0123456789][A-Z0-9][A-Z0-9]?[A-Z0-9]?[A-Z0-9]?\b '
    regex_us = '[AKNW[A-Z]{0,2}[0123456789][A-Z]{1,3}'

    regular = re.findall(regex_all, call.upper())
    non_us = re.findall(regex_non_us, call.upper())
    us = re.findall(regex_us, call.upper())
    if regular or non_us or us:
        return True
    else:
        return False


def main(callsigns):
    dxcc = Dxcc()

    for call in callsigns:
        if is_hamradio(call):
            print(call, dxcc.dxcc_info(call))
        else:
            print(call, ('INVALID', []))


# for k in range(1, len(sys.argv)):
#     call = sys.argv[k]
#     if is_hamradio(call):
#         print(call, dxcc.dxcc_info(call))
#     else:
#         print(call, ('INVALID', []))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    #parser.add_argument("callsigns", type=str, help="One or several calls, separated by space")
    parser.add_argument('-c', '--callsigns', nargs='+', help='One or several calls, separated by space', required=True)
    args = parser.parse_args()
    calls = args.callsigns

    main(calls)
