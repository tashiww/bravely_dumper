from pathlib import Path
import struct
import re


# top level directory containing subfolders with script files
base = Path("A:/content0.game/romfs/common/")
file_list = [f for f in base.rglob('*.*') if f.name != 'index.fs']

# place output file in current script directory
cwd = Path(__file__).resolve().parent
out = Path(str(cwd) + "/test_dump.txt")

# empty the file before we start writing to it
out.open("w").close()
out = out.open("a")


def fprint(text, mode="both", fout=out):
	""" outputs text to mode: stdout, file, or both """

	if mode == 'stdout' or mode == 'both':
		print(text)
	if mode == 'file' or mode == 'both':
		out.write(str(text) + '\n')


def extract_text(src_file, loc, length):
	""" return a string: length bytes from loc in src_file with enc encoding """

	src_file.seek(loc, 0)
	text = src_file.read(length).decode("utf-16", "ignore")
	text = re.sub(r'\x00+', '\n', text)
	return text


def read_header(src_file, file_ptr):
	""" return rel_ptr, abs_ptr, script_len from src_file @ file_ptr location """
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


def find_and_dump(script_path):
	""" dump text from all files in file_list """

	fprint("==="*15)
	if f.suffix == '.fs':
		index_path = Path(f.parents[0] / 'index.fs')

		with open(index_path, 'rb') as index_file:

			next_ptr = struct.unpack("<I", index_file.read(4))[0]

			while(True):

				file_ptr, file_len, mystery = struct.unpack("<III", index_file.read(12))
				if next_ptr > 0:
					name_length = next_ptr - index_file.tell()
				else:
					name_length = None
				file_name = index_file.read(name_length).decode()
				file_name = re.sub(r'\x00+', '', file_name)

				with open(script_path, 'rb') as script_file:
					header = read_header(script_file, file_ptr)
					if header['script_len'] > 0:
						fprint("Script File: " + "/".join(script_path.parts[3:]))
						fprint(f"{file_ptr=}, {file_name=}")
						fprint(f"{header['abs_ptr']=}, {header['script_len']=}")
						fprint("==="*15)
						text = extract_text(script_file, header['abs_ptr'], header['script_len'])
						fprint(text, 'file')

				index_file.seek(next_ptr, 0)

				if next_ptr == 0:
					break
				next_ptr = struct.unpack("<I", index_file.read(4))[0]

	else:
		with open(script_path, 'rb') as script_file:
			header = read_header(script_file, 0)
			if header['script_len'] > 0:
				fprint("Script File: " + "/".join(script_path.parts[3:]))
				fprint(f"{header['abs_ptr']=}, {header['script_len']=}")
				fprint("==="*15)
				text = extract_text(script_file, header['abs_ptr'], header['script_len'])
				fprint(text, 'file')


for f in file_list:
	find_and_dump(f)
