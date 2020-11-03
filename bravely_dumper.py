import fugashi
from pathlib import Path
import os, sys
import struct

from pprint import pprint

tagger = fugashi.Tagger()

foo = "今日はラヌーの日だ"
zzz = tagger(foo)
bar = [word.surface for word in tagger(foo)]

def dump(obj):
	for attr in dir(obj):
		if(attr[0:2] != '__'):
			print("obj.%s = %r" % (attr, getattr(obj, attr)))

# for x in tagger(foo):
	# dump(x)

#file_list = list(Path("A:/content0.game/romfs/common/").rglob("*.fs"))
base = Path("A:/content0.game/romfs/common/")
file_list = base.rglob("*.fs")
folder_list = (sorted([*{f.parent.name for f in file_list}]))

cwd = Path(__file__).resolve().parent
out = Path(str(cwd) + "/test_dump.txt")
out.open("w").close()
out = out.open("a")

for folder in folder_list:
	print(f"{folder=}")
	out.write("==="*10 + "\n")
	out.write(f"{folder=}\n")
	idx = Path(base / folder / "index.fs")
	crowd = Path(base / folder / "crowd.fs")
	with open(idx, 'rb') as fx:
		next_ptr = struct.unpack("<I", fx.read(4))[0]
		while(next_ptr):
			print(f"{next_ptr=}")
			out.write((f"\n{next_ptr=}\n"))
			file_ptr = struct.unpack("<I", fx.read(4))[0]
			file_len = struct.unpack("<I", fx.read(4))[0]
			mystery1 = struct.unpack("<I", fx.read(4))[0]
			file_name = fx.read(next_ptr-fx.tell()-4).decode()

			print(f"{file_ptr=}, {file_name=}")
			out.write(f"{file_ptr=}, {file_name=}\n")
			with open(crowd, 'rb') as f:
				f.seek(file_ptr+6*4,0)
				script_ptr = struct.unpack("<I", f.read(4))[0]
				script_len = struct.unpack("<I", f.read(4))[0]
				print(f"{script_ptr=}, {script_len=}")
				out.write(f"{script_ptr=}, {script_len=}\n")
				f.seek(file_ptr+script_ptr, 0)
				out.write(f.read(script_len).decode("utf-16", "ignore").replace('\x00','\n'))


			fx.seek(next_ptr, 0)
			next_ptr = struct.unpack("<I", fx.read(4))[0]
