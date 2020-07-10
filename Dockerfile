FROM ubuntu:16.04

WORKDIR /root/source

ENV DEBIAN_FRONTEND noninteractive
ENV USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends ubuntu-desktop \
    gnome-panel \
    gnome-settings-daemon \
    metacity \
    gnome-terminal \
    nautilus \
	wget \
	tar \
    ssh
	
# Install Choregraphe Suite 2.5.5.5
RUN wget -P /root/ https://community-static.aldebaran.com/resources/2.5.10/Choregraphe/choregraphe-suite-2.5.10.7-linux64-setup.run
RUN chmod +x /root/choregraphe-suite-2.5.10.7-linux64-setup.run
RUN /root/choregraphe-suite-2.5.10.7-linux64-setup.run --mode unattended --installdir /opt/Aldebaran 

# Install pynaoqi 2.5.5.5 library
RUN wget -P /root/ https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
RUN tar -xvzf /root/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz -C /root/
RUN rm /root/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
ENV LD_LIBRARY_PATH /opt/Aldebaran/lib/
ENV PYTHONPATH="/root/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages"

# Set correct python
RUN echo "alias py='/opt/Aldebaran/bin/python2.orig'" >> ~/.bashrc

