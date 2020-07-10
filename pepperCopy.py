import sys
import io
from os import listdir
from os.path import isfile, join
from paramiko import SSHClient
from scp import SCPClient

if len(sys.argv) < 2:
    print("Usage: python peppercopy.py nao@<IP>")
    sys.exit()


ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect(hostname=sys.argv[1], username="nao", password="pepper")

files = [f for f in listdir("source/") if isfile(join("source/", f))]

with SCPClient(ssh.get_transport()) as scp:
    for f in files:
        scp.put("source/"+f, "source/"+f)


