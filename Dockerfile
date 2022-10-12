FROM kbase/sdkbase2:python
MAINTAINER rory.flynn@colostate.edu
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# Install miniconda
RUN apt-get update && \
    apt-get install wget -q && \
    wget -nv https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    sh Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda
# Add miniconda bin to path permanently in the container
ENV PATH=/root/miniconda/bin:$PATH
# Set up conda
RUN echo $(which conda) && \
    conda config --set always_yes yes && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge
# Install dependencies and DRAM
# install from conda
#TODO add
# install from pip
#TODO add
# install from github
RUN conda install -q pandas scikit-bio "scipy==1.8.1"
RUN conda install -q pandas prodigal "mmseqs2!=10.6d92c" "hmmer!=3.3.1" "trnascan-se >=2" sqlalchemy barrnap "altair >=4" openpyxl networkx ruby parallel wget nose coverage pyyaml git
RUN python -c "exec(\"from skbio.io import read as read_sequence\")"
RUN pip install -q jsonrpcbase
# try 2
RUN git clone https://github.com/WrightonLabCSU/DRAM.git
RUN cd DRAM && git pull
RUN pip install ./DRAM
RUN echo $(cat ./DRAM/)
RUN echo $(cat ./DRAM/mag_annotator/__init__.py)
RUN rm /data/__READY__
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
