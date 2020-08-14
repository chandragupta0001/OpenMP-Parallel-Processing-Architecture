from mpi4py import MPI
import numpy as np
comm=MPI.COMM_WORLD
my_rank= comm.Get_rank()
p=comm.Get_size()
if (p>>1)!=p/2 and p!=1:
    print("processor must be in power of 2")
    comm.Abort()

if my_rank==0:
    # print("enter the matrix for first ")
    #  R=int(input("Enter rows: "))
    #  C  = int(input("Enter coloumn: "))

     N=100
     M=100
     A=np.array([list(range(1 + N * i, 1 + N * (i + 1))) for i in range(M)])#M X N
     print("A=",A)
     #A=np.array([[1,2],[2,3]])
     B=np.array([list(range(1 + M * i, 1 + M * (i + 1))) for i in range(N)])# N X M
     print("B=",B)
     #B=np.array([[2,3],[5,6]])
     M = A.shape[0]
     N = A.shape[0]
     Z = B.shape[1]
     C=np.zeros((M,M))#M X M
     #A=np.array([[],[]])
     #B=np.array([[],[]])
     step=1
     res=0
     if M>p:
      step=int(M/p)
      res=M%p
#print(step,res)
if my_rank==0:
    # if  p != pow(2, int(np.log2(p))) and p!=1:
    #     print("invalid no of processor")
    #     exit()
    row=A[:(step+res),:]
    if p==1:
        row=A
    else:
     comm.send([A[(step+res):,:],B,step,res],dest=1,tag=1)
    if p>2:
     comm.send([A[(step+res):,:],B,step,res],dest=(p-1),tag=1)
    print(my_rank,row)
    prod=row@B

    #print(my_rank,prod)
    top=[]
    bot=[]
    if p>1:
     top=comm.recv(source=1,tag=2)
     top=np.row_stack((prod,top))
    result=top
    if p==1:
        result=prod
    if p>2 and M>p:
     bot=comm.recv(source=p-1,tag=2)
     result=np.row_stack((top,bot))
    print("result",result)
if my_rank==p/2:
     # if p != pow(2, int(np.log2(p))):
     #    print("invalid no of processor")
     #    exit()
     message=comm.recv(source=(p/2)-1,tag=1)
     [X, B,step, res] = message
     row=X[:step,:]
     print(my_rank,row)
     prod = row @ B
     #print(my_rank, prod)
     comm.send(prod,dest=(p/2)-1,tag=2)
if my_rank==(p/2)+1:
     # if p != pow(2, int(np.log2(p))):
     #    print("invalid no of processor")
     #    exit()
     message=comm.recv(source=((p/2)+2)%p,tag=1)
     [X, B, step, res] = message
     row = X[-step:, :]
     #print(my_rank, row)
     prod = row @ B
    # print(my_rank, prod)
     comm.send(prod,dest=((p/2)+2)%p,tag=2)
if my_rank>(p/2+1) and my_rank<=p-1:
    # if  p != pow(2, int(np.log2(p))):
    #     print("invalid no of processor")
    #     exit()
    message=comm.recv(source=(my_rank+1)%p,tag=1)
    [X, B, step, res] = message
    comm.send([X[:-step,:],B,step,res],my_rank-1,tag=1)
    row = X[-step:, :]
    print(my_rank,row)
    prod = row @ B
    #print(my_rank, prod)
    recived=comm.recv(source=(my_rank-1),tag=2)
    recived=np.row_stack((recived,prod))
    comm.send(recived,(my_rank+1)%p,tag=2)

if my_rank>0 and my_rank<p/2:
    # if  p != pow(2, int(np.log2(p))):
    #     print("invalid no of processor")
    #     exit()
    message=comm.recv(source=my_rank-1,tag=1)
    [X, B, step, res] = message
    comm.send([X[step:,:],B,step,res],my_rank+1,tag=1)
    row = X[:step, :]
    print(my_rank,row)
    prod = row @ B
    #print(my_rank, prod)
    recived = comm.recv(source=(my_rank +1), tag=2)
    recived = np.row_stack((prod,recived))
    comm.send(recived, (my_rank - 1) % p, tag=2)


MPI.Finalize()