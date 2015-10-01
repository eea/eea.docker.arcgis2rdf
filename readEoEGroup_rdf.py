#! /usr/bin/env python

# Additional libraries in use apart of the standard Python libs : rdflib and json
# rdflib ->
#    RDFLib is open source and is maintained in a GitHub repository:
#    http://github.com/RDFLib/rdflib/
#    RDFLib may be easy_installed:
#       First is needed to install in the machine
#       the easy install package at: http://pypi.python.org/pypi/setuptools
#       Second run in shell:  $ easy_install rdflib
# json ->
#     This library is available sonce Python 2.6 can be found at: http://pypi.python.org/pypi/simplejson/
# How to run:
#    1. Use the shell
#    2. Go to the script directory (Python exported is needed)
#    3. Run: python readEoEGroup_rdf.py <outputfilepath> -g GROUPNAME
#
# The argument is:
#   outputpath: Provides the full output in the server machine with the filename with extension .rdf
#   e.g. "M:\ags_mxd_data\RDF\test.rdf"
############################################

from rdflib import Namespace, BNode, Literal, URIRef
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
import json
from datetime import datetime
from optparse import OptionParser
import httplib, urllib, string, os, sys, re

#http://www.arcgis.com/sharing/rest/community/groups

#q=Redlands
#
# {
#   "query": "<query>",
#   "total": total number of results returned,
#   "start": start number,
#   "num": number in result set,
#   "nextStart": -1,
#   "results": [{
#     "id": "<group id>",
#     "title": "<group title>",
#     "isInvitationOnly": true | false,
#     "owner": "<group owner username>",
#     "description": "<description>",
#     "snippet": "<summary>",
#     "tags": [
#       "<tag1>",
#       "<tag2>",
#       "<tag3>"
#     ],
#     "phone": "<contact>",
#     "thumbnail": file name,
#     "created": date created shown in UNIX time,
#     "access": "private | org | public "
#    }]
#  }


httpurl = "eea.maps.arcgis.com"
GROUPNAME = "European Environment Agency (Applications)"


def groupSearch(httpurl,groupName):
    params={}
    url = 'http://' + httpurl + "/sharing/rest/community/groups"
    params['f'] = 'json'
    #params['token']=self.token
    params['q']=groupName

    URL = url + "?" + urllib.urlencode(params)
    myJsonText = urllib.urlopen(URL).read()
    jsonresult = json.loads(myJsonText)
    # give JSON object back
    return jsonresult

#
# http://www.arcgis.com/sharing/rest/content/groups/4774c1c2b79046f285b2e86e5a20319
# http://www.arcgis.com/apidocs/rest/

def groupContent(httpurl,groupId):
    params={}

    url = 'http://' + httpurl + '/sharing/search'

    q='( group:' + groupId + ') '
    q += 'AND ((type:"service" -type:"globe" -type:"geodata" -type:"Service Definition") '
    q += 'OR type:"KML" OR type:"WMS" OR type:"Web Map" OR type:"web mapping application" '
    q += 'OR (type:"feature collection"  -type:"Feature Collection Template") '
    q += 'OR type:"mobile application")'

    params['q'] = q
    params['num']='10000'
    params['sortField']='modified'
    params['sortOrder']='desc'
    params['f'] = 'json'

    URL = url + "?" + urllib.urlencode(params)
    myJsonText = urllib.urlopen(URL).read()
    jsonresult = json.loads(myJsonText)

    # give JSON object back
    return jsonresult


def striphtml(text):
    p = re.compile(r'<.*?>')
    return p.sub('', text)


def generaterdf(outputfile, groupName):
    # find the groups based on the name of the group.
    myList = groupSearch(httpurl,groupName)
    # take the first group's id
    groupId = myList['results'][0]['id']
    print groupId


    # Find all items in one group.
    myList = groupContent(httpurl,groupId)

    # REsult
    print "total records : %s" % myList['total']
    print "start record  : %s" % myList['start']
    print "num record  : %s" % myList['num']
    print "next start record  : %s" % myList['nextStart']

    #
    # The following fields are returned.
    #itemType, culture, owner, guid, screenshots, id, size, appCategories, access, avgRating, title, numRatings, numComments, snippet,
    #listed, largeThumbnail, type, thumbnail, uploaded, industries, description, tags, typeKeywords, extent, banner, properties, name,
    #licenseInfo, languages, url, lastModified, documentation, modified, spatialReference, item, numViews, accessInformation

    graph = Graph()
    store = IOMemory()

    dmNs = Namespace('http://' + httpurl + "/rdfschema.rdf#")
    dctNs = Namespace("http://purl.org/dc/terms/")
    rdfsNs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    g = ConjunctiveGraph(store=store)
    g.bind("dm", dmNs)
    g.bind("dct", dctNs)
    g.bind("rdfs", rdfsNs)

    for obj in myList['results']:
        print obj['title'] +  ' -> ' + obj['id']

        subject = URIRef('http://discomap.eea.europa.eu/map/EEABasicviewer/?appid=' + obj['id'])
        tmpgraph = Graph(store=store, identifier=subject)
        tmpgraph.add((subject, dctNs['id'], Literal(obj['id'])))
        tmpgraph.add((subject, rdfsNs['label'], Literal(obj['title'])))
        tmpgraph.add((subject, dmNs['type'], Literal(obj['itemType'])))

        if 'url' in obj and obj['url']:
            tmpgraph.add((subject, dmNs['serviceURL'], URIRef(obj['url'])))

        if 'description' in obj and obj['description']:
            description = ' '.join(striphtml(obj['description']).split())
            description = re.sub(u"(\u2018|\u2019)", "'", description)
            tmpgraph.add((subject, dctNs['description'], Literal(description)))

        if obj.get("uploaded","") != "":
            # remove timezone from timestamp
            timestamp = int(str(obj['uploaded'])[:-3])
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            tmpgraph.add((subject, dctNs['created'], Literal(date)))
            tmpgraph.add((subject, dctNs['issued'], Literal(date)))

        if obj.get("title","") != "":
            tmpgraph.add((subject, dctNs['title'], Literal(obj['title'])))

        if obj.get("owner","") != "":
            tmpgraph.add((subject, dctNs['creator'], Literal(obj['owner'])))

        if obj.get("tags","") != "":
            for keyword in obj['tags']:
                tmpgraph.add((subject, dctNs['subject'], Literal(keyword.strip())))

        #also "Comments", "Subject", "Category", "Credits"


    outRDF = os.path.join(outputfile)
    RDFFile = open(outRDF,"w")
    RDFFile.writelines(g.serialize())
    RDFFile.close()


def usage(prog):
    print >> sys.stderr, "Usage: %s <outputfile> [-g GroupName]" % prog
    sys.exit(1)


def main():
    parser = OptionParser(usage="usage: %prog [options] <outputfile>")
    parser.add_option("-g", "--group", dest="groupName",
        default=GROUPNAME)

    options, arguments = parser.parse_args()

    if len(arguments) != 1:
        usage(sys.argv[0])

    try:
        # program's main code here
        generaterdf(arguments[0], options.groupName)
    except:
        # error handling code here
        print "error..."
        return 1  # exit on error
    else:
        print "RDF produced successfully"
        return 0  # exit errorlessly


if __name__ == '__main__':
    main()

