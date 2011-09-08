#!/usr/bin/env python

"""Plot the performance for different block sizes of one function across
variants.
"""

import libplot

import pylab
import pdb
import math

def pretty_kb(v):
    if v < 1024:
        return '%d' % v
    else:
        if v % 1024 == 0:
            return '%d k' % (v//1024)
        else:
            return '%.1f k' % (v/1024)

def plot(records, function, alignment=None):
    variants = libplot.unique(records, 'variant', prefer='this')
    records = [x for x in records if x.function==function]

    if alignment != None:
        records = [x for x in records if x.alignment==alignment]

    alignments = libplot.unique(records, 'alignment')
    assert len(alignments) == 1
    aalignment = alignments[0]

    bytes = libplot.unique(records, 'bytes')[0]

    colours = iter('bgrcmyk')
    all_x = []

    pylab.figure(1).set_size_inches((16, 12))
    pylab.clf()

    if 'str' in function:
        # The harness fills out to 16k.  Anything past that is an
        # early match
        top = 16384
    else:
        top = 2**31

    for variant in variants:
        matches = [x for x in records if x.variant==variant and x.bytes <= top]
        matches.sort(key=lambda x: x.bytes)

        X = [x.bytes for x in matches]
        Y = [x.bytes*x.loops/x.elapsed/(1024*1024) for x in matches]

        all_x.extend(X)
        colour = colours.next()

        if X:
            pylab.plot(X, Y, c=colour)
            pylab.scatter(X, Y, c=colour, label=variant, edgecolors='none')

    pylab.legend(loc='upper left', ncol=3)
    pylab.grid()
    pylab.title('%(function)s of %(aalignment)s byte aligned blocks' % locals())
    pylab.xlabel('Size (B)')
    pylab.ylabel('Rate (MB/s)')

    # Figure out how high the range goes
    top = max(all_x)

    power = int(round(math.log(max(all_x)) / math.log(2)))

    pylab.semilogx()

    pylab.axes().set_xticks([2**x for x in range(0, power+1)])
    pylab.axes().set_xticklabels([pretty_kb(2**x) for x in range(0, power+1)])
    pylab.xlim(0, top)
    pylab.ylim(0, pylab.ylim()[1])

def main():
    records = libplot.parse()

    functions = libplot.unique(records, 'function')
    alignments = libplot.unique(records, 'alignment')

    for function in functions:
        for alignment in alignments:
            plot(records, function, alignment)
            pylab.savefig('sizes-%s-%02d.png' % (function, alignment), dpi=72)

    pylab.show()

if __name__ == '__main__':
    main()

