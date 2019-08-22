import os

dir_path = os.getcwd()

for dirpath, dirnames, filenames in os.walk(dir_path):
	for dirname in dirnames:
		for dirpath_inner, dirnames_inner, inner_files in os.walk(dirname):
			for file in inner_files:
				if "part01" in file or "part001" in file:
					os.system("7z x \"{}/{}\" -psnahp -aos".format(dirpath_inner, file))
