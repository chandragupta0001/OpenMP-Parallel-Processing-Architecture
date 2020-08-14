from mpi4py import MPI
import numpy as np
comm=MPI.COMM_WORLD
my_rank= comm.Get_rank()
p=comm.Get_size()
if  p != pow(2, int(np.log2(p))):
    print("processor must be in power of 2: all processor terminate")
    comm.Abort()

flag=0
if my_rank==0:
     N=100
     M=100
     A=np.array([list(range(1 + N * i, 1 + N * (i + 1))) for i in range(M)])#M X N
    # A=np.array([[1,2,5],[2,3,6],])

     print("A",A)
     B=np.array([list(range(1 + M * i, 1 + M * (i + 1))) for i in range(N)])# N X M
     #B=np.array([[2,3],[5,6]])
     print("B",B)
     M=A.shape[0]
     N=A.shape[0]
     Z=B.shape[1]
     if(A.shape[1]!=B.shape[0]):

      comm.Abort()
     C=np.zeros((M,Z))#M X M
     R=np.copy(C)
     step=1
     res=0
     #
     # if p>N:
     #    p=N
     #    p=pow(2,int(np.log2(p)))
     #
     # if p<N:
     step=int(M/p)
     res=M%p
     if p>M:
         print("error   overflow")
         step=1
         res=0
     if p==1:
         print("Processor should be Power of 2")
         print("Final",A@B)
         exit()




mask=1
for phase in range(1,int(np.log2(p))+1):
    phase_max=np.power(2,phase)
    if (p >> 1) != p / 2 or p != pow(2, int(np.log2(p))):
        print("Processor Must be Power of 2: process terminate")
        exit()
    if(my_rank>=0 and my_rank<=(phase_max/2)-1):

        recepient=my_rank | mask
        if my_rank==0:
            comm.send(A[:,:],dest=recepient,tag=1)
            comm.send(B,dest=recepient, tag=2)
            comm.send(C,dest=recepient,tag=3)
            comm.send(step,dest=recepient, tag=4)
            comm.send(res,dest=recepient,tag=5)
            if flag==0:
              row=A[:(step+res+1),:]
              print(my_rank,row)
              prod=row@B
              R[:(step + res+1), :]=prod
              flag=1
            #print(step,res)

            #print(my_rank)
        if my_rank!=0:

            comm.send(A[:,:],dest=recepient,tag=1)

            comm.send(B,dest=recepient, tag=2)
            comm.send(C,dest=recepient,tag=3)
            comm.send(step,dest=recepient, tag=4)
            comm.send(res,dest=recepient,tag=5)
            if flag==0:
              row = A[(step*(my_rank)+res+1):(step*(my_rank+1)+res+1), :]
              print(my_rank,row)
              prod=row@B
              R[(step * (my_rank) + res+1):(step * (my_rank +1)+ res+1), :]=prod
              flag=1
            #print(my_rank)

    elif my_rank>=phase_max/2 and my_rank<=phase_max-1:
        sender=my_rank & ~mask
        A=comm.recv(source=sender,tag=1)
        B=comm.recv(source=sender, tag=2)
        C=comm.recv(source=sender, tag=3)
        step=comm.recv(source=sender, tag=4)
        res=comm.recv(source=sender, tag=5)
        R=np.copy(C)
        if flag==0:
          row = A[(step * (my_rank) + res+1):(step * (my_rank+1) + res+1), :]
          prod=row@B
          print(my_rank,row)
          R[(step * (my_rank) + res+1):(step * (my_rank+1) + res+1), :]=prod
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
        comm.send(R, dest=recip, tag=6)
       # print(my_rank, C)



    if my_rank>=0 and my_rank<=(phase_max/2)-1:

        sen=my_rank | mask
        R=R+comm.recv(source=sen,tag=6)
       # print(my_rank, C)

    mask=int(mask/2)
if my_rank==0:
  print("total no of processor",p)
  print("Step Size",step,"Residual", res)
  print('fianl',R)
  print("validate",np.sum(R-A@B))



MPI.Finalize()