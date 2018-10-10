#!/usr/bin/python

import sys
import os
import shutil
import re

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove


def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    patternsFound = 0
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                matches = re.findall(pattern, line)
                patternsFound += len(matches)
                newLine = line
                for match in matches:
                    newLine = newLine.replace(match, subst)
                new_file.write(newLine)
            if patternsFound == 0:
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
    customExtractLocation = "customExtractLocation"
    safeRemove(customExtractLocation)
    os.makedirs(customExtractLocation)
    run('tar -xf %s -C %s' % (tarFile, customExtractLocation))
    # find the only directory in target
    extractedFile = os.listdir(customExtractLocation)[0]
    # rename to target
    move(os.path.join(customExtractLocation, extractedFile), targetDirectory)
    safeRemove(customExtractLocation)


def run(cmd):
    worked = os.system(cmd)
    if worked != 0:
        raise ValueError(
            'Unexpected output code (%d) of command `%s`' % (worked, cmd))


def configKeyPattern(configKey):
    return "#?%s.*" % configKey


def modifyConfig(installDir, configKey, configValue):
    configFile = os.path.join(installDir, "conf", "neo4j.conf")
    replace(configFile, configKeyPattern(configKey),
            "%s=%s" % (configKey, configValue))


def modifyConfigAll(installDirs, configKey, configValue):
    for installDir in installDirs:
        modifyConfig(installDir, configKey, configValue)


def modifyAllConfigInc(installDirs, configKey, configValue, incAmount):
    for item in range(0, len(installDirs)):
        installDir = installDirs[item]
        modifyConfig(installDir, configKey, configValue + (incAmount*item))


def modifyConfigAllSetPorts(installls, configKey, baseValue, basePort):
    basePort = int(basePort)
    offset = 0
    for install in installs:
        modifyConfig(install, configKey, baseValue+str(basePort+offset))
        offset += 1


def installSslToAll(installs, basename):
    policyName = 'cluster'
    for index in range(0, len(installs)):
        install = installs[index]
        certsPath = os.path.join(install, 'certificates', policyName)

        privateKey = os.path.join(certsPath, "private.key")
        publicKey = os.path.join(certsPath, "public.crt")
        # Create the keys with public already in trusted directory
        createSslKeyPair(privateKey, publicKey)
        # Copy trusted public key to other installs
        for targetInstall in installs:
            dstKeyName = "public."+str(index)+".crt"
            targetPath = os.path.join(
                targetInstall, "certificates", policyName, "trusted", dstKeyName)
            print "TARGET PATH IS: "+targetPath
            run("cp %s %s" % (publicKey, targetPath))


def createSslPathsAll(installs, policyName):
    for install in installs:
        allowed = os.path.join(install, 'certificates', policyName, 'trusted')
        revoked = os.path.join(install, "certificates", policyName, "revoked")
        os.makedirs(allowed)
        os.makedirs(revoked)


def createSslKeyPair(privateKey, publicKey):
    COUNTRY = "UK"
    STATE = "London"
    LOCATION = "London"
    ORG = "Neo4j"
    UNIT = "Backup Orgnisation Unit"
    COMMON = "127.0.0.1"
    SETUP = "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s" % (
        COUNTRY, STATE, LOCATION, ORG, UNIT, COMMON)

    cmd = "openssl req -newkey rsa:4096 -nodes -sha512 -x509 -days 3650 -nodes -out %s -keyout %s -subj \"%s\"" % (
        publicKey, privateKey, SETUP)
    print "Command is: "+cmd
    run(cmd)


def setupEncryption():
    policyName = "cluster"
    basePolicySetting = "dbms.ssl.policy."+policyName
    modifyConfigAll(installs, 'causal_clustering.ssl_policy', policyName)
    modifyConfigAll(
        installs, basePolicySetting+'.base_directory', 'certificates/'+policyName)
    modifyConfigAll(installs, basePolicySetting+'.client_auth', "REQUIRE")
    modifyConfigAll(
        installs, basePolicySetting+'.tls_versions', 'TLSv1.2')
    modifyConfigAll(installs, basePolicySetting+'.ciphers',
                    'TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA')
    modifyConfigAll(
        installs, basePolicySetting+'.allow_key_generation', 'false')
    modifyConfigAll(installs, basePolicySetting+'.trust_all', 'false')

    # Now create ssl to match expected locations
    basename = 'cluster_key'
    createSslPathsAll(installs, 'cluster')
    installSslToAll(installs, basename)


def useDefaultCreds(installs):
    for install in installs:
        cmd = os.path.join(install, "bin/neo4j-admin")
        run(cmd+" set-initial-password neo4j")


def enableClusters(installs):
    DISCOVERY_START = 5000
    TRANSACTION_START = 6000
    RAFT_START = 7000
    cores = filter(lambda x: x.find("core") > -1, installs)
    replicas = filter(lambda x: x.find("replica") > -1, installs)
    modifyConfigAll(cores, "dbms.mode", "CORE")
    modifyConfigAll(replicas, "dbms.mode", "READ_REPLICA")
    modifyConfigAll(
        installs, "causal_clustering.expected_core_cluster_size", len(cores))
    modifyConfigAll(installs, "causal_clustering.initial_discovery_members",
                    "localhost:5000,localhost:5001,localhost:5002")
    modifyConfigAllSetPorts(
        installs, 'causal_clustering.discovery_listen_address', '0.0.0.0:', DISCOVERY_START)
    modifyConfigAllSetPorts(
        installs, 'causal_clustering.transaction_listen_address', '0.0.0.0:', TRANSACTION_START)
    modifyConfigAllSetPorts(
        installs, 'causal_clustering.raft_listen_address', '0.0.0.0:', RAFT_START)


BOLT_START = 7697
HTTP_START = 7474
HTTPS_START = 7484
BKUP_START = 6362

tarFile = sys.argv[1]
installs = ["cluster-core1", "cluster-core2", "cluster-core3",
            "cluster-replica1", "cluster-replica2", "cluster-replica3"]

for install in installs:
    safeExtract(tarFile, install)

modifyConfigAllSetPorts(
    installs, 'dbms.connector.bolt.listen_address', '0.0.0.0:', BOLT_START)
modifyConfigAllSetPorts(
    installs, 'dbms.connector.http.listen_address', '0.0.0.0:', HTTP_START)
modifyConfigAllSetPorts(
    installs, 'dbms.connector.https.listen_address', '0.0.0.0:', HTTPS_START)
enableClusters(installs)

modifyConfigAllSetPorts(
    installs, 'dbms.backup.address', '0.0.0.0:', BKUP_START)
modifyConfigAll(installs, 'dbms.connector.https.enabled', 'true')
modifyConfigAll(installs, 'causal_clustering.raft_messages_log_enable', 'true')
modifyConfigAll(installs, 'dbms.logs.debug.level', 'DEBUG')
modifyConfigAll(
    installs, 'dbms.security.causal_clustering_status_auth_enabled', 'false')
modifyConfigAll(installs, 'dbms.tx_log.rotation.retention_policy', '10 files')
modifyConfigAll(installs, 'dbms.tx_log.rotation.size', '1M')
modifyConfigAll(installs, "causal_clustering.multi_dc_license", "true")


# modifyConfig(installs[0], 'causal_clustering.refuse_to_be_leader', 'true')
# modifyConfigAll(installs, "causal_clustering.enable_pre_voting", "true")
# setupEncryption()

useDefaultCreds(installs)
