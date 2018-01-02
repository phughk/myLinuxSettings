#!/usr/bin/python

import sys, os, shutil, re

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    patternsFound = 0
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                matches = re.findall(pattern, line)
                patternsFound += len(matches)
                newLine = line
                for match in matches:
                    newLine = newLine.replace(match, subst)
                new_file.write(newLine)
            if patternsFound==0:
                new_file.write(subst+"\n")
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    return patternsFound

def safeRemove(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)

def safeExtract(tarFile, targetDirectory):
    # remove target if exists
    safeRemove(targetDirectory)
    # extract tar
    customExtractLocation="customExtractLocation"
    safeRemove(customExtractLocation)
    os.makedirs(customExtractLocation)
    run('tar -xf %s -C %s' % (tarFile, customExtractLocation))
    # find the only directory in target
    extractedFile=os.listdir(customExtractLocation)[0]
    # rename to target
    move(os.path.join(customExtractLocation, extractedFile), targetDirectory)
    safeRemove(customExtractLocation)

def run(cmd):
    worked = os.system(cmd)
    if worked!=0:
        raise ValueError('Unexpected output code (%d) of command `%s`' % (worked, cmd))

def configKeyPattern(configKey):
    return "#?%s.*" % configKey

def modifyConfig(installDir, configKey, configValue):
    configFile = os.path.join(installDir, "conf", "neo4j.conf")
    replace(configFile, configKeyPattern(configKey), "%s=%s" % (configKey, configValue) )

def modifyConfigAll(installDirs, configKey, configValue):
    for installDir in installDirs:
        modifyConfig(installDir, configKey, configValue)

def modifyAllConfigInc(installDirs, configKey, configValue, incAmount):
    for item in range(0, len(installDirs)):
        installDir = installDirs[item]
        modifyConfig(installDir, configKey, configValue + (incAmount*item) )

def modifyConfigAllSetPorts(installls, configKey, baseValue, basePort):
    basePort = int(basePort)
    offset=0
    for install in installs:
        modifyConfig(install, configKey, baseValue+str(basePort+offset))
        offset+=1

def createSslKey(basename):
    if os.path.exists(basename+'.key') or os.path.exists(basename+'.csr'):
        # no need to generate
        return
    run("openssl req -newkey rsa:2048 -nodes -keyout %s.key -out %s.csr" % (basename, basename))

def installSslToAll(installs, basename):
    baseKey = basename+'.key'
    baseCert = basename+'.csr'
    policyName = 'cluster'
    for install in installs:
        certsPath = os.path.join(install, 'certificates', policyName)
        run('cp %s %s' % (baseKey, certsPath) )
        run('mv %s %s' % (os.path.join(certsPath, baseKey), os.path.join(certsPath, 'private.key')))
        run('cp %s %s' % (baseCert, certsPath) )
        run('mv %s %s' % (os.path.join(certsPath, baseCert), os.path.join(certsPath, 'public.crt')))
        run('cp %s %s' % (os.path.join(certsPath, 'public.crt'), os.path.join(certsPath, 'trusted', 'self.crt')))

def createSslPathsAll(installs, policyName):
    for install in installs:
        os.makedirs( os.path.join(install, 'certificates', policyName, 'trusted') )

def setupEncryption():
    modifyConfigAll(installs, 'dbms.connector.bolt.tls_level', 'REQUIRED')
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.base_directory', 'certificates/cluster')
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.client_auth', "REQUIRE")
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.tls_versions', 'TLSv1.2')
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.ciphers', 'TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA')
    modifyConfigAll(installs, 'causal_clustering.ssl_policy', 'cluster')
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.allow_key_generation', 'true')
    modifyConfigAll(installs, 'dbms.ssl.policy.cluster.trust_all', 'false')
    
    # Now create ssl to match expected locations
    basename = 'cluster_key'
    createSslPathsAll([installs[0]], 'cluster')
    createSslKey(basename)
    run('ln -s ../cluster-core1/certificates cluster-core2/')
    run('ln -s ../cluster-core1/certificates cluster-core3/')
    # installSslToAll(installs, basename)

tarFile = sys.argv[1]
safeExtract(tarFile, "cluster-core1")
safeExtract(tarFile, "cluster-core2")
safeExtract(tarFile, "cluster-core3")
installs = ["cluster-core1", "cluster-core2", "cluster-core3"]

# modifyAllConfig(installs, "dbms.backup.enabled", "false")
modifyConfigAll(installs, "dbms.mode", "CORE")
modifyConfigAll(installs, "causal_clustering.expected_core_cluster_size", len(installs))
modifyConfigAll(installs, "causal_clustering.initial_discovery_members", "localhost:5000,localhost:5001,localhost:5002")

modifyConfigAllSetPorts(installs, 'causal_clustering.discovery_listen_address', '0.0.0.0:', 5000)
modifyConfigAllSetPorts(installs, 'causal_clustering.transaction_listen_address', '0.0.0.0:', 6000)
modifyConfigAllSetPorts(installs, 'causal_clustering.raft_listen_address', '0.0.0.0:', 7000)
modifyConfigAllSetPorts(installs, 'dbms.connector.http.listen_address', '0.0.0.0:', 7474)
modifyConfigAllSetPorts(installs, 'dbms.connector.bolt.listen_address', '0.0.0.0:', 7687)
modifyConfigAll(installs, 'dbms.connector.https.enabled', 'false')
setupEncryption()
