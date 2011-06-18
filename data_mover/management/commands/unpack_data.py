import sys
import tempfile
import tarfile
from glob import glob
import os
import shutil
from distutils import dir_util

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
	help = 'Fixes FilePathFields whose base paths have changed.'
	args = "dump_path"

	def handle(self, dump_path, **options):
		if dump_path == '-':
			arc = tarfile.open(fileobj=sys.stdin, mode='r:gz')
		else:
			arc = tarfile.open(dump_path, mode='r:gz')
		base_path = tempfile.mkdtemp()
		arc.extractall(path=base_path)
		path = glob(os.path.join(base_path, '*'))[0]
		
		# media files
		#shutil.copytree(os.path.join(path, 'media'), settings.MEDIA_ROOT)
		dir_util.copy_tree(os.path.join(path, 'media'), settings.MEDIA_ROOT)
		
		# load db fields
		old_stdout = sys.stdout
		sys.stdout = open(os.path.join(path, 'backup_db_dump.json'), 'w')
		call_command('dumpdata', indent=4)
		sys.stdout.close()
		sys.stdout = old_stdout
		call_command('flush', noinput=True, interactive=False)
		call_command('reset', 'contenttypes', 'auth', noinput=True, interactive=False)
		call_command('loaddata', os.path.join(path, 'db_dump.json'))
		
		# rebase FilepathFields
		call_command('rebase_filepathfields', os.path.join(path, 'fpf_bases_dump.json'))
