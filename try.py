mm = {'a': {3, 4, 5, 6}, 'b': {3, 4, 5}, 'c': {8}}

ac = False
for k, v in mm.items():
    if 3 in v:
        ac = True
if ac:
    print('Found 8')