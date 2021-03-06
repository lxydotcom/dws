FROM ubuntu:14.04
MAINTAINER Adam Lee <lijla02@ca.com>

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

RUN apt-get update \
    && apt-get purge -y -force-yes \
        vim-tiny \
    && apt-get install -y --force-yes --no-install-recommends \
        python python-mysqldb cron curl \
        wget supervisor ca-certificates \
        openssh-server pwgen sudo vim net-tools \
    && apt-get autoclean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* 

# Install other softwares
#RUN wget -qO- https://get.docker.com/ | sh
# Install Docker client only
RUN arch=`[ "\`getconf LONG_BIT\`" -eq "64" ] && echo "x86_64" || echo "i386"`; wget -nv -O /usr/bin/docker https://get.docker.com/builds/Linux/${arch}/docker-latest && chmod a+x /usr/bin/docker

# Configure 

# docker host for docker client/daemon/swarm
ENV DOCKER_HOST tcp://dockerhost:2374

# delivery script directory
ENV DELIVERY_ROOT_PATH /dws/delivery/

# add supervisor configuration file
ADD supervisord.conf /etc/supervisor/


############ Enable SSH daemon
RUN mkdir /var/run/sshd
RUN echo 'root:interOP@123' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
############

EXPOSE 22
WORKDIR /root

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
