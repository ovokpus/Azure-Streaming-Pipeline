# Azure Functions host (runtime 4.x) running the Python v2 app in function_app.py.
FROM mcr.microsoft.com/azure-functions/python:4-python3.12
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
COPY . /home/site/wwwroot
