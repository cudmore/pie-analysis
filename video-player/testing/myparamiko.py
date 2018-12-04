from paramiko import SSHClient
from scp import SCPClient
import sys

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('example.com')

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

# SCPCLient takes a paramiko transport and progress callback as its arguments.
scp = SCPClient(ssh.get_transport(), progress=progress)

# you can also use progress4, which adds a 4th parameter to track IP and port
# useful with multiple threads to track source
def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s\'s progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )
scp = SCPClient(ssh.get_transport(), progress4=progress4)

scp.put('test.txt', '~/test.txt')
# Should now be printing the current progress of your put function.

scp.close()