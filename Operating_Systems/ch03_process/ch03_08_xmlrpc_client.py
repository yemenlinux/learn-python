# xmlrpc_client.py
import xmlrpc.client

def main():
    # Connect to server
    proxy = xmlrpc.client.ServerProxy('http://localhost:8000/')
    
    try:
        # Test basic functions
        print("=== Testing Basic Functions ===")
        print(f"Current time: {proxy.get_time()}")
        print(f"5 + 3 = {proxy.add(5, 3)}")
        print(f"5 * 3 = {proxy.multiply(5, 3)}")
        
        # Test user function
        print("\n=== Testing User Function ===")
        user_info = proxy.get_user(42)
        print(f"User Info: {user_info}")
        
        # Test string functions
        print("\n=== Testing String Functions ===")
        test_string = "Hello World"
        print(f"Original: {test_string}")
        print(f"Reversed: {proxy.reverse(test_string)}")
        print(f"Uppercase: {proxy.upper(test_string)}")
        print(f"Lowercase: {proxy.lower(test_string)}")
        
        # List available methods
        print("\n=== Available Methods ===")
        methods = proxy.system.listMethods()
        for method in methods:
            print(f"- {method}")
            
    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
