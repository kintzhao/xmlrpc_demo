#https://docs.python.org/2/library/simplexmlrpcserver.html#
import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://192.168.1.232:8001')
print(s.pow(2,3))  # Returns 2**3 = 8
print(s.add(2,3))  # Returns 5
print(s.mul(5,2))  # Returns 5*2 = 10
print(s.fullName('kint'))   
print(s.fullName('zhao'))   
# Print list of available methods
print(s.system.listMethods())
