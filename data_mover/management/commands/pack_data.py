""" Packs all data needed to move a full Django project between machines

dumps the database
dumps the bases of filepathfields
packs up all media (user uploads)

ouput is a tar.gz stream to stdout


Usage:

python manage.py pack_data > my_data_pack.tar.gz

Unpack with unpack_data
"""
import sys
import tempfile
import shutil
import tarfile
import datetime

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# from http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

class Command(BaseCommand):
	help = "Dumps all the data needed to move a full Django project between machines"
	args = "[appname ...]"

	def handle(self, *args, **options):
		if 'exclude' in options:
			if not args:
				args = settings.INSTALLED_APPS
			args = list(set(args) - set(options['exclude'].split(',')))
		# get temp dir
		timestamp = datetime.datetime.now().isoformat()
		path = os.path.join(tempfile.mkdtemp(), timestamp)
		mkdir_p(path)
		# dump db
		with open(os.path.join(path, 'db_dump.json'), 'w') as db_dump_file:
			old_stdout = sys.stdout
			sys.stdout = db_dump_file
			call_command('dumpdata', *args, indent=4)
		
		# dump filepathfields' bases
		with open(os.path.join(path, 'fpf_bases_dump.json'), 'w') as fpf_bases_dump_file:
			sys.stdout = fpf_bases_dump_file
			call_command('dumpbase_filepathfields', *args)
		
		sys.stdout = old_stdout
		
		# copy media
		shutil.copytree(settings.MEDIA_ROOT, os.path.join(path, 'media'))
		
		# pack
		dump_file, dump_file_path = tempfile.mkstemp('.tar.gz')
		arc = tarfile.open(dump_file_path, mode='w:gz')
		arc.add(path, arcname=timestamp)
		arc.close()
		
		#output
		shutil.copyfileobj(open(dump_file_path), sys.stdout)
