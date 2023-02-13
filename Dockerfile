FROM python:3.11
MAINTAINER ainis
RUN apt install git
RUN apt install bash
EXPOSE 8898
RUN pip install fastapi
RUN pip install requests
RUN pip install uvicorn
RUN adduser --disabled-password --gecos "" deploy2022user
ADD print_hello /bin
RUN chmod 777 /bin/print_hello
USER deploy2022user
ADD fastapi_app.py /bin
ADD README.md /
CMD uvicorn bin.fastapi_app:app --host 0.0.0.0 --port 8898