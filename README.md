# eea.docker.arcgis2rdf

Exports ArcGIS online catalogue data into RDF files

## Dependencies

Additional libraries in use apart of the standard Python libs : rdflib and json

 * rdflib ->
    RDFLib is open source and is maintained in a GitHub repository:
    http://github.com/RDFLib/rdflib/
    RDFLib may be easy_installed:
       First is needed to install in the machine
       the easy install package at: http://pypi.python.org/pypi/setuptools
       Second run in shell:  $ easy_install rdflib
 * json ->
     This library is available sonce Python 2.6 can be found at: http://pypi.python.org/pypi/simplejson/

## How to run:
    1. Use the shell
    2. Go to the script directory (Python exported is needed)
    3. Run: python readEoEGroup_rdf.py <outputfilepath> -g "GROUPNAME"

#### The argument is:
   outputpath: Provides the full output in the server machine with the filename with extension .rdf
   e.g. "M:\ags_mxd_data\RDF\test.rdf"

#### Options
   --group, -g : It possible retrive data from sevaral groups.
        The dafault group is "European Environment Agency (Applications)"
        Avalilable groups are listed in http://eea.maps.arcgis.com/home/groups.html

#### Example
    python readEoEGroup_rdf.py retrive_data.rdf -g "GMES Services"
