FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

ADD ./ /tmp/asm3
WORKDIR /tmp/asm3/

RUN apt-get update && apt-get install -y make 

RUN make deps
RUN make all
RUN make dist

RUN cd ./install/deb

RUN ./makedeb.sh

RUN dpkg -i sheltermanager3_`cat ../../VERSION`_all.deb

CMD service sheltermanager3 start && tail -f /var/log/sheltermanager3.log
