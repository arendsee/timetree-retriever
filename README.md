# TimeTree Retriever

This script is designed to automate the retrieval of divergence times between
taxa from TimeTree (http://www.timetree.org/). Unfortunately, they do not
provide a REST interface. So here is a dirty little script that bypasses the
horrors of their GUI. To this end I download the entire HTML page for each
query and parse out the single datum of interest.
