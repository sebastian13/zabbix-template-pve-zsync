#!/usr/bin/perl

# This script parses the output of `PVE-zsync list`
# https://pve.proxmox.com/wiki/PVE-zsync

# Author: Sebastian Plocek
# https://github.com/sebastian13/zabbix-template-pve-zsync

use strict;
use warnings;
use 5.010;

my $first = 1;

print "[\n";

for my $i (`pve-zsync list | tail -n +2`)
{
	my @a = split ' ', $i;

	print "\t,\n" if not $first;
	$first = 0;

	print "\t{\n";
	print "\t\t\"{#SOURCE}\":\"$a[0]\",\n";
	print "\t\t\"{#NAME}\":\"$a[1]\",\n";
	print "\t\t\"{#STATE}\":\"$a[2]\",\n";
	print "\t\t\"{#LASTSYNC}\":\"$a[3]\",\n";
	print "\t\t\"{#TYPE}\":\"$a[4]\",\n";
	print "\t\t\"{#CON}\":\"$a[5]\"\n";
	print "\t}\n";
}

print "]\n";
