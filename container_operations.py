from __future__ import absolute_import, unicode_literals
from pprint import pprint
from threading import Thread
import time, sys
import shlex, subprocess

from jqueuing_manager import jqueuing_app, node_id
import monitoring

print("I'm starting the Container Operations")

job_workers = []

def worker(container):
	# Arguments you give on command line
	print("---------------------- worker_main ----------------------")
	monitoring.add_worker(node_id, container["service_name"])
	output = subprocess.check_output(['python3','jqueuing_worker.py', str(node_id) ,str(container)])
	monitoring.terminate_worker(node_id, service_name)
	print(output)
	print("---------------------- worker_main End ----------------------")

@jqueuing_app.task
def add(container):
	print("**************************************")
	print(container)
	job_worker_thread = Thread(target = worker, args = (container,))
	job_worker_thread.start()
	job_workers.append(job_worker_thread)
	print("**************Back from worker ************")
