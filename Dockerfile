FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install --no-install-recommends -y \
  bash-completion \
  && rm -rf /var/lib/apt/lists/*
RUN echo 'source /usr/share/bash-completion/bash_completion' >> /etc/bash.bashrc

RUN cd /etc/bash_completion.d/ \
  && curl -SLO https://rawgit.com/django/django/stable/1.9.x/extras/django_bash_completion

RUN echo 'export HISTFILE=$HOME/.bash_history/history' >> $HOME/.bashrc

WORKDIR /app
COPY requirements requirements
RUN pip install --no-cache-dir -r requirements/local.txt && rm -rf /root/.cache
RUN pip install --no-cache-dir ipython && rm -rf /root/.cache

ARG TINI_VERSION
RUN curl -SL \
  https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini \
  -o /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
