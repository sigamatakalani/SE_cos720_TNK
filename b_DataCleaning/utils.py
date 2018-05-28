import os
import sys

EVERY_COUNT_CHARACTERS = 5
AMOUNT_TO_MOVE_EVERY_CHARACTER = 4

def printList(string, list):
	output = string

	for item in list:
		output += "{"
		output += item
		output += "}, "

	output += "\n"

	print(output)

def log(string):
	# if os.name == "nt":
	# 	print(os.system("cls"))
	# else:
	# 	sys.stdout.write("\003[K")

	print(string, end="               ", flush=True)