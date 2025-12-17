# race_condition_bank.py
import threading
import time
import random

class UnsafeBankAccount:
    """Bank account without synchronization - prone to race conditions"""
    def __init__(self, initial_balance=1000):
        self.balance = initial_balance
    
    def deposit(self, amount):
        """Deposit money - not thread-safe"""
        print(f"Thread {threading.current_thread().name} depositing ${amount}")
        # Simulate some processing time
        time.sleep(random.uniform(0.001, 0.005))
        
        # Read-modify-write: This is not atomic!
        new_balance = self.balance + amount
        time.sleep(0.001)  # Simulate context switch opportunity
        self.balance = new_balance
        
        print(f"  After deposit: ${self.balance}")
    
    def withdraw(self, amount):
        """Withdraw money - not thread-safe"""
        print(f"Thread {threading.current_thread().name} withdrawing ${amount}")
        
        # Check balance
        if self.balance >= amount:
            # Simulate some processing time
            time.sleep(random.uniform(0.001, 0.005))
            
            # Read-modify-write: This is not atomic!
            new_balance = self.balance - amount
            time.sleep(0.001)  # Simulate context switch opportunity
            self.balance = new_balance
            
            print(f"  After withdrawal: ${self.balance}")
            return True
        else:
            print(f"  Insufficient funds! Balance: ${self.balance}")
            return False

def perform_transactions(account, num_deposits, num_withdrawals):
    """Perform random transactions on the account"""
    for _ in range(num_deposits):
        amount = random.randint(50, 200)
        # amount = 50
        account.deposit(amount)
    
    for _ in range(num_withdrawals):
        amount = random.randint(50, 200)
        # amount = 50
        account.withdraw(amount)

def bank_race_condition():
    """Demonstrate race condition in bank account"""
    print("=== BANK ACCOUNT RACE CONDITION ===")
    print("Starting balance: $1000")
    print("Expected final balance: $1000 (deposits and withdrawals cancel out)")
    print()
    
    account = UnsafeBankAccount(1000)
    
    # Create threads that will cause race conditions
    threads = []
    
    # Each thread does 50 deposits and 50 withdrawals
    for i in range(5):
        thread = threading.Thread(
            target=perform_transactions,
            args=(account, 50, 50),
            name=f"Customer-{i}"
        )
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"\nFinal balance: ${account.balance}")
    print(f"Expected balance: $1000")
    print(f"Difference: ${account.balance - 1000}")
    
    if account.balance != 1000:
        print("\n⚠️  RACE CONDITION DETECTED! Balance is incorrect.")
    else:
        print("\n✅ No race condition (got lucky with timing).")
    
    return account.balance

if __name__ == "__main__":
    # Run multiple times to see different outcomes
    for run in range(3):
        print(f"\n{'='*60}")
        print(f"RUN {run + 1}")
        print(f"{'='*60}")
        bank_race_condition()
        time.sleep(1) 
