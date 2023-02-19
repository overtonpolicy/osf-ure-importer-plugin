#!/usr/bin/env python

"""
Pandoc filter to convert definition lists to bullet
lists with the defined terms in strong emphasis (for
compatibility with standard markdown).
"""

from pandocfilters import toJSONFilter, BulletList, Para, Strong



def tobullet(term, defs):
    return([Para([Strong(term)])] + [b for d in defs for b in d])

def deflists(key, value, format, meta):
    import sys
    #print(key, file=sys.stderr)
    if key == 'OrderedList':
        for t in value:            
            print(f"\n:{t}", file=sys.stderr)
        #if value[0][1]['t'] in ('LowerAlpha', 'LowerRoman', ):
        #    value[0][1]['t'] = 'Decimal'

        #return BulletList([tobullet(t, d) for [t, d] in value])


if __name__ == "__main__":
    toJSONFilter(deflists)