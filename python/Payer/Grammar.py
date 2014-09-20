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

@Proto.decorate
def get_name():
    r'''get_name

        get_name (Ref name) = name;
    '''

class Grammar(object):
    def __init__(self):
        self._raw = { };
        self._references = { };
        self._reduced = { };

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

    @Proto.decorate_method
    def deref():
        r'''Grammar.deref

            deref (Ref key) = self[key];
            deref x         = x;
        '''

    def expand_references(self, L):
        return top_down(self.deref, L);
    
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

    # @MatcherMethod.decorate
    # def nullity(add):
    #     @add(Ref(var('name')))
    #     def _nullity(self, name):
    #         if self._dirty: self.update_nullity_cache();
    #         return self._nullity_cache[(Ref, name)];

    #     @add(var('L'))
    #     def _nullity(self, L): return nullity(L);
