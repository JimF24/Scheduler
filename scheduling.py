# Author: JiaYi Feng
# NetID: jf3354@nyu.edu
# Date: 10/15/2018
import heapq
import sys

'''Process object.
    attributes: A,B,C,M
    input_order is the order in the sorted list
    quantum is initialized to be 2
    penalty is initialized to be -1
    blockedCount is the remaining time of IO burst
    Totalblock is the total IO burst
    burstTime is the remaining time of CPU burst
    Totalburst is the total CPU burst
    finishTime records the big time when the process terminates
    
    __lt__ function is a comparator function, highest priority is penalty ratio, then A, the lowest priority is input_order
'''


class Processobj:
    A = 0
    B = 0
    C = 0
    M = 0
    input_order = 0
    blockedCount = 0
    Totalblock = 0
    finishTime = 0
    burstTime = -1
    Totalburst = 0
    quantum = 2
    penalty = -1

    ## initialize process object
    def __init__(self, a, b, c, m):
        self.A = a
        self.B = b
        self.C = c
        self.M = m

    ## comparator function
    def __lt__(self, other):
        # highest priority
        if self.penalty != other.penalty:
            return self.penalty > other.penalty
        #second priority
        elif self.A != other.A:
            return self.A < other.A
        #lowest priority
        else:
            return self.input_order < other.input_order

# global var X
X = 0
# global var random_numbers is the random-numbers file
global random_numbers
random_numbers = open("random-numbers", "r")


'''randomOS function
    @@@ param: U: basically it's the process.B
    @@@
    
'''
def randomOS(U):
    X = int(next(random_numbers))
    res = 1 + (X % U)
    return res

'''FCFS function
    @@@ param: count: number of processes
                processes: process list
                detailed: --verbose flag
    @@@
    
'''
def FCFS(count,processes, detailed):
    # initialize var
    running = None
    blocked = []
    ready = []
    # currready is a priority queue that handles processes that are going to be added to ready list in each cycle
    curready = []
    terminated = []
    time = 0
    cpu = 0
    IO = 0
    totalTurnaroud = 0
    totalWaiting = 0
    totalBlock = 0
    # print original input
    print("The original input was: ", end="")
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()

    # print sorted input and assign input_order to every processes
    processes.sort()
    for i in range(len(processes)):
        processes[i].input_order = i
    print("The (sorted) input is: ",end='')
    print(count, "   ",end='')
    for i in range(count):
        print("(",end='')
        cur = processes[i]
        print(cur.A," ",cur.B," ",cur.C," ",cur.M," ",end='')
        print(")   ",end='')
    print()

    # Main loop
    while(True):
        # if --verbose flag: before cycle do print detailed info
        if detailed == True:
            if time == 0:
                print("Before cycle ", time,":",end=" ")
                for process in processes:
                    print("    ", "unstarted 0",end="")
                print()
            else:
                print("Before cycle ", time,":", end=" ")
                for process in processes:
                    if process in blocked:
                        print("    ", "blocked  ",process.blockedCount,end="")
                    elif process == running:
                        print("    ", "running  ",process.burstTime,end="")
                    elif  process in ready:
                        print("        ready  0", end="")
                    elif process in terminated:
                        print(" terminated  0",end="")
                    else:
                        print("  unstarted  0",end="")
                print()

        # do blocked processes
        if blocked:
            for process in blocked:
                # IO burst -1 every cycle
                process.blockedCount = process.blockedCount - 1
                # if IO burst ends, append the process to ready list
                if process.blockedCount == 0:
                    blocked = [process for process in blocked if process.blockedCount != 0]
                    heapq.heappush(curready, process)

        # do running processes
        if running is not None:
            # CPU burst -1 every cycle
            running.burstTime = running.burstTime - 1
            # if CPU burst ends, we determine whether the process terminates or IO burst is required
            if running.burstTime == 0:
                # process terminates, append it to terminated list
                if running.Totalburst == running.C:
                    running.finishTime = time
                    terminated.append(running)
                    running = None
                # IO burst is required
                else:
                    blocked.append(running)
                    running = None
        # do arriving processes, check whether the process starts or not
        for process in processes:
            if process.A == time:
                heapq.heappush(curready, process)
        # append the heap to the big ready list
        while curready:
            ready.append(heapq.heappop(curready))
        # do ready processes
        if (running is None) and ready:
            # pop the first element of the ready list (following first come first served)
            running = ready.pop(0)
            # compute CPU burst and IO burst for the process
            burst = randomOS(running.B)
            if burst + running.Totalburst > running.C:
                burst = running.C - running.Totalburst
            running.burstTime = burst
            running.Totalburst = running.Totalburst + running.burstTime
            if running.Totalburst != running.C:
                running.blockedCount = running.burstTime * running.M
                running.Totalblock = running.Totalblock + running.blockedCount
        # determine the main loop ends or not
        # if all processes are in terminated list, the loop ends
        if len(terminated) == len(processes):
            break
        # else, clock ++, if blocked list is not empty, IO Util ++
        else:
            if blocked:
                totalBlock = totalBlock +1
            time = time+1
    # print summary information
    print("The scheduling algorithm used was First Come First Served ")
    for i in range(len(processes)):
        per = processes[i]
        print("Process ",i,": ")
        print("         ",end='')
        print("(A,B,C,M) = ","(",per.A,",",per.B,",",per.C,",",per.M,")")
        print("         ", end='')
        print("Finishing time: ",per.finishTime)
        print("         ", end='')
        print("Turnaround time: ",per.finishTime-per.A)
        print("         ", end='')
        print("I/O time: ",per.Totalblock)
        print("         ", end='')
        print("Waiting time: ", per.finishTime-per.A-per.Totalblock-per.Totalburst)
    for process in processes:
        cpu = cpu + process.Totalburst
        IO = IO + process.Totalblock
        totalTurnaroud = totalTurnaroud + process.finishTime - process.A
        totalWaiting = totalWaiting + process.finishTime - process.A - process.Totalblock - process.Totalburst
    print("Summary Data: ")
    print("         ", end='')
    print("Finishing time: ",time)
    print("         ", end='')
    print("CPU Utilization: ", cpu/time)
    print("         ", end='')
    print("I/O Utilization: ", totalBlock/time)
    print("         ", end='')
    print("Throughput: ", 100*count/time, " processes per hundred cycles")
    print("         ", end='')
    print("Average turnaround time: ", totalTurnaroud/count)
    print("         ", end='')
    print("Average waiting time: ", totalWaiting/count)

'''Round Robin function
    @@@ param:  count: number of processes
                processes: process list
                detailed: --verbose flag
    @@@
    
'''
def RR(count, processes, detailed):
    running = None
    blocked = []
    ready = []
    curready = []
    terminated = []
    time = 0
    cpu = 0
    IO = 0
    totalTurnaroud = 0
    totalWaiting = 0
    totalBlock = 0
    # print original input
    print("The original input was: ", end="")
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    processes.sort()
    # print sorted input
    for i in range(len(processes)):
        processes[i].input_order = i
    print("The (sorted) input is: ", end='')
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    # main loop
    while(True):
        # if --verbose then: before cycle do print
        if detailed == True:
            if time == 0:
                print("Before cycle ", time,":",end=" ")
                for process in processes:
                    print("    ", "unstarted 0",end="")
                print()
            else:
                print("Before cycle ", time,":", end=" ")
                for process in processes:
                    if process in blocked:
                        print("    ", "blocked  ",process.blockedCount,end="")
                    elif process == running:
                        print("    ", "running  ",min(process.burstTime,process.quantum),end="")
                    elif  process in ready:
                        print("        ready  0", end="")
                    elif process in terminated:
                        print(" terminated  0",end="")
                    else:
                        print("  unstarted  0",end="")
                print()
        # do blocked processes
        if blocked:
            for process in blocked:
                # IO burst -1 every cycle
                process.blockedCount = process.blockedCount - 1
                # if IO burst ends, append process to ready list
                if process.blockedCount == 0:
                    blocked = [process for process in blocked if process.blockedCount != 0]
                    heapq.heappush(curready,process)
        # do running processes
        if running is not None:
            # CPU burst -1 every cycle
            running.burstTime = running.burstTime - 1
            # quantum -1 every cycle
            running.quantum = running.quantum - 1
            # if quantum is 0,  but CPU burst doesn't end, append the process to ready list
            if running.quantum == 0 and running.burstTime != 0:
                running.quantum = 2
                heapq.heappush(curready, running)
                running = None
            # if CPU burst ends, append the process to block list
            elif running.burstTime == 0:
                running.quantum = 2
                if running.Totalburst == running.C:
                    running.finishTime = time
                    terminated.append(running)
                    running = None
                else:
                    blocked.append(running)
                    running = None

        #do arriving processes
        #check if any process starts
        for process in processes:
            if process.A == time:
                heapq.heappush(curready, process)
        while curready:
            ready.append(heapq.heappop(curready))
        # do ready processes
        if (running is None) and ready:
            # pop the first element of the ready list as running
            running = ready.pop(0)
            # compute CPU burst time and IO burst
            if running.burstTime <= 0:
                burst = randomOS(running.B)
                if burst + running.Totalburst > running.C:
                    burst = running.C - running.Totalburst
                running.burstTime = burst
                running.Totalburst = running.Totalburst + running.burstTime
                if running.Totalburst != running.C:
                    running.blockedCount = running.burstTime * running.M
                    running.Totalblock = running.Totalblock + running.blockedCount
        # check if the main loop ends (all processes terminate, then the loop end)
        if len(terminated) == len(processes):
            break
        # if the main loop doesn't end, clock ++, if block list is not empty, IO Util ++
        else:
            if blocked:
                totalBlock = totalBlock +1
            time = time+1
    # print summary info
    print("The scheduling algorithm used was Round Robin ")
    for i in range(len(processes)):
        per = processes[i]
        print("Process ",i,": ")
        print("         ",end='')
        print("(A,B,C,M) = ","(",per.A,",",per.B,",",per.C,",",per.M,")")
        print("         ", end='')
        print("Finishing time: ",per.finishTime)
        print("         ", end='')
        print("Turnaround time: ",per.finishTime-per.A)
        print("         ", end='')
        print("I/O time: ",per.Totalblock)
        print("         ", end='')
        print("Waiting time: ", per.finishTime-per.A-per.Totalblock-per.Totalburst)
    for process in processes:
        cpu = cpu + process.Totalburst
        IO = IO + process.Totalblock
        totalTurnaroud = totalTurnaroud + process.finishTime - process.A
        totalWaiting = totalWaiting + process.finishTime - process.A - process.Totalblock - process.Totalburst
    print("Summary Data: ")
    print("         ", end='')
    print("Finishing time: ",time)
    print("         ", end='')
    print("CPU Utilization: ", cpu/time)
    print("         ", end='')
    print("I/O Utilization: ", totalBlock/time)
    print("         ", end='')
    print("Throughput: ", 100*count/time, " processes per hundred cycles")
    print("         ", end='')
    print("Average turnaround time: ", totalTurnaroud/count)
    print("         ", end='')
    print("Average waiting time: ", totalWaiting/count)


''' Last Come First Served function.
    @@@ param:  count: number of process
                proceeses: process list
                detailed: --verbose flag
    @@@
'''
def LCFS(count, processes, detailed):

    running = None
    blocked = []
    ready = []
    curready = []
    terminated = []
    time = 0
    cpu = 0
    IO = 0
    totalTurnaroud = 0
    totalWaiting = 0
    totalBlock = 0
    # print original input
    print("The original input was: ", end="")
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    processes.sort()
    # print sorted input
    for i in range(len(processes)):
        processes[i].input_order = i
    print("The (sorted) input is: ", end='')
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    # main loop
    while(True):
        # if --verbose, before cycle do print
        if detailed == True:
            if time == 0:
                print("Before cycle ", time,":",end=" ")
                for process in processes:
                    print("    ", "unstarted 0",end="")
                print()
            else:
                print("Before cycle ", time,":", end=" ")
                for process in processes:
                    if process in blocked:
                        print("    ", "blocked  ",process.blockedCount,end="")
                    elif process == running:
                        print("    ", "running  ",process.burstTime,end="")
                    elif  process in ready:
                        print("        ready  0", end="")
                    elif process in terminated:
                        print(" terminated  0",end="")
                    else:
                        print("  unstarted  0",end="")
                print()


        # do blocked processes
        if blocked:
            for process in blocked:
                # IO burst -1 every cycle
                process.blockedCount = process.blockedCount - 1
                # if IO burst ends, append the process to ready list
                if process.blockedCount == 0:
                    blocked = [process for process in blocked if process.blockedCount != 0]
                    heapq.heappush(curready, process)
        # do running processes
        if running is not None:
            # CPU burst -1 every cycle
            running.burstTime = running.burstTime - 1
            # if CPU burst ends
            if running.burstTime == 0:
                # check if the process terminates
                if running.Totalburst == running.C:
                    running.finishTime = time
                    terminated.append(running)
                    running = None
                # if not terminates, append the process to block list
                else:
                    blocked.append(running)
                    running = None
        # do arriving processes
        # check any process starts
        for process in processes:
            if process.A == time:
                heapq.heappush(curready, process)
        curready.sort()
        while curready:
            ready.append(curready.pop())
        # do ready processes
        if (running is None) and ready:
            # pop the last element of the ready list
            running = ready.pop()
            # compute IO burst and CPU burst
            burst = randomOS(running.B)
            if burst + running.Totalburst > running.C:
                burst = running.C - running.Totalburst
            running.burstTime = burst
            running.Totalburst = running.Totalburst + running.burstTime
            if running.Totalburst != running.C:
                running.blockedCount = running.burstTime * running.M
                running.Totalblock = running.Totalblock + running.blockedCount
        # if all processes are in the terminated list, main loop ends
        if len(terminated) == len(processes):
            break
        # else clock ++, if block list not empty, IO Util++
        else:
            if blocked:
                totalBlock = totalBlock +1
            time = time+1
    print("The scheduling algorithm used was Last Come First Served ")
    for i in range(len(processes)):
        per = processes[i]
        print("Process ",i,": ")
        print("         ",end='')
        print("(A,B,C,M) = ","(",per.A,",",per.B,",",per.C,",",per.M,")")
        print("         ", end='')
        print("Finishing time: ",per.finishTime)
        print("         ", end='')
        print("Turnaround time: ",per.finishTime-per.A)
        print("         ", end='')
        print("I/O time: ",per.Totalblock)
        print("         ", end='')
        print("Waiting time: ", per.finishTime-per.A-per.Totalblock-per.Totalburst)
    for process in processes:
        cpu = cpu + process.Totalburst
        IO = IO + process.Totalblock
        totalTurnaroud = totalTurnaroud + process.finishTime - process.A
        totalWaiting = totalWaiting + process.finishTime - process.A - process.Totalblock - process.Totalburst
    print("Summary Data: ")
    print("         ", end='')
    print("Finishing time: ",time)
    print("         ", end='')
    print("CPU Utilization: ", cpu/time)
    print("         ", end='')
    print("I/O Utilization: ", totalBlock/time)
    print("         ", end='')
    print("Throughput: ", 100*count/time, " processes per hundred cycles")
    print("         ", end='')
    print("Average turnaround time: ", totalTurnaroud/count)
    print("         ", end='')
    print("Average waiting time: ", totalWaiting/count)


''' Highest Penalty Ration Next function.
    @@@ param:  count: number of process
                proceeses: process list
                detailed: --verbose flag
    @@@
'''
def HPRN(count, processes, detailed):
    running = None
    blocked = []
    ready = []
    curready = []
    terminated = []
    time = 0
    cpu = 0
    IO = 0
    totalTurnaroud = 0
    totalWaiting = 0
    totalBlock = 0
    # print original input
    print("The original input was: ", end="")
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    processes.sort()
    # print sorted input
    for i in range(len(processes)):
        processes[i].input_order = i
    print("The (sorted) input is: ", end='')
    print(count, "   ", end='')
    for i in range(count):
        print("(", end='')
        cur = processes[i]
        print(cur.A, " ", cur.B, " ", cur.C, " ", cur.M, " ", end='')
        print(")   ", end='')
    print()
    # main loop
    while (True):
        # if --verbose, before cycle do print if detailed == true
        if detailed == True:
            if time == 0:
                print("Before cycle ", time, ":", end=" ")
                for process in processes:
                    print("    ", "unstarted 0", end="")
                print()
            else:
                print("Before cycle ", time, ":", end=" ")
                for process in processes:
                    if process in blocked:
                        print("    ", "blocked  ", process.blockedCount, end="")
                    elif process == running:
                        print("    ", "running  ", process.burstTime, end="")
                    elif process in ready:
                        print("        ready  0", end="")
                    elif process in terminated:
                        print(" terminated  0", end="")
                    else:
                        print("  unstarted  0", end="")
                print()
        # do blocked processes
        if blocked:
            for process in blocked:
                # IO burst -1 every cycle
                process.blockedCount = process.blockedCount - 1
                # if IO burst ends, append the process to blocked list
                if process.blockedCount == 0:
                    blocked = [process for process in blocked if process.blockedCount != 0]
                    heapq.heappush(curready, process)
        # do running processes
        if running is not None:
            # CPU burst -1 every cycle
            running.burstTime = running.burstTime - 1
            # if CPU burst ends, check whether it terminates
            if running.burstTime == 0:
                if running.Totalburst == running.C:
                    running.finishTime = time
                    terminated.append(running)
                    running = None
                else:
                    blocked.append(running)
                    running = None
        # do arriving processes
        # check any process starts
        for process in processes:
            if process.A == time:
                heapq.heappush(curready, process)
        while curready:
            ready.append(heapq.heappop(curready))
        # do ready processes
        if (running is None) and ready:
            # before pop from ready list, compute penalty ratio
            for process in ready:
                if process.Totalburst == 0:
                    process.penalty = (time - process.A)/1
                else:
                    process.penalty = (time - process.A)/process.Totalburst
            # sort ready based on the priority
            ready.sort()
            # pop the first element from the ready list
            running = ready.pop(0)
            # compute CPU burst and IO burst
            burst = randomOS(running.B)
            if burst + running.Totalburst > running.C:
                burst = running.C - running.Totalburst
            running.burstTime = burst
            running.Totalburst = running.Totalburst + running.burstTime
            if running.Totalburst != running.C:
                running.blockedCount = running.burstTime * running.M
                running.Totalblock = running.Totalblock + running.blockedCount
        # if all processes terminate, the main loop ends
        if len(terminated) == len(processes):
            break
        # else clock++, if block list not empty, IO Util ++
        else:
            if blocked:
                totalBlock = totalBlock + 1
            time = time + 1
    # print summary info
    print("The scheduling algorithm used was Highest Penalty Ratio Next ")
    for i in range(len(processes)):
        per = processes[i]
        print("Process ", i, ": ")
        print("         ", end='')
        print("(A,B,C,M) = ", "(", per.A, ",", per.B, ",", per.C, ",", per.M, ")")
        print("         ", end='')
        print("Finishing time: ", per.finishTime)
        print("         ", end='')
        print("Turnaround time: ", per.finishTime - per.A)
        print("         ", end='')
        print("I/O time: ", per.Totalblock)
        print("         ", end='')
        print("Waiting time: ", per.finishTime - per.A - per.Totalblock - per.Totalburst)
    for process in processes:
        cpu = cpu + process.Totalburst
        IO = IO + process.Totalblock
        totalTurnaroud = totalTurnaroud + process.finishTime - process.A
        totalWaiting = totalWaiting + process.finishTime - process.A - process.Totalblock - process.Totalburst
    print("Summary Data: ")
    print("         ", end='')
    print("Finishing time: ", time)
    print("         ", end='')
    print("CPU Utilization: ", cpu / time)
    print("         ", end='')
    print("I/O Utilization: ", totalBlock / time)
    print("         ", end='')
    print("Throughput: ", 100 * count / time, " processes per hundred cycles")
    print("         ", end='')
    print("Average turnaround time: ", totalTurnaroud / count)
    print("         ", end='')
    print("Average waiting time: ", totalWaiting / count)

# --verbose flag
detailed = False
# input file
filename = ""
if sys.argv[1] == "--verbose":
    detailed = True
    filename = sys.argv[2]
else:
    filename = sys.argv[1]
input = open(filename, "r")
processinfo = []
count = 0
processlist = []
# deal with input file
for s in input:
    s = s.split()
    for i in s:
        if count == 0:
            if i.isdigit():
                count = int(i)
        else:
            if '(' in i:
                i = i.strip('(')
                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' not in i:
                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' in i:
                i = i.strip(')')
                if i.isdigit():
                    processinfo.append(int(i))
                process = Processobj(processinfo[0],processinfo[1], processinfo[2], processinfo[3])
                processlist.append(process)
                processinfo.clear()
FCFS(count, processlist, detailed)
processlist.clear()
# reset everything for the next function
input.seek(0)
count = 0
for s in input:
    s = s.split()
    for i in s:
        if count == 0:
            if i.isdigit():
                count = int(i)
        else:
            if '(' in i:
                i = i.strip('(')

                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' not in i:
                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' in i:
                i = i.strip(')')
                if i.isdigit():
                    processinfo.append(int(i))
                process = Processobj(processinfo[0],processinfo[1], processinfo[2], processinfo[3])

                processlist.append(process)
                processinfo.clear()
random_numbers.seek(0)


RR(count, processlist, detailed)
processlist.clear()
input.seek(0)
count = 0
for s in input:
    s = s.split()
    for i in s:
        if count == 0:
            if i.isdigit():
                count = int(i)
        else:
            if '(' in i:
                i = i.strip('(')

                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' not in i:
                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' in i:
                i = i.strip(')')
                if i.isdigit():
                    processinfo.append(int(i))
                process = Processobj(processinfo[0],processinfo[1], processinfo[2], processinfo[3])

                processlist.append(process)
                processinfo.clear()
random_numbers.seek(0)


LCFS(count, processlist, detailed)
processlist.clear()
input.seek(0)
count = 0
for s in input:
    s = s.split()
    for i in s:
        if count == 0:
            if i.isdigit():
                count = int(i)
        else:
            if '(' in i:
                i = i.strip('(')

                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' not in i:
                if i.isdigit():
                    processinfo.append(int(i))
            elif ')' in i:
                i = i.strip(')')
                if i.isdigit():
                    processinfo.append(int(i))
                process = Processobj(processinfo[0],processinfo[1], processinfo[2], processinfo[3])

                processlist.append(process)
                processinfo.clear()
random_numbers.seek(0)


HPRN(count, processlist, detailed)


