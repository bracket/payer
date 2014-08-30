from Payer.Language import *;
import Proto;
from Matcher import *;
from TypeTag import TypeTag;

__all__ = [ 'Grammar', ];

globals().update(type_tags);

# OutputNode = TypeTag('OutputNode');

# def get_outputs(term):
#     pattern = (OutputNode, var('node'), _);
#     for m, d in find(pattern, term): yield d['node'];

class GetReferences(object):
    def __init__(self): self.refs = set();

    @Proto.decorate_finder_method
    def __call__():
        r'''get_references

            get_references (Ref name) = self.refs.add(name);
        '''

def get_references(L):
    gf = GetReferences();
    gf(L);
    return gf.refs;

class Grammar(object):
    def __init__(self):
        self._raw = { };
        self._references = { };
        self._reduced = { };

    def __iter__(self):
        return self._languages.iteritems();
    
    @Proto.decorate_method
    def __getitem__():
        r'''Grammar.__getitem__

            getitem (Ref key) = self._languages[Ref(key)];
            getitem key       = self._languages[Ref(key)];
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

    # @MatcherMethod.decorate
    # def derivative(add):
    #     @add(var('c'), Ref(var('name')))
    #     def _derivative(self, c, name): return self.derivative(c, self._raw[(Ref, name)]);

    # @MatcherMethod.decorate
    # def finalize(add):
    #     @add(Ref(var('name')))
    #     def _finalize(self, name): return self.finalize(self._raw[(Ref, name)]);

    # @MatcherMethod.decorate
    # def expand_nullity_ref(add):
    #     @add(passvar('ref', Ref(_)))
    #     def _expand_nullity_ref(self, ref):
    #         out = self._nullity_cache[ref[0]];
    #         if out in _NED: return out;
    #         else: return ref[0];

    #     @add(var('L'))
    #     def _expand_nullity_ref(self, L): return L;

    # def update_nullity_cache(self):
    #     done = _NED;
    #     changed = True;

    #     while changed:
    #         changed = False;

    #         for k, L in self._nullity_cache.iteritems():
    #             if L in done: continue;

    #             M = self._nullity_cache[k] = nullity(bottom_up(self.expand_nullity_ref, L));
    #             changed = changed or (M != L);

    #     for k, L in self._nullity_cache.iteritems():
    #         if L not in done: self._nullity_cache[k] = null();

    # @MatcherMethod.decorate
    # def nullity(add):
    #     @add(Ref(var('name')))
    #     def _nullity(self, name):
    #         if self._dirty: self.update_nullity_cache();
    #         return self._nullity_cache[(Ref, name)];

    #     @add(var('L'))
    #     def _nullity(self, L): return nullity(L);
