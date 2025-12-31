def exponential_averaging(alpha=0.5):
    """
    Demonstrate exponential averaging for CPU burst prediction
    """
    import numpy as np
    
    # Simulated actual burst times
    actual_bursts = [6, 4, 6, 4, 13, 13, 13]
    predicted = [10]  # Initial guess
    
    print("Exponential Averaging (α = {})".format(alpha))
    print("=" * 50)
    print(f"{'Actual':<10} {'Predicted':<10} {'Error':<10}")
    print("-" * 30)
    
    for i, actual in enumerate(actual_bursts):
        # Calculate next prediction
        next_pred = alpha * actual + (1 - alpha) * predicted[-1]
        error = abs(next_pred - actual)
        
        print(f"{actual:<10} {predicted[-1]:<10.2f} {error:<10.2f}")
        
        # For next iteration
        predicted.append(next_pred)
    
    return predicted

# Run demonstration
print("\nBurst Time Prediction using Exponential Averaging:")
exponential_averaging(alpha=0.5) 
