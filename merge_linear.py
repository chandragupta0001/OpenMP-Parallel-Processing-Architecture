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
if (p>>1)!=p/2 and p!=1:
    print("processor must be in power of 2")
    comm.Abort()


if my_rank==0:
    #arr = [12, 11, 13, 5, 6, 7,78,55,48,25,-66,44,15,190,0,900,0,52,47,77,89,104,52,48,23,26,41]
    arr=[random.randint(-100, 100) for iter in range(32)]


    print("given array", arr)
    N=len(arr)
    step=1
    res=0
    if p>1 and len(arr)>p:
      step=int(len(arr)/(p-1))
      res=int(len(arr)%(p-1))
    if p==1:
        mergeSort(arr, 0, len(arr) - 1)
        print("result",arr)
        exit()
    print(step,res)
    # if p>N:
    #     print("large no of Processor ")
    #     mergeSort(arr,0,len(arr)-1)
    #     print("result", arr)
    #     comm.Abort()

    # if (p>>1)!=p/2:
    #     print("invalid no of processor")
    #     exit()

if my_rank==0:
    #my_arr=arr[:(step+res)]
    comm.send([arr,step,res,N],dest=1,tag=1)
    if p>2:
     comm.send([arr, step, res,N], dest=p-1, tag=1)
    #print(my_rank,my_arr)
    #n=int(len(my_arr))
    #mergeSort(my_arr,0,n-1)
    #print('shorted',my_rank,my_arr)
    left=comm.recv(source=1,tag=2)
    right=[]
    if p>2:
     right=comm.recv(source=p-1,tag=2)
    n=int(len(left))
    left=left+right
    #n=int(len(left))
    m = int(len(left))
    merge(left,0,n-1,m-1)
    if len(arr)!=len(left):
        print("Sorted array",np.unique(left))
    else:
     print("sorted array",left)
     print(len(arr),len(left))
    # left=np.concatenate(my_arr,right)
    # result=np.concatenate(left,right)
if my_rank==p/2:
    # if (p>>1)!=p/2:
    #     print("invalid no of processor")
    #     exit()
    message=comm.recv(source=(p/2)-1,tag=1)
    [arr,step,res,N]=message
    # if p>N:
    #     print("invalid no of processor")
    #     exit()
    my_arr=arr[:step+res]
    print(my_rank, my_arr)
    n=int(len(my_arr))
    mergeSort(my_arr,0,n-1)
    print('shorted',my_rank,my_arr)
    comm.send(my_arr,dest=(p/2)-1,tag=2)


if my_rank==(p/2)+1:
    # if (p>>1)!=p/2:
    #     print("invalid no of processor")
    #     exit()
    message = comm.recv(source=((p / 2) + 2) % p, tag=1)
    [arr, step, res,N] = message
    # if p>N:
    #     print("invalid no of processor")
    #     exit()
    my_arr = arr[-step:]
    print(my_rank, my_arr)
    n=int(len(my_arr))
    mergeSort(my_arr,0,n-1)
    print('shorted',my_rank,my_arr)
    comm.send(my_arr,dest=((p/2)+2)%p,tag=2)
if my_rank>(p/2+1) and my_rank<=p-1 and p>2:
    # if (p>>1)!=p/2:
    #     print("invalid no of processor")
    #     exit()
    message = comm.recv(source=(my_rank + 1) % p, tag=1)
    [arr, step, res,N] = message
    # if p>N:
    #     print("invalid no of processor")
    #     exit()
    comm.send([arr[:-step],step,res,N],my_rank-1,tag=1)
    my_arr = arr[-step:]
    print(my_rank, my_arr)
    n=int(len(my_arr))
    mergeSort(my_arr,0,n-1)
    print('shorted',my_rank,my_arr)
    recived=comm.recv(source=my_rank-1,tag=2)
    n = int(len(my_arr))
    my_arr=my_arr+recived
    #n = int(len(my_arr))
    m = int(len(my_arr))
    merge(my_arr,0,n-1,m-1)
    comm.send(my_arr,dest=(my_rank+1)%p,tag=2)

if my_rank>0 and my_rank<p/2:
    # if (p>>1)!=p/2:
    #     print("invalid no of processor")
    #     exit()
    message = comm.recv(source=my_rank - 1, tag=1)
    [arr, step, res,N] = message
    # if p>N:
    #     print("invalid no of processor")
    #     exit()
    comm.send([arr[step:],step,res,N],my_rank+1,tag=1)


    my_arr = arr[:step]
    print(my_rank, my_arr)
    n=int(len(my_arr))
    mergeSort(my_arr,0,n-1)
    print('shorted',my_rank,my_arr)
    recived=comm.recv(source=my_rank+1,tag=2)
    n = int(len(my_arr))
    my_arr=my_arr+recived
   # n = int(len(my_arr))
    m = int(len(my_arr))
    merge(my_arr,0,n-1,m-1)
    comm.send(my_arr,dest=(my_rank-1)%p,tag=2)
# if my_rank==0:
#   n = len(arr)
#   print ("Given array is",arr)
#
#   mergeSort(arr,0,n-1)
#   print ("\n\nSorted array is",arr)

MPI.Finalize()

