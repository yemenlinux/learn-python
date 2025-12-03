# xmlrpc_server.py
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import datetime

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('./RPC2',)

# Create server
server = SimpleXMLRPCServer(('localhost', 8000))
server.register_introspection_functions()

# Register functions
def current_time():
    return datetime.datetime.now().isoformat()

def add_numbers(x, y):
    return x + y

def multiply_numbers(x, y):
    return x * y

def get_user_info(user_id):
    return {
        'id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com',
        'created': datetime.datetime.now().isoformat()
    }

server.register_function(current_time, 'get_time')
server.register_function(add_numbers, 'add')
server.register_function(multiply_numbers, 'multiply')
server.register_function(get_user_info, 'get_user')

# Register an instance with methods
class StringFunctions:
    def reverse(self, text):
        return text[::-1]
    
    def upper(self, text):
        return text.upper()
    
    def lower(self, text):
        return text.lower()

server.register_instance(StringFunctions())

print("XML-RPC Server running on http://localhost:8000")
print("Press Ctrl+C to stop the server")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server...")
