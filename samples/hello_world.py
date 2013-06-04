'''Hello or World - Enter 'Hello', 'World' to get 1, 2 as a response, or
anything else to see unrecognized input'''

import os, sys;
sys.path.append(os.path.abspath('../python'));

from Payer.Language import *;

def make_word_recognizer(word):
    return reduce(concat, (terminals([ord(x)]) for x in word));

def main():
    hello, world = map(make_word_recognizer, ('Hello', 'World'));
    L = union(output(1, hello), output(2, world));
    space = LanguageSpace();

    string = raw_input('>>> ');
    for x in string: L = space.derivative(ord(x), L);

    outputs = list(get_outputs(space.finalize(L)));
    if outputs: print '\n'.join(str(out.value) for out in outputs);
    else: print 'Unrecognized input';

if __name__ == '__main__':
    main();
