import os

# Define the directory containing the files
directory = "web/backend/preprocessing/lyrics"

# Check each file in the range from 0 to 5000
for i in range(11173):  # up to and including 5000
    filename = f"{i}.txt"
    filepath = os.path.join(directory, filename)

    # Check if the file exists
    if not os.path.exists(filepath):
        # If the file does not exist, create an empty file
        open(filepath, 'a').close()
        print(f"Created empty file: {filename}")
    else:
        print(f"File exists: {filename}")

print("Process completed.")
