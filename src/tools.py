def traversal(c, p="root", x=None, d=0):
	if not x:
		x = {}
	for i, v in iter(c.items()):
		pName = "%s.%s"%(p, i)
		if type(v) == dict:
			x.update(traversal(v, pName, x, d+1))
		else:
			x[pName] = v
	
	if d == 0:
		x = {k.replace("root.", "").strip():v for k, v in x.items()}
	return x

# class DotAccessibleDict(dict):
# 	def __init__(self, d):
# 		for k,v in d.items():
# 			if type(v) == dict:
# 				d[k] = DotableDict(v)
# 		self._items = d
	
# 	def __getattr__(self, attr):
# 		return self.get(attr)
	
# 	def __setattr__(self, k, v):
# 		self.__setitem__(key, value)

#https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class DotAccessibleDict(dict):
	def __init__(self, *args, **kwargs):
		super(DotAccessibleDict, self).__init__(*args, **kwargs)
		for arg in args:
			if isinstance(arg, dict):
				for k, v in iter(arg.items()):
					if isinstance(v, dict):
						self[k] = DotAccessibleDict(v)
					else:
						self[k] = v
		if kwargs:
			for k, v in iter(kwargs.items()):
				if isinstance(v, dict):
					self[k] = DotAccessibleDict(v)
				else:
					self[k] = v

	def __getattr__(self, attr):
		return self.get(attr)

	def __setattr__(self, key, value):
		self.__setitem__(key, value)

	def __setitem__(self, key, value):
		super(DotAccessibleDict, self).__setitem__(key, value)
		self.__dict__.update({key: value})

	def __delattr__(self, item):
		self.__delitem__(item)

	def __delitem__(self, key):
		super(DotAccessibleDict, self).__delitem__(key)
		del self.__dict__[key]