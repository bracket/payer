from . import proto
from .language import *
from .type_tag import TypeTag
from functools import reduce
from matcher import *

__all__ = [
    'Grammar',
    'language_tags',
]

globals().update(type_tags)

language_tags = [ 'RegularLanguage', 'ContextFreeLanguage' ]
language_tags = { k : TypeTag(k) for k in language_tags }

globals().update(language_tags)

def get_references(L):
    pattern = passvar('x', Ref(var('y')))
    return { pattern.value.parent for _, _ in find(pattern, L) }


@proto.decorate
def get_name():
    r'''get_name

        get_name (Ref name) = name
    '''

def determine_finalization(languages):
    null, epsilon = Null(), Epsilon()
    done = { null, epsilon }

    remaining = { key : finalize(L) for key, L in languages.items() }
    out = {  }

    def safe_get(key):
        return out.get(key, key)

    reconstruct = Reconstruct()

    changed = True
    while changed:
        changed = False

        for key, L in list(remaining.items()):
            if L in done:
                out[key] = L
                remaining.pop(key)
                changed = True
            else:
                term = bottom_up(safe_get, L)
                term = reconstruct(term)
                remaining[key] = term

                if term != L:
                    changed = True

    for key in remaining:
        out.setdefault(key, null)

    return out


def determine_language_types(references):
    regular_language = RegularLanguage()
    regular_set = { regular_language }

    out = { key : regular_language for key, refs in references.items() if not refs }
    remaining = { key : L for key, L in references.items() if key not in out }

    changed = True

    while changed:
        changed = False

        for key, prev_types in list(remaining.items()):
            next_types = { out.get(term, term) for term in prev_types }

            if next_types == regular_set:
                out[key] = regular_language
                remaining.pop(key)
                changed = True
            elif prev_types != next_types:
                remaining[key] = next_types
                changed = True

    context_free_language = ContextFreeLanguage()

    for key in remaining:
        out.setdefault(key, context_free_language)

    return out


class Grammar(object):
    def __init__(self):
        self._raw = { }
        self._references = { }
        self._language_types = None
        self._finalized = None


    def __iter__(self):
        return self._raw.items()


    def as_dict(self):
        return { get_name(k) : v for k, v in self._raw.items() }


    @proto.decorate_method
    def __getitem__():
        r'''Grammar.__getitem__

            getitem (Ref key) = self._raw[Ref(key)]
            getitem key       = self._raw[Ref(key)]
        '''


    @MatcherMethod.decorate
    def __setitem__(add):
        @add(passvar('key', Ref(_)), var('value'))
        def setitem(self, key, value):
            key = key.parent
            self._raw[key] = value
            self._references[key] = get_references(value)

            self._language_types = None
            self._finalized = None


        @add(var('key'), var('value'))
        def setitem(self, key, value):
            self[Ref(key)] = value


    @property
    def language_types(self):
        if self._language_types is not None:
            return self._language_types

        types = self._language_types = determine_language_types(self._references)
        return types


    @property
    def finalized(self):
        if self._finalized is not None:
            return self._finalized

        finalized = self._finalized = determine_finalization(self._raw)
        return finalized


    def finalize(self, L):
        finalized = self.finalized
        valid = { Null(), Epsilon() }

        def safe_get(key):
            return finalized.get(key, key)

        out = bottom_up(safe_get, L)
        out = reconstruct(out)

        if out not in valid:
            raise RuntimeError(
                "Unable to determine finalization for language with current grammar",
                { "language" : L }
            )

        return out
