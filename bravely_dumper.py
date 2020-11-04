from pathlib import Path
import struct
import re


# top level directory containing subfolders with script files
base = Path("A:/content0.game/romfs/common/")

# get list of all files containing text, recursively
file_list = [f for f in base.rglob('*.*') if f.name != 'index.fs']

# place output file in current script directory
cwd = Path(__file__).resolve().parent
out = Path(str(cwd) + "/test_dump.txt")

# empty the file before we start writing to it
out.open("w").close()
out = out.open("a")


def fprint(text, mode="both", fout=out):
	""" outputs text to modes: stdout, file, or both """

	if mode == 'stdout' or mode == 'both':
		print(text)
	if mode == 'file' or mode == 'both':
		out.write(str(text) + '\n')


def extract_text(src_file, loc, length):
	""" return a string of length bytes from loc in src_file """

	src_file.seek(loc, 0)
	text = src_file.read(length).decode("utf-16", "ignore")
	text = re.sub(r'\x00+', '\n', text)

	return text


def read_header(src_file, file_ptr):
	""" return dict of rel_ptr, abs_ptr, script_len
		from src_file @ file_ptr location """

	# skip first four bytes of file header
	src_file.seek(file_ptr+4*4, 0)

	# relative pointers for two text blocks and their lengths
	names_ptr, names_len, script_ptr, script_len = \
		struct.unpack("<IIII", src_file.read(16))

	return {
			"rel_ptr": script_ptr,
			"script_len": script_len,
			"abs_ptr": script_ptr+file_ptr
			}


def read_script(script_path, file_ptr=0, file_name=None):
	""" parse header and output text from script files,
		starting at file_ptr offset """
	with open(script_path, 'rb') as script_file:
		header = read_header(script_file, file_ptr)
		if header['script_len'] > 0:
			# print file path / name starting from /common/
			fprint("Script File: " + "/".join(script_path.parts[3:]))

			if file_name:
				fprint(f"internal filename: {file_name}")

			fprint(f"script_location: {header['abs_ptr']}, " +
										f"script_length: {header['script_len']}")
			fprint("==="*15)
			text = extract_text(script_file, header['abs_ptr'], header['script_len'])
			fprint(text, 'file')


def find_and_dump(script_path):
	""" dump text from file specified by Path object script_path """

	# .fs files contain many files internally, indicated by an index.fs
	if f.suffix == '.fs':
		index_path = Path(f.parents[0] / 'index.fs')

		with open(index_path, 'rb') as index_file:

			next_ptr = 1
			while(next_ptr):

				next_ptr, file_ptr, file_len, mystery = \
						struct.unpack("<IIII", index_file.read(16))

				# read to the next pointer, or end of file if no more pointers
				if next_ptr > 0:
					name_length = next_ptr - index_file.tell()
				else:
					name_length = None

				# file names are UTF-8
				file_name = index_file.read(name_length).decode()
				# trim trailing NULLs
				file_name = re.sub(r'\x00+', '', file_name)

				read_script(script_path, file_ptr, file_name)
				index_file.seek(next_ptr, 0)


	# if extension is not .fs, there's no index file to parse
	else:
		read_script(script_path)


# loop through all script files in /common/
# parse headers, find text, and output
for f in file_list:
	find_and_dump(f)
