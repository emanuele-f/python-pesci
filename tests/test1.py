# Assigment and print
x = 4
print x

# Reassignment
x = 5
print x, "\n", 2

# Arithmetic operators
y = 4
x *= (6+4) * (y)
print x

z = [x,y]
x, y = [9, 8]
# Function member call
z.append(9)

# If test
if x>2<0 or not y>0:
    y = 20
print z,y

# Function definition
def square(x, z=5, l="6", *args, **kargs):
    global y

    # Global variable assignment
    y = 10

    print x, z, l, args, kargs
    return x*x

# Own function call
print square(5, 8, *z, p=6, k=1)
print y

# dict
d = {"name":"??"}
print d
