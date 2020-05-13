FROM kbase/sdkbase2:python
MAINTAINER michael.t.shaffer@colostate.edu
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# Install miniconda
RUN apt-get update && \
    apt-get install wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    sh Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda
# Add miniconda bin to path permanently in the container
ENV PATH=/root/miniconda/bin:$PATH
# Set up conda
RUN echo $(which conda) && \
    conda config --set always_yes yes && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda update conda
# Install dependencies and DRAM
RUN conda install pandas scikit-bio prodigal "mmseqs2!=10.6d92c" hmmer "trnascan-se >=2" sqlalchemy barrnap "altair >=4" openpyxl networkx ruby parallel wget nose coverage && \
    pip install DRAM-bio jsonrpcbase
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
