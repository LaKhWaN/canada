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

Description: Memory Visualiser -- See Memory Usage Report with bar charts

Date: 
'''

import argparse
import os

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    num_chars = int(percent * length)
    return "[{}{} | {}%]".format("#" * num_chars, " " * (length - num_chars), int(percent * 100))

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open('/proc/meminfo') as mem_info:
        for line in mem_info:
            if line.startswith('MemTotal:'):
                return int(line.split()[1])
    return 0

def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    status_file_path = f'/proc/{proc_id}/status'
    if os.path.exists(status_file_path):
        with open(status_file_path) as status_file:
            for line in status_file:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1])
    return 0

def is_firefox_running() -> bool:
    "Check if Firefox is running"
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/cmdline', 'rb') as cmdline_file:
                    cmdline = cmdline_file.read().decode('utf-8')
                    if 'firefox' in cmdline:
                        return True
            except (FileNotFoundError, UnicodeDecodeError):
                continue
    return False

if __name__ == "__main__":
    args = parse_command_args()

    if not args.program:
        total_memory = get_sys_mem()
        available_memory = get_sys_mem()  # Adjust this based on your specific requirements
        memory_in_use = total_memory - available_memory
        percent_used = memory_in_use / total_memory
        graph = percent_to_graph(percent_used, args.length)
        print(f'Memory {graph} {memory_in_use}/{total_memory}')
    else:
        if args.program.lower() == 'firefox':
            if not is_firefox_running():
                print(f'{args.program} not found.')
            else:
                total_memory = get_sys_mem()
                total_memory_in_use = 0

                for pid in os.listdir('/proc'):
                    if pid.isdigit():
                        total_memory_in_use += rss_mem_of_pid(pid)

                percent_used = total_memory_in_use / total_memory
                graph = percent_to_graph(percent_used, args.length)
                print(f'Memory {graph} {total_memory_in_use}/{total_memory}')
        else:
            print(f'The script does not currently support checking memory usage for {args.program}.')
