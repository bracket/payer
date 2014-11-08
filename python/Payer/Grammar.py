import Proto;
from Payer.Language import *;
from Matcher import *;
from TypeTag import TypeTag;

__all__ = [ 'Grammar', ];

globals().update(type_tags);

language_tags = [ 'RegularLanguage', 'ContextFreeLanguage' ];
language_tags = { k : TypeTag(k) for k in language_tags };
globals().update(language_tags);

class GetReferences(object):
    def __init__(self): self.refs = set();

    @Proto.decorate_finder_method
    def __call__():
        r'''get_references

            get_references (Ref name) = self.refs.add(Ref(name));
        '''

def get_references(L):
    gf = GetReferences();
    gf(L);
    return gf.refs;

@Proto.decorate
def get_name():
    r'''get_name

        get_name (Ref name) = name;
    '''

class GetFinalizes(object):
    def __init__(self): self.finalizes = set();

    @Proto.decorate_finder_method
    def __call__():
        r'''get_finalizes

            get_finalizes (Finalize l) = self.finalizes.add(l);
        '''

def get_finalizes(L):
    gf = GetFinalizes();
    gf(L);
    return gf.finalizes;

class Simplify(object):
    def __init__(self, finalizes):
        self.finalizes = finalizes;
        self.done = { null(), epsilon() };

    @Proto.decorate_method
    def __call__():
        r'''simplify

            simplify (Union xs)           = reduce(union, (self(x) for x in xs));
            simplify (Concat xs)          = reduce(concat, (self(x) for x in xs));
            simplify (Repeat l)           = repeat(self(l));
            simplify (Finalize reference) = self._simplify_finalize(reference);
            simplify x                    = x;
        '''

    def _simplify_finalize(self, reference):
        deref = self.finalizes[reference];
        if deref in self.done: return deref;
        else: return Finalize(reference);

class Grammar(object):
    def __init__(self):
        self._raw = { };
        self._references = { };

    def __iter__(self):
        return self._raw.iteritems();

    def as_dict(self):
        return { get_name(k) : v for k, v in self._raw.iteritems() };

    @Proto.decorate_method
    def __getitem__():
        r'''Grammar.__getitem__

            getitem (Ref key) = self._raw[Ref(key)];
            getitem key       = self._raw[Ref(key)];
        '''

    @MatcherMethod.decorate
    def __setitem__(add):
        @add(Ref(var('key')), var('value'))
        def _setitem(self, key, value):
            key = Ref(key);
            self._raw[key] = value;
            self._references[key] = get_references(value);

        @add(var('key'), var('value'))
        def _setitem(self, key, value):
            key = Ref(key);
            self._raw[key] = value;
            self._references[key] = get_references(value);

    def determine_language_types(self):
        regular_language = RegularLanguage();
        regular_set = { regular_language } ;

        out = { L : regular_language for L, refs in self._references.iteritems() if not refs };
        done = { L for L in out };

        remaining = dict(self._references);

        changed = True;
        while changed:
            changed = False;
            for L, prev_types in remaining.iteritems():
                if L in done: continue;
                next_types = { out.get(term, term) for term in prev_types };

                if next_types == regular_set:
                    out[L] = regular_language;
                    done.add(L);
                elif prev_types != next_types:
                    remaining[L] = next_types;
                    changed = True;

        for L in remaining.viewkeys() - done: out[L] = ContextFreeLanguage();

        return out;

    @Proto.decorate_method
    def deref():
        r'''Grammar.deref

            deref (Ref key) = self[key];
            deref x         = x;
        '''

    def expand_references(self, L):
        return top_down(self.deref, L);

    @MatcherMethod.decorate
    def regular_deref(add):
        @add(passvar('r', Ref(var('key'))))
        def regular_deref(self, r):
            return self[r.parent] if self._language_types[r.parent] == RegularLanguage() else r.parent;

        @add(var('L'))
        def regular_deref(self, L): return L;

    def expand_regular_references(self, L):
        self._language_types = self.determine_language_types();
        return top_down(self.regular_deref, L);

    @Proto.decorate_method
    def reduce(add):
        r'''reduce

            reduce (Ref name)       = self[name];
            reduce (Derivative c l) = derivative(c, self.reduce(l));
            reduce x                = x;
        '''

    def finalize(self, L):
        null, epsilon = Null(), Epsilon();
        done = { null, epsilon };

        remaining = [ L ];
        finalized = { L : finalize(self.reduce(L)) };

        while remaining:
            x = remaining.pop(0);
            for f in get_finalizes(finalized[x]):
                if f in finalized: continue;
                finalized[f] = finalize(self.reduce(f));
                remaining.append(f);

        simplify = Simplify(finalized);

        changed = True;
        while changed:
            changed = False;
            for key, f in finalized.iteritems():
                if f in done: continue;

                s = simplify(f);
                if s == f: continue;

                finalized[key] = s;
                changed = True;

        if finalized[L] == epsilon: return epsilon;
        else: return null;
