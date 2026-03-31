import random

n = random.randint(0, 10**3)
n = 416

print(n)

count = 0

i = 1
while i * i <= n:
    if n % i == 0:
        if i * (i + 1) <= n:
            count += 1
        
        j = n // i
        if j != i and j * (j + 1) <= n:
            count += 1
    i += 1

print(count)