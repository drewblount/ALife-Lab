
import matplotlib.pyplot as plt
execfile('topWords.py')

# goal: run some topWords.multip_sh_term_vects and histogram the output

def compare(n, m):
    for is_cite in (True, False):
        multip_sh_term_vects(n, m, is_cite=is_cite, False, 1)
        
for m in (1000, 10000, 100000):
    print 'comparing children=%d' % m
    compare(20, m)
