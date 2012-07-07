from ADT import Type, Matcher, _;
import Memo;


memo = Memo.SharedMemo();

class TriBool(Type): pass;

@memo
@TriBool
def True_(): return ();

@memo
@TriBool
def Maybe_(): return ();

@memo
@TriBool
def False_(): return ();

@Matcher
def and_(add):
	@add(False_(), _)
	def f(): return False_();

	@add(_, False_())
	def f(): return False_();

	@add(True_(), True_())
	def f(): return True_();

	@add(_, _)
	def f(): return Maybe_();

@Matcher
def or_(add):
	@add(True_(), _)
	def f(): return True_();

	@add(_, True_())
	def f(): return True_();

	@add(False_(), False_())
	def f(): return False_();

	@add(_, _)
	def f(): return Maybe_();

@Matcher
def to_bool(add):
	@add(True_())
	def f(): return True;

	@add(False_())
	def f(): return False;
