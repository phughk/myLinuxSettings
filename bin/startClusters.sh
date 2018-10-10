#/bin/sh

find . -path "**/bin/neo4j" | xargs -I {} sh -c "{} start"
