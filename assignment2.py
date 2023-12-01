import argparse
import os, sys

def parse_command_args():
    """
    Parses the command line arguments using argparse.

    Returns:
        argparse.Namespace: A namespace containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts")
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="Print sizes in human readable format")
    parser.add_argument("-l", "--length", type=int, default=20,
                        help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", nargs="?", help="Program to scan")
    return parser.parse_args()

def percent_to_graph(percent: float, length: int=20) -> str:
    """
    Converts a percentage to a string of hash symbols and spaces.

    Args:
        percent (float): The percentage to be converted.
        length (int): The total length of the bar graph.

    Returns:
        str: A string of hash symbols and spaces.
    """
    hashes = int(percent * length)
    spaces = length - hashes
    return "#" * hashes + " " * spaces

def get_sys_mem() -> int:
    """
    Reads the /proc/meminfo file and returns the total system memory.

    Returns:
        int: The total system memory in bytes.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024

def get_avail_mem() -> int:
    """
    Reads the /proc/meminfo file and returns the available system memory.

    Returns:
        int: The available system memory in bytes.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024

def pids_of_prog(program: str) -> list:
    """
    Gets the PIDs of a running program.

    Args:
        program (str): The name of the program to scan.

    Returns:
        list(int): A list of PIDs of the program.
    """
    output = os.popen(f"pidof {program}").read()
    return [int(pid) for pid in output.strip().split()]

def rss_mem_of_pid(pid: int) -> int:
    """
    Gets the RSS memory of a process.

    Args:
        pid (int): The PID of the process.

    Returns:
        int: The RSS memory of the process in bytes.
    """
    path = f"/proc/{pid}/status"
    try:
        with open(path) as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except FileNotFoundError:
        pass
    return 0

def main():
    args = parse_command_args()

    if args.program:
        pids = pids_of_prog(args.program)
        total_rss = sum(rss_mem_of_pid(pid) for pid in pids)
        print(f"{args.program}:")
    else:
        total_rss = 0
        pids = [os.getpid()]

    for pid in pids:
        rss = rss_mem_of_pid(pid)
        total_rss += rss

        percent = rss / get_sys_mem()
        graph = percent_to_graph(percent, args.length)

        if args.human_readable:
            print(f"{pid:>8} {graph} {percent:.2%} {rss/1024:.2f}KiB")
        else:
            print(f"{pid:>8} {graph} {percent:.2%} {rss:,}")

    if not args.program:
        total_mem = get_sys_mem()
        avail_mem = get_avail_mem()
