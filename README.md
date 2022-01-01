Capstone project
=======================
This repository contains all the work done for the capstone project of BIOL59000 at Lewis University.

This work follows that of a paper published by H. Zhong, G. Loukides, and R. Gwadera found at:
https://doi.org/10.1016/j.jbi.2019.103360


clustEHR : A web application for clustering electronic health records
------------------------
With the field of biomedical informatics and translational bioinformatics growing on a daily basis, new tools are need in the efforts to generate, process, and store the large amounts of data being created around the clock, help out reseearch in the prediction of clinical outcomes whether through screening, medicine, or genetics, as well as create actionable insights for researchers and clinical practitioners alike. To assist in these efforts, a web app clustEHR was developed utilizing the MASPC algorithm for clustering electronic health records based on a subset of features, namely, demographics and diagnoses. Certain user-friendly features were developed, in particular, for this web app such that it not only removes the strong coding skills requirement in order to be able to utilize the MASPC algorithm for clustering electronic health records and opens it up to a much wider audience, but attempts to fill in some of the gaps identified by the original authors of the MASPC algorithm. In order to overcome such issues as reproducibility, this open-source web application was implemented as a containerized application using Docker, written in Python using the micro web framework Flask, and tested using two independent anonymized electronic health record datasets. Using this sort of technological stack opens up a large potentional for further modularizatoin and decoupling so that incorporating novel methodologies can be done easily.


OBTAINING THE DOCKER IMAGE
------------------------
The Docker image which contains the end product of this study is found at https://hub.docker.com/r/dominicamartinez/clustehr
which can be obtained from running the command
```
docker pull dominicamartinez/clustehr
```

BUILD
------------------------
The Dockerfile found at the root of this repository contains the build information should one want to build the Docker image manually. The Docker image can be built by running
```
docker build -t clustehr .
```
in the same directory as the Dockerfile on a local cloned repository.

RUN
------------------------
Once the Docker image is built, clustEHR can be run by issuing the following command if you built it manually using the command from the BUILD section:
```
docker run -d -p 5000:5000 clustehr
```
or
```
docker run -d -p 5000:5000 dominicamartinez/clustehr
```
if downloaded from Docker Hub with `docker pull`.

This will run the Docker container in the background. After that using http://localhost:5000 on any web browser will connect to the 
web server inside the container and should show the clustEHR UI.

TEST SETS
------------------------
There are some small test sets within the test_data directory which can be used to verify functionality of the app.
The study, however, used the following data sets to help guide the creation as more representative of the type of information
which can be obtained from EHR systems.

- https://www.healthvermont.gov/health-statistics-vital-records/health-care-systems-reporting/hospital-discharge-data
- https://sites.google.com/site/informsdataminingcontest/data/

LICENSING
----------------------------------------
Where applicable MIT licensing applies (included within the repository [LICENSE.md]).
Otherwise all rights are reserved by the authors of all source files found here that are also included found within:
https://bitbucket.org/EHR_Clustering/maspc/src/master/

Comments and Questions
----------------------
Dominic Martinez
dominicamartinez@lewisu.edu
