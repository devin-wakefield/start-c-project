#!/usr/bin/python
# Copywrite 2015 Devin Wakefield
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Devin Wakefield's GitHub: https://github.com/vladDrakul



"""How to Use the C Project Starter!

The purpose of this project is to help you quickly and easily set up function definitions and a Makefile without stabbing your neighbors in frustration as you forget semi-colons all over the place. 
No, I haven't done that yet, and I don't want to. Hence, this project.

Usage:
	start_C_project [filename.json]

filename.json:
	You provide this json file. It defines your function definitions, how many files you need, which go into .h files, and which go into .c files.
	You start with an array of objects. Each object in this array defines a C file.
	Attributes to a file object:
		-name: This tells us what the name of your file is. 
			Ex: "name" : "tree"
		-private: This is an array of each function definition that will only be in the .c file.
			Ex: "private" : ["int make_node(int data)", "int delete_node_r(struct node *root, int data)"]
			Notice you don't need semi-colons in there. Of course, you can include them anyway, thanks to the magic of ";;" having no effect.
		-public: This is an array of each function definition that will be in the .h file.
			Ex: "public" : ["int insert(int data)", "int delete_tree(struct tree *tree)"]
		-dependencies: This is an array of each #include you want to have at the beginning of your file.
			Ex: "dependencies" : ["<stdlib.h>", "tree.h"]
			Note that if you want to have #include <[something.h]> with the pointy braces ("<, >") then include them. If you want #include "something.h" with quotation marks instead, don't include pointies.
			Also, a .c file will automatically #include its own .h file, unless it doesn't have one, but you can include it anyway if you want. I don't care.


This python* script will (hopefully) output all the .h and .c files you need to start, as well as a basic Makefile all set to use. 
This tool is intended for starting things up quickly, without having to switch between several files just to get the basic layout set up. 
Hopefully, you will also focus more on WHAT you want this program to do, and HOW it will happen instead of rolling your eyes (and getting dizzy and then pasing out) from each syntatical error with which you garnish your code.
I hope you will have less "What the fuck did I forget this time" and more "Oh, but what if I had this helper function to make this easier, and this feature to do blah blah?? Awesome!"
Good luck!

*Yes, python, not C, because a) why not, b) who cares, and c) because I would need this to write it in C in the first place. Duh.
"""


import json
import os.path
import sys
import getopt


#This basically makes sure that filename is actually a file, and then opens it with json
def read_json(filename):
	assert os.path.isfile(filename)
	with open(filename) as data_file:
		data = json.load(data_file)
		return data

#This takes in a file json object (as described in readme) and makes the appropriate .h file.
def write_h_file(data):
	fname = data["name"] + ".h"
	
	#if public is empty, then do not make .h file.
	if len(data["public"]) != 0:
		with open(fname, 'a') as h_file:

			#write #includes to file
			incl = "#include "
			for dep in data["dependencies"]:
				line = incl + (dep if dep[0] == '<' else "\"" + dep + "\"") + "\n"
				h_file.write(line)

			h_file.write("\n\n")

			#write the function definitions to the file
			for func_def in data["public"]:
				line = func_def + ";\n" #hahaha the whole point of this
				h_file.write(line)

			h_file.write("\n")

	return

#Write a .c file from a json file object (as described in readme).
def write_c_file(data):
	fname = data["name"] + ".c"

	with open(fname, 'a') as c_file:

		#all dependencies for the .c file should be in the .h file. This then includes that IF we actually made a .h file. 
		if len(data["public"]) !=0:
			incl = "#include \"" + data["name"] + ".h\"" + "\n"
			c_file.write(incl)
		else:
			#since there was no .h file, dependencies have to be put in here. I'm not assuming there are no dependencies, because main.c might need stdio.h, for example
			incl = "#include "
			for dep in data["dependencies"]:
				line = incl + (dep if dep[0] == '<' else "\""  + dep + "\"") + "\n"
				c_file.write(line)

		c_file.write("\n\n")

		#write the function definitions
		for func_def in data["private"]:
			line = func_def + ";\n" #yayyyy I don't have to do it now :)
			c_file.write(line)

		c_file.write("\n")

	return

#on implementation, it could be more efficient to build the makefile string while writing the .h and .c files. 
#However, I'll have to implement it separately anyway if I want to have the option of JUST making a makefile... I think I want that? will decide later.
def write_makefile(data):
	with open("Makefile", 'a') as makefile:
		#write flags, like CC = gcc or w/e
		makeObj = data["Makefile"]
		for key in makeObj:
			line = key + " = " + makeObj[key] + "\n"
			makefile.write(line)

		files = data["files"]
		deps = {}
		for a_file in files:
			make_deps = []
			for elt in a_file["dependencies"]:
				if elt[0] != '<':
					make_deps.append(elt)

			deps[a_file["name"]] = make_deps
		
		#doing this manually because it's a little different...
		object_names = reduce(lambda x, y: x + " " + y + ".o", deps.keys(), "")
		default = "\ndefault: " + object_names + "\n\t$(CC) $(CFLAGS) -o $(TARGET) " + object_names + "\n\n"
		makefile.write(default)

		for dep in deps:
			line = dep + ".o: " + reduce(lambda x, y: x + " " + y[:-1] + "o", deps[dep], "") + "\n"
			line += "\t$(CC) $(CFLAGS) -c " + dep + ".c\n\n"
			makefile.write(line)

		clean = "clean: \n\t$(RM) main *.o *~\n"
		makefile.write(clean)

#			CC_line = "CC = " + makeObj["CC"] + "\n"
#			makefile.write(CC_line)
#
#			c_flags = "CFLAGS = " makeObj["CFLAGS"] + "\n"
#			makefile.write(c_flags)
#
#			target = "TARGET = " makeObj["TARGET"] + "\n"
#			makefile.write(target)


	return

#basically directs traffic of the program. 
def setup_project(json_filename):
	data = read_json(json_filename)
	files = data["files"]
	for a_file in files:
		write_h_file(a_file)
		write_c_file(a_file)

	write_makefile(data)

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def process(arg):
	setup_project(arg)

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "h", ["help"])
			#process options (there's only 1 legal one)
			for o, a in opts:
				#print help
				if o in ("-h", "--help"):
					print __doc__
					sys.exit(0)

			# process arguments (again, only 1 legal one atm)
			for arg in args:
				process(arg) 
		except getopt.error, msg:
			raise Usage(msg)

	# more code, unchanged
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
