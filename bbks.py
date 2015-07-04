import heapq
import sys
from copy import deepcopy
class PriorityQueue:
    """
    This class is a simple implementation of a priority queue using a heap data structure
    """
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority*-1, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        self.count-=1
        return item

    def isEmpty(self):
        return len(self.heap) == 0

class Node:
    """
    A representation of a node in the state space tree
    """
    def __init__(self, selectedTasks, fee, day, bound):
        self.selectedTasks = selectedTasks
        self.fee = fee
        self.day = day
        self.bound = bound
        self.id=0


def calculatedBound(node,sortedTasks,maxNumberOfDays):
    """
    This function calculates the upper bound - the total fees of the optimal relaxed scenario where we can
     take fractions of tasks
     - of a given node

    :param node: a node in the state space of the problem
    :param sortedTasks: the entire collection of the tasks sorted by density (fee/day) in a descending order
    :param maxNumberOfDays:  the maximum allowed number of days
    :return: the upper bound value  for the given node
    """
    lastItemAddedId=node.id
    currentDays = node.day
    currentFee=node.fee

    while lastItemAddedId<len(sortedTasks) and currentDays+sortedTasks[lastItemAddedId].day>maxNumberOfDays :
        currentDays+=sortedTasks[lastItemAddedId].day
        currentFee+=sortedTasks[lastItemAddedId].fee
        lastItemAddedId+=1
    remainingDays = maxNumberOfDays-currentDays
    if remainingDays>0 and lastItemAddedId<len(sortedTasks):
        fractionalFee=remainingDays*sortedTasks[lastItemAddedId].fee/sortedTasks[lastItemAddedId].day
        currentFee+=fractionalFee
    return currentFee


def SolveKSWithBB(sortedTasks,maxNumberOfDays):
    """
    The main function for exploring the branch and bound state space tree
    Given a list of tasks (ordered by density fee/day) and the maximum number of days allowed, this function optimizes
     the chosen items that maximizes the total fees using the branch and bound algorithm as a knapsack problem

    :param sortedTasks: the entire collection of the given tasks ordered by their density (fee/day)
    :param maxNumberOfDays: the maximum allowed number of days
    :return: the best possible total fees value and the set of tasks to achieve this value
    """
    q =  PriorityQueue()
    bestSoFar = Node(  [0 for i in tasks], float("-inf"), 0, 0 )
    startNode = Node(  [0 for i in tasks], 0, 0, 0 )
    startNode.bound=calculatedBound(startNode,sortedTasks,maxNumberOfDays)
    q.push(startNode,startNode.bound)
    while not q.isEmpty():
        currentNode = q.pop()
        if currentNode.bound>bestSoFar.fee and currentNode.id<len(sortedTasks)-1:
            nextAdded = deepcopy(currentNode)
            nextAdded.id+=1
            nextAdded.selectedTasks[currentNode.id]=1
            nextAdded.fee+= sortedTasks[currentNode.id].fee
            nextAdded.day+=sortedTasks[currentNode.id].day
            nextAdded.bound=calculatedBound( nextAdded,sortedTasks,maxNumberOfDays )
            if nextAdded.day<=maxNumberOfDays:
                if nextAdded.fee>bestSoFar.fee:
                    bestSoFar=deepcopy(nextAdded)
                if nextAdded.bound >bestSoFar.fee:
                    q.push(nextAdded,nextAdded.bound)
            nextNotAdded  = deepcopy(currentNode)
            nextNotAdded.selectedTasks[currentNode.id]=-1
            nextNotAdded.id+=1
            nextNotAdded.bound=calculatedBound( nextNotAdded,sortedTasks,maxNumberOfDays )
            if nextNotAdded.bound>bestSoFar.fee:
                q.push(nextNotAdded,nextNotAdded.bound)
    indx=0
    bst=[]
    for i in bestSoFar.selectedTasks:
        if i==1:
            bst.append(sortedTasks[indx])
        indx+=1
    bst.sort(key=lambda x:x.id)
    return (bestSoFar.fee,bst,bestSoFar.day)

class Task:
    """
    An object representation of a task
    """
    def __init__(self, fee, day,id):
        self.fee = fee
        self.day = day
        self.density = fee/day
        self.id=id

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('usage: bbks.py [the Path to the file containing the tasks ] [max allowed number of Days]')
        sys.exit(1)
    tasksFileName =sys.argv[1]
    with open(tasksFileName) as tasksFile:
        tasksLines = tasksFile.readlines()
    maxNumberOfDays = int(sys.argv[2])
    tasks=[]
    id=1

    for taskLine in tasksLines[1:]:
        line=taskLine.split()
        tasks.append(Task(float(line[0]),float(line[1]),id))
        id+=1
    tasks.sort(key=lambda x:x.density,reverse=True)
    bestFees,selectedTasks,usedDays = SolveKSWithBB(tasks,maxNumberOfDays)
    print('The max fees total is: {0} in: {1} days '.format(bestFees,usedDays))
    print('The tasks are as follows:')
    for task in selectedTasks:
        print('id: {2}, fee: {0}, day: {1}'.format(int(task.fee), int(task.day),task.id))