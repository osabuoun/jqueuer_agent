from __future__ import absolute_import, unicode_literals
import time, shlex, subprocess, random, sys, os

from container_worker import job_app
import container_worker as jqw
import monitoring
import celery
from celery.exceptions import Reject
from celery.result import AsyncResult

print("Job Operations - Started")

class JQueuer_Task(celery.Task):
	'''
	def on_success(self, retval, task_id, args, kwargs):
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
		res = AsyncResult(task_id)
		
		print('{0!r} succeeded: {1!r}: {2!r}'.format(task_id, str(res.ready()),retval))
		#sys.exit(1)
		#self.update_state(state='FAILURE', meta={'exc': exc}), 'task_id': task_id, 'args': args, 'kwargs': kwargs, 'einfo': einfo})
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
		print("*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*")
	'''
	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
		print('{0!r} failed: {1!r}'.format(task_id, exc))
		#sys.exit(1)
		#self.update_state(state='FAILURE', meta={'exc': exc}), 'task_id': task_id, 'args': args, 'kwargs': kwargs, 'einfo': einfo})
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
		print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")

index = 0
container_dead = False
@job_app.task(bind=True,acks_late=True, track_started=True, base=JQueuer_Task) # 
def add(self, exp_id, job_queue_id, job):
	print("+++++++++++++++++++ First ++++++++++++++++++++++++")
	print(self.AsyncResult(self.request.id).state)
	print("++++++++++++++++++++++++++++++++++++++++++++++++++")
	global index, container_dead
	if (container_dead):
		time.sleep(30) 
		raise Reject('my container is dead', requeue=True)
	index = index +1
	job_params  = job['params']
	job_command 	= job['command']
	job_start_time = time.time()
	output = ""

	worker_id = self.request.hostname.split("@")[1]
	#node_id, service_name, container_id  = worker_id.split("##")

	monitoring.run_job(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id)

	#log_file =  "./log/" + self.request.hostname + ".log"
	log_file =  "./" + worker_id + ".log"

	with open(log_file, "a") as myfile:
		myfile.write("node_id: " + getNodeID(worker_id) + "\n") 
		myfile.write("worker_id: " + worker_id + "\n") 
		myfile.write("New Queue Job: " + job_queue_id + "\n") 
		myfile.write("Command: " + str(job['command']) + "\n")
		myfile.write("Parameters: " + str(len(job_params)) + "\n")
		tasks = job['tasks']
		try:
			if (isinstance(tasks, list)):
				print("Tasks : There is a List of " + str(len(tasks)))
				output = process_list(worker_id, exp_id, job_queue_id, job, myfile, job_start_time)
			else:
				output = process_array(worker_id, exp_id, job_queue_id, job, myfile, job_start_time)
				print("Tasks : There is an array of " + str(tasks['count']))
			print("......................................................")
			print(worker_id + " has finished the job " + job_queue_id + " - " + exp_id)
			monitoring.terminate_job(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)

		except subprocess.CalledProcessError as e:
			monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
			print("/////////////////////  Exception 1 in worker ///////////////////////// - " + str(index))
			#print(str(e))
			#print("/////////////////////////////////////////////////////")
			container_dead = True
			#raise Reject(e, requeue=True)
			self.update_state(state='RETRY')
			print("+++++++++++++++++++ Failed ++++++++++++++++++++++++")
			print(self.AsyncResult(self.request.id).state)
			print("++++++++++++++++++++++++++++++++++++++++++++++++++")
			time.sleep(200)
			print("I' killing the process since my container is dead :(")
			#time.sleep(10)
			#sys.exit(0)
		'''
		except Exception as e:
	#		monitoring.task_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task_id, task_start_time)
			monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
			print("/////////////////////  Exception 2 in worker /////////////////////////" + str(index))
			#print(str(e))
			#print("/////////////////////////////////////////////////////")
			try:
				raise Reject(e, requeue=True)
			except Exception as e:
				pass
		'''
		return output

def getNodeID(worker_id):
	return worker_id.split("##")[0]

def getServiceName(worker_id):
	return worker_id.split("##")[1]

def getContainerID(worker_id):
	return worker_id.split("##")[2]

def process_list(worker_id, exp_id, job_queue_id, job, myfile, job_start_time):
	output = ""
#	try:
	for task in job['tasks']:
		print("-------------------------------------\n")
		print("Task: " + str(task) + "\n")
		try:
			task_command = task['command'] 
		except Exception as e:
			task['command'] = job['command']
		try:
			task_data = task['data'] 
		except Exception as e:
			tasks['data'] = job['data']
	
		task_start_time = time.time()
		monitoring.run_task(getNodeID(worker_id), exp_id,getServiceName(worker_id), worker_id, job_queue_id, task["id"])

		command = ['docker','exec', getContainerID(worker_id)] + task_command + task["data"] + [str(worker_id)]
		output = subprocess.check_output(command)
		monitoring.terminate_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task["id"], task_start_time)
	'''
	except subprocess.CalledProcessError as e:
		monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
		print("//////////////////// List /////////////////////////////")
		print(str(e))
		print("/////////////////////////////////////////////////////")
		raise Reject(e, requeue=True)
		print("I' killing the process since my container is dead :(")
		sys.exit(0)
	except Exception as e:
#		monitoring.task_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task["id"], task_start_time)
		monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
		print("//////////////////// List ///////////////////////////")
		print(str(e))
		print("/////////////////////////////////////////////////////")
		raise Reject(e, requeue=True)
	'''
	myfile.write("output: " + str(output) + "\n")
	print(worker_id + " - Output: " + str(output))
	return output

def process_array(worker_id, exp_id, job_queue_id, job, myfile, job_start_time):
	output = ""
	tasks = job['tasks']
	try:
		task_command = tasks['command'] 
	except Exception as e:
		tasks['command'] = job['command']
	try:
		task_data = tasks['data'] 
	except Exception as e:
		tasks['data'] = job['data']

	myfile.write("Task: " + str(tasks) + "\n")
#	try:
	for x in range(0,tasks['count']):
		myfile.write("-------------------------------------\n")
		task_start_time = time.time()
		task_id = tasks["id"] + "_" + str(x)
		monitoring.run_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task_id)
		command = ['docker','exec', getContainerID(worker_id)] + tasks['command'] + [str(tasks["data"]) + [str(worker_id)]]
		print(worker_id + " - Running Task : " + str(command))
		output = subprocess.check_output(command)
		monitoring.terminate_task(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task_id , task_start_time)
	'''	
	except subprocess.CalledProcessError as e:
		monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
		print("///////////////////// Array //////////////////////////")
		print(str(e))
		print("/////////////////////////////////////////////////////")
		raise Reject(e, requeue=True)
		print("I' killing the process since my container is dead :(")
		sys.exit(0)
	except Exception as e:
#		monitoring.task_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, task_id, task_start_time)
		monitoring.job_failed(getNodeID(worker_id), exp_id, getServiceName(worker_id), worker_id, job_queue_id, job_start_time)
		print("///////////////////// Array /////////////////////////")
		print(str(e))
		print("/////////////////////////////////////////////////////")
		raise Reject(e, requeue=True)
	'''
	myfile.write("output: " + str(output) + "\n")
	print(worker_id + " - Output: " + str(output))
	return output


