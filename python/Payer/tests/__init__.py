# from Payer.Language import *;
# 
# __all__ = [ 'assertRecognizes' ]
# 
# def assertRecognizes(self, language, string):
#     n, e = null(), epsilon();
#     for x in string:
#         language = derivative(ord(x), language);
#         self.assertNotEquals(language, n);
#     self.assertEquals(finalize(language), e);
