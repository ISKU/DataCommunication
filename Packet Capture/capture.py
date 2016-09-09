import socket
import struct
import sys

socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x003))

def hex2ip(ip):
	integer_ip = int(ip, 16)
	ip1 = integer_ip >> 24
	ip2 = (integer_ip & 0x00ff0000) >> 16
	ip3 = (integer_ip & 0x0000ff00) >> 8
	ip4 = integer_ip & 0xff
	return "%d.%d.%d.%d" % (ip1, ip2, ip3, ip4)

def hex2mac(mac):
	mac1 = mac[0:2]
	mac2 = mac[2:4]
	mac3 = mac[4:6]
	mac4 = mac[6:8]
	mac5 = mac[8:10]
	mac6 = mac[10:12]
	return "%s:%s:%s:%s:%s:%s" % (mac1, mac2, mac3, mac4, mac5, mac6)

for frame in range(1, int(sys.argv[1])+1):
	print "\n\n========================================================"
	print " Frame %d" % (frame)
	print "========================================================"

	packet = socket.recvfrom(4096)

	ethernet_header = struct.unpack("!6s6s2s", packet[0][0:14])
	dst_ethernet = ethernet_header[0].encode('hex')
	src_ethernet = ethernet_header[1].encode('hex')
	type_ethernet = "0x" + ethernet_header[2].encode('hex')
	print "* Ethernet II"
	print "	Destination MAC Address:", hex2mac(dst_ethernet)
	print "	Source MAC Address:", hex2mac(src_ethernet)
	print "	Type:", type_ethernet

	if type_ethernet == '0x0800':
		ip_header = struct.unpack("!1s1s2s2s2s1s1s2s4s4s", packet[0][14:34])
		version_ip = int(ip_header[0].encode('hex'), 16) >> 4
		ihl_ip =  int(ip_header[0].encode('hex'), 16) & 0x0f
		dsf_ip = ip_header[1].encode('hex')
		length_ip = ip_header[2].encode('hex')
		identification_ip = ip_header[3].encode('hex')
		reserve_ip = (int(ip_header[4].encode('hex'), 16) >> 15)
		dontfrag_ip = (int(ip_header[4].encode('hex'), 16) >> 14) & 1
		morefrag_ip = (int(ip_header[4].encode('hex'), 16) >> 13) & 1
		offset_ip = (int(ip_header[4].encode('hex'), 16)) & 0x1fff
		ttl_ip = ip_header[5].encode('hex')
		protocol_ip = ip_header[6].encode('hex')
		checksum_ip = ip_header[7].encode('hex')
		src_ip = ip_header[8].encode('hex')
		dst_ip = ip_header[9].encode('hex')

		print "* Internet Protocol Version 4"
		print "	Version:", version_ip
		print "	Header Length:", ihl_ip * 4, "bytes"
		print "	Service Type:", dsf_ip
		print "	Total Length:", int(length_ip, 16), "bytes"
		print "	identification:", int(identification_ip, 16)
		print "	Reserved bit:", reserve_ip
		print "	Don't Fragment:", dontfrag_ip
		print "	More Fragment:", morefrag_ip
		print "	Fragmentation Offset:", offset_ip
		print "	Time-To-Live:", int(ttl_ip, 16)
		print "	Protocol:", int(protocol_ip, 16)
		print "	Header Checksum:", checksum_ip
		print "	Source IP Address:", hex2ip(src_ip)
		print "	Destination IP Address:", hex2ip(dst_ip)

		if protocol_ip == '06':
			tcp_header = struct.unpack("!2s2s4s4s2s2s2s2s", packet[0][34:54])
			srcport_tcp = tcp_header[0].encode('hex')
			dstport_tcp = tcp_header[1].encode('hex')
			seq_tcp = tcp_header[2].encode('hex')
			ackn_tcp =  tcp_header[3].encode('hex')
			flag_tcp = tcp_header[4].encode('hex')
			thl_tcp = (int(flag_tcp, 16) & 0xff00) >> 12
			reserved_tcp = (int(flag_tcp, 16) >> 9) & 7
			nonce_tcp = (int(flag_tcp, 16) >> 8) & 1
			cwr_tcp = (int(flag_tcp, 16) >> 7) & 1
			ece_tcp = (int(flag_tcp, 16) >> 6) & 1
			urg_tcp = (int(flag_tcp, 16) >> 5) & 1
			ack_tcp = (int(flag_tcp, 16) >> 4) & 1
			psh_tcp = (int(flag_tcp, 16) >> 3) & 1
			rst_tcp = (int(flag_tcp, 16) >> 2) & 1
			syn_tcp = (int(flag_tcp, 16) >> 1) & 1
			fin_tcp = int(flag_tcp, 16) & 1
			window_tcp = tcp_header[5].encode('hex')
			checksum_tcp = tcp_header[6].encode('hex')
			urgent_tcp = tcp_header[7].encode('hex')
			
			print "* Transmission Control Protocol"
			print "	Source Port:", int(srcport_tcp, 16)
			print "	Destination Port:", int(dstport_tcp, 16)
			print "	Sequence Number:", int(seq_tcp, 16)
			print "	Acknowledgment Number:", int(ackn_tcp, 16)
			print "	Header Length:", thl_tcp * 4, "bytes"
			print "	Reserved:", reserved_tcp
			print "	Nonce:", nonce_tcp
			print "	CWR:", cwr_tcp
			print "	ECN-Echo:", ece_tcp
			print "	Urgent:", urg_tcp
			print "	Acknowledgment:", ack_tcp
			print "	Push:", psh_tcp
			print "	Reset:", rst_tcp
			print "	Syn:", syn_tcp
			print "	Fin:", fin_tcp
			print "	Window Size:", int(window_tcp, 16)
			print "	Checksum:", checksum_tcp
			print "	Urgent Pointer:", urgent_tcp

		elif protocol_ip == '11':
			udp_header = struct.unpack("!2s2s2s2s", packet[0][34:42])
			srcport_udp = udp_header[0].encode('hex')
			dstport_udp = udp_header[1].encode('hex')
			length_udp = udp_header[2].encode('hex')
			checksum_udp = udp_header[3].encode('hex')

			print "* User Datagram Protocol"
			print "	Source Port:", int(srcport_udp, 16)
			print "	Destination Port:", int(dstport_udp, 16)
			print "	Length:", int(length_udp, 16)
			print "	Checksum:", checksum_udp

	elif type_ethernet == '0x0806':
		arp_header = struct.unpack("!2s2s1s1s2s6s4s6s4s", packet[0][14:42])
		htype_arp = arp_header[0].encode('hex')
		ptype_arp = arp_header[1].encode('hex')			
		hlen_arp = arp_header[2].encode('hex')
		plen_arp = arp_header[3].encode('hex')
		oper_arp = arp_header[4].encode('hex')
		sha_arp = arp_header[5].encode('hex')
		spa_arp = arp_header[6].encode('hex')
		tha_arp = arp_header[7].encode('hex')
		tpa_arp = arp_header[8].encode('hex')

		print "* Address Resolution Protocol"
		print "	Hardware Type:", int(htype_arp, 16)
		print "	Protocol Type: 0x" + ptype_arp
		print "	Hardware Length:", int(hlen_arp, 16)
		print "	Protocol Length:", int(plen_arp, 16)
		print "	Operation:", oper_arp
		print "	Source Hardware Address:", hex2mac(sha_arp)
		print "	Source Protocol Address:", hex2ip(spa_arp)
		print "	Destination Hardware Address:", hex2mac(tha_arp)
		print "	Destination Protocol Address:", hex2ip(tpa_arp)
