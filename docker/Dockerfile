#Base Image
FROM python:3.11

#Working directory i containeren
WORKDIR /app

#Kopier requirements
COPY requirements.txt /app/

#installer python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Kopier resten af projektet
COPY . .

#Test
RUN  python -m pytest ./DataProcessing/tests/ > test.txt

#Åbner bash
CMD ["bash"]

