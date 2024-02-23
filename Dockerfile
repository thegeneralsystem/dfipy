FROM python:3.11
SHELL ["/bin/bash", "-c"]

WORKDIR /home/dev
COPY . /home/dev

RUN source dfi-api.env
RUN source tests.env

RUN apt update && apt install awscli -y

RUN pip install --upgrade pip && pip3 install poetry poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt --with dev
RUN pip3 install -e .
RUN pip3 install -r requirements.txt

RUN groupadd -r developers && useradd -r -g developers dev
RUN usermod -m -d /home/dev dev
RUN chown -R dev /home/dev
USER dev

CMD ["/bin/bash"]
