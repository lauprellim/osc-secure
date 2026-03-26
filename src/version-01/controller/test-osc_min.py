'''
test to see if osc_min supports floats and can generate valid OSC
payload bytes

output should be a byte string like:

b'/test\x00\x00\x00,if\x00\x00\x00\x00*?\x00\x00\x00'



'''

from osc_min import osc_pack

msg = osc_pack('/test', ',if', (42, 0.5))
print(msg)
