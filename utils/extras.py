import random

def generate_matric_numbers(prefix, start_number, end_number):
    matric_numbers = []
    for i in range(start_number, end_number + 1):
        matric_no = f"{prefix}/24/{i:04d}"
        matric_numbers.append(matric_no)
    return matric_numbers

prefix = "CSC"  # Example prefix for Computer Science department
start_number = 1
end_number = 700
matric_numbers = generate_matric_numbers(prefix, start_number, end_number)

# Shuffle the list to randomize the matric numbers
random.shuffle(matric_numbers)

# Print the generated matric numbers
for matric_no in matric_numbers:
    print(matric_no)
