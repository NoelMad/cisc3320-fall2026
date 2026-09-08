#HW1: Process Inspection Script

#Import the os module
import os

#Print PID and PPID
print(os.getpid())
print(os.getppid())

#Loop over os.environ
for key, value in os.environ.items():
    print(f"{key}={value}")

#List /proc/self/fd
try:
  os.listdir('/proc/self/fd')
except Exception as e:
  print(e)

#Wrap it in a main guard
try:
   print(os.listdir('/proc/self/fd'))
except Exception as e:
   print(e)

if __name__== "__main__":
  pass
