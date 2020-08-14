import numpy as np
import  random
from mpi4py import  MPI
comm=MPI.COMM_WORLD
my_rank=comm.Get_rank()
p=comm.Get_size()
def merge(arr, l, m, r):
    n1 = int(m - l + 1)
    n2 = int(r- m)

    L = np.zeros(n1)
    R = np.zeros(n2)

    # Copy data to temp arrays L[] and R[]
    for i in range(0 , n1):
        L[i] = arr[l + i]

    for j in range(0 , n2):
        R[j] = arr[m + 1 + j]
    i = 0
    j = 0
    k = l

    while i < n1 and j < n2 :
        if L[i] <= R[j]:
            arr[k] = int(L[i])
            i += 1
        else:
            arr[k] = int(R[j])
            j += 1
        k += 1
    while i < n1:
        arr[k] = int(L[i])
        i += 1
        k += 1
    while j < n2:
        arr[k] = int(R[j])
        j += 1
        k += 1
def mergeSort(arr,l,r):
    if l < r:


        m = int((l+(r-1))/2)

        mergeSort(arr, l, m)
        mergeSort(arr, m+1, r)
        merge(arr, l, m, r)
flag=0
if  p != pow(2, int(np.log2(p))):
    print("processor must be in power of 2: all processor terminate MPI Abort")
    comm.Abort()

if my_rank==0:
    #arr = [12, 11, 13, 5, 6, 7,78,55,48,25,-66,44,15,190,0,900,0,52,47,77,89,104,52,48,23,26,41]
    arr = [random.randint(-100, 100) for iter in range(25)]
    # arr = []
    # elem = int(input("Enter the no of element :"))
    # for i in range(elem):
    #     arr.append(int(input()))
    # arr=np.array(arr)
    #arr=[random.randint(-100, 100) for iter in range(16)]
    print(arr)
    N=len(arr)
    # if p==1:
    #     print("invalid no of processor")
    #     exit()
    step=int(len(arr)/(p-1))
    res=int(len(arr)%(p-1))
    if p>N:
        print("Warning: large no of Processor ")
        step=1
        res=0


mask=1
for phase in range(1,int(np.log2(p))+1):
    if (p >> 1) != p / 2 or p != pow(2, int(np.log2(p))):
        print("invalid no of processor")
        exit()
    phase_max=np.power(2,phase)
    if(my_rank>=0 and my_rank<=(phase_max/2)-1):
        recepient=my_rank | mask
        if my_rank==0:
            comm.send([arr,step,res],dest=recepient,tag=1)
            if flag==0:
              my_arr=arr[:res]
              print(my_rank,my_arr)
              mergeSort(my_arr,0,len(my_arr)-1)
              print('sorted array',my_rank,my_arr)
              flag=1

        if my_rank!=0:
            comm.send([arr,step,res],dest=recepient,tag=1)
            if flag==0:
              my_arr=arr[step*(my_rank-1)+res:step*(my_rank)+res]
              print(my_rank,my_arr)
              mergeSort(my_arr,0,len(my_arr)-1)
              print('sorted array',my_rank,my_arr)
              flag=1

    elif my_rank>=phase_max/2 and my_rank<=phase_max-1:
            sender=my_rank & ~mask
            message=comm.recv(source=sender,tag=1)
            [arr,step,res]=message
            if flag==0:
              my_arr = arr[step * (my_rank - 1)+res:(step*(my_rank)+res)]
              print(my_rank,my_arr)
              mergeSort(my_arr,0,len(my_arr)-1)
              print('sorted array',my_arr)
              flag=1
    mask=mask<<1


#print('mask',mask)
#print("C=",C)
flag1=0
mask=int(p/2)
for phase in range(int(np.log2(p)),0,-1):
    phase_max=pow(2,phase)
    if my_rank>=phase_max/2 and my_rank<=phase_max-1:
        recip=my_rank & ~mask
        comm.send(my_arr, dest=recip, tag=6)
       # print(my_rank, C)
    if my_rank>=0 and my_rank<=(phase_max/2)-1:
       sen=my_rank | mask
       new_arr=comm.recv(source=sen,tag=6)
       n = int(len(my_arr))
       my_arr = my_arr + new_arr
       m = int(len(my_arr))
       merge(my_arr, 0, n - 1, m - 1)


    mask=int(mask/2)

if my_rank==0:
    print("Given array",arr)
    print("Sorted array",my_arr)
    print(my_rank,len(my_arr),len(arr))

MPI.Finalize()