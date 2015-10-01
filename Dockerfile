FROM python:2.7
MAINTAINER Antonio De Marinis <demarinis@eea.europa.eu>

# install setuptools/easy_install and rdflib
RUN wget https://bootstrap.pypa.io/ez_setup.py -O - | python \
    && easy_install rdflib

RUN mkdir /opt/arcgis2rdf && \
    mkdir /var/local/arcgis2rdf

WORKDIR /opt/arcgis2rdf

ADD readEoEGroup_rdf.py ./

ENV ARCGIS_FILEPATH /var/local/arcgis2rdf/arcgis_data.rdf
ENV ARCGIS_GROUP="European Environment Agency (Applications)"

VOLUME ["/var/local/arcgis2rdf"]

CMD ./readEoEGroup_rdf.py $ARCGIS_FILEPATH -g "${ARCGIS_GROUP}"
