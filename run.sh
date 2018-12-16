#!/bin/bash

# Absolute path to the location of this script
WORKING_DIR=/home/quasar/projects/jeff-tcia-pubs/XML-Parser

source env/bin/activate

# These paths are all relative to the above working dir
UPLOAD_PATH=upload
TITLEINFO=titleinfo.csv
OUTPUT_HTML=Publications.html
OUTPUT_SVG=graph.svg

###############################################################################

cd $WORKING_DIR

# Select the first xml file, ignore all others
PUB_FILE=$(find $UPLOAD_PATH -type f -iname '*.xml' | head -n 1)

echo "Using EndNote file: $PUB_FILE"


echo "Updating titleinfo ($TITLEINFO)"
./update_citations_and_urls.py $PUB_FILE $TITLEINFO

echo "Generating $OUTPUT_HTML"
./make_publications.py $TITLEINFO $PUB_FILE $OUTPUT_HTML

echo "Generating $OUTPUT_SVG"
./make_graph.py $PUB_FILE $OUTPUT_SVG

echo "Update complete!"
