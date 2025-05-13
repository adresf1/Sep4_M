#Base Image
FROM python:3.11

#ARG DATABASE_URL
#ENV DATABASE_URL=${DATABASE_URL}

#Working directory i containeren
WORKDIR /app

#Kopier requirements
COPY requirements.txt /app/

#installer python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Kopier resten af projektet
COPY . .

#Test Suite
#WORKDIR /app/DataProcessing
#RUN pytest TestDemoDataRaw.py 

WORKDIR /app
#Åbner bash
CMD ["bash"]

