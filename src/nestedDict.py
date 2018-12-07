
### https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value
def nested_set(dic, keys, value):
	for key in keys[:-1]:
		dic = dic.setdefault(key, {})
	dic[keys[-1]] = value


if __name__ == "__main__":
	d = {"a":{"test":1}}
	nested_set(d, ["a", "b", "c"], 3)
# 	print(d)