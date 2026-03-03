import os
import numpy as np

# 1. Create the 'data' folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# 2. Create a fake array with 100 random numbers
fake_array = np.random.rand(100)

# 3. Save it exactly where our FastAPI server is looking
np.save("data/leakage_results.npy", fake_array)

print("✅ Fake data created successfully inside the 'data' folder!")