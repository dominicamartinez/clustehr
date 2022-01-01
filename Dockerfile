FROM openjdk:11.0.4-jre-slim-buster
COPY --from=python:3.8-slim-buster / / 

# GCC is needed for optimal binning module dependencies
RUN apt-get update && apt-get install -y gcc

# copy list of necessary python modules and install them
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# Not necessary now but removal of gcc would be recommended for security reasons
# for example, in a production deployment of this tool
RUN apt-get --purge remove -y gcc

COPY src /app
COPY bin/spmf.jar /app
WORKDIR /app

COPY bin/startup.sh /sbin/
RUN chmod +x /sbin/startup.sh

ENTRYPOINT ["/sbin/startup.sh"]
