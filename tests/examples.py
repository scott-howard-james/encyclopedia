from encyclopedia import Dictionary

fruit = Dictionary({'apple':'red', 'blueberry':'blue'})
assert fruit == {'apple': 'red', 'blueberry': 'blue'}

colors = Dictionary({'red':'FF0000', 'blue':'0000FF', 'green':'00FF00'})
assert fruit * colors == Dictionary({'apple': 'FF0000', 'blueberry': '0000FF'})



from encyclopedia import Record
characteristics = Record({
    'name':str,
    'age':int})

Dog = characteristics.instance
fido = Dog()
fido['age']='2'
assert fido['age']==2

try:
    fido['street']='something'
    assert False
except:
    pass


def no_name(x=None):
    return 'UNKNOWN' if x is None else str(x)

Named = Record({
    'name':no_name,
    'age':int},
    autopopulate=True).instance

someone = Named()
assert someone['name']=='UNKNOWN'
