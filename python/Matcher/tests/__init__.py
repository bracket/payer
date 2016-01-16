from Matcher import  *;

__all__ = [ 'assertMatches' ];

def assertMatches(self, pattern, value):
    # TODO: Print out trace of failure when match fails
    self.assertTrue(match(pattern, value));
