from python:3
COPY . /opt
WORKDIR /opt
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "-u", "guppy.py" ]
