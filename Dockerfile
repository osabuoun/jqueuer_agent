FROM python:3
ADD requirements.txt /jqueuing_manager/requirements.txt
ADD job_operations.py /jqueuing_manager/job_operations.py
ADD jqueuing_worker.py /jqueuing_manager/jqueuing_worker.py
ADD container_feeder.py /jqueuing_manager/container_feeder.py
ADD container_operations.py /jqueuing_manager/container_operations.py
ADD monitoring.py /jqueuing_manager/monitoring.py
ADD jqueuing_manager.py /jqueuing_manager/jqueuing_manager.py
ADD config /jqueuing_manager/config
ADD data /jqueuing_manager/data
WORKDIR /jqueuing_manager/
RUN mkdir log
RUN pip install -r requirements.txt
RUN pip install -U "celery[redis]"
ENTRYPOINT python3 jqueuing_manager.py
