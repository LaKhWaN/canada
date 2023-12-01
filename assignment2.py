#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Winter 2023
Program: assignment2.py 
Author: "Student Name"
The python code in this file is original work written by
"Student Name". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: <Enter your documentation here>

Date: 

'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Print sizes in human readable format")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    num_hashes = int(percent * length)
    num_spaces = length - num_hashes
    return '[' + '#' * num_hashes + ' ' * num_spaces + ']'

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open('/proc/meminfo') as meminfo_file:
        for line in meminfo_file:
            if line.startswith('MemTotal:'):
                return int(line.split()[1])

def get_avail_mem() -> int:
    "return total memory that is currently in use"
    with open('/proc/meminfo') as meminfo_file:
        for line in meminfo_file:
            if line.startswith('MemAvailable:'):
                return int(line.split()[1])

def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
    pidof_output = os.popen(f"pidof {app_name}").read().strip()
    if pidof_output:
        return [int(pid) for pid in pidof_output.split()]
    else:
        return []

def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    try:
        with open(f'/proc/{proc_id}/status') as status_file:
            for line in status_file:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1])
    except FileNotFoundError:
        return 0

if __name__ == "__main__":
    args = parse_command_args()

    if not args.program:
        total_mem = get_sys_mem()
        avail_mem = get_avail_mem()

        if args.human_readable:
            total_mem /= (1024 * 1024)  # Convert to GiB
            avail_mem /= (1024 * 1024)  # Convert to GiB

        percent_used = 1 - (avail_mem / total_mem)

        print(f"Memory {percent_to_graph(percent_used, args.length)} | {int(avail_mem)}/{int(total_mem)}")

    else:
        if not os.popen(f"pidof {args.program}").read().strip():
            print(f"{args.program} not found.")
            sys.exit(1)

        total_rss = 0

        for pid in pids_of_prog(args.program):
            total_rss += rss_mem_of_pid(pid)

        if args.human_readable:
            total_rss /= (1024 * 1024)  # Convert to GiB

        percent_used = total_rss / get_sys_mem()

        print(f"{args.program} {percent_to_graph(percent_used, args.length)} | {int(total_rss)}")
