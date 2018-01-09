FROM python:3
ADD requirements.txt /jqueuing_manager/requirements.txt
ADD job_operations.py /jqueuing_manager/job_operations.py
ADD jqueuing_worker.py /jqueuing_manager/jqueuing_worker.py
ADD container_feeder.py /jqueuing_manager/container_feeder.py
ADD container_operations.py /jqueuing_manager/container_operations.py
ADD monitoring.py /jqueuing_manager/monitoring.py
ADD jqueuing_manager.py /jqueuing_manager/jqueuing_manager.py
ADD parameters.py /jqueuing_manager/parameters.py
WORKDIR /jqueuing_manager/
RUN mkdir log
RUN mkdir data
RUN pip3 install -r requirements.txt
RUN pip3 install -U "celery[redis]"
ENV NODE_ID=noname 
ENTRYPOINT python3 jqueuing_manager.py $NODE_ID