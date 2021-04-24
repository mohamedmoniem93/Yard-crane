#!/usr/bin/python3.7

# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:20:23 2020

@author: Mohamed Abdel Moniem
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:59:26 2020

@author: Mohamed Abdel Moniem
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:52:33 2019

@author: Mohamed Abdel Moniem
"""

#Yard crane scheduling

from gurobipy import *

# initiate the model
m=Model()

# Modeldata

TB=6
yr=50
TC=6
yt=150

sourceblock=[1,2,3,4,5,6,7,8,9,10,11,12]
destblock=[1,2,3,4,5,6,7,8,9,10,11,12]
shifts=[1]


import random
Random=[]
for i in range (12):
    x=(random.randint(0,2))
    Random.append(x)
#print(Random)
IT=[]
for i in range(1,13):
    for j in range(1,2):
        IT.append(tuple([i,j]))       
#print(IT)
H= dict(zip(IT,Random))
print("H=", H)

import random
Random=[]
for i in range (12):
    x=(random.randint(0,2))
    Random.append(x)
#print(Random)
IT=[]
for i in range(1,13):
    for j in range(1,2):
        IT.append(tuple([i,j]))       
#print(IT)
b= dict(zip(IT,Random))
print("b=", b)     

##H= {(1, 1): 2, (2, 1): 0, (3, 1): 0, (4, 1): 1, (5, 1): 0, (6, 1): 2, (7, 1): 2, (8, 1): 0}
#b= {(1, 1): 2, (2, 1): 1, (3, 1): 2, (4, 1): 0, (5, 1): 1, (6, 1): 2, (7, 1): 0, (8, 1): 1}



I={1:(1,1),
   2:(1,2),
   3:(1,3),
   4:(1,4),
   5:(2,1),
   6:(2,2),
   7:(2,3),
   8:(2,4),
   9:(3,1),
   10:(3,2),
   11:(3,3),
   12:(3,4)}

J={1:(1,1),
   2:(1,2),
   3:(1,3),
   4:(1,4),
   5:(2,1),
   6:(2,2),
   7:(2,3),
   8:(2,4),
   9:(3,1),
   10:(3,2),
   11:(3,3),
   12:(3,4)}

y={}
#same rows and adj columns
for k1,v1 in I.items():
    for k2,v2 in J.items():
        if v1[0]==v2[0] and abs(v1[1]-v2[1])==1:
            y1=abs(v1[1]-v2[1])*210
            y[(k1,k2)]=y1
#same columns and diff rows
        elif v1[1]==v2[1] and v1[0]!=v2[0]:
           y5=abs(v1[0]-v2[0])*46+(2*yt) 
           y[(k1,k2)]=y5
#diff rows and adj columns
        elif v1[0]!=v2[0] and abs(v1[1]-v2[1])==1:
            y2=abs(v1[1]-v2[1])*210+abs(v1[0]-v2[0])*46+(2*yt) 
            y[(k1,k2)]=y2
        elif k1==k2:
            y[(k1,k2)]=10000000
        else: 
            y3=abs(v1[1]-v2[1])*210+abs(v1[0]-1)+abs(v2[0]-1)*46+(2*yr)+(4*yt)
            y[(k1,k2)]=y3       

print ("y[i,j]=",y)

m.update()

# Decision variables
x={}
for i in sourceblock:
    for j in destblock:
        for t in shifts:
            x[i,j,t]=m.addVar(lb=0.0,ub=2.0, vtype=GRB.INTEGER,name="x[%s,%s,%s]"%(i,j,t))

m.update()        
#Constraints

# total number of yard cranes moving from block i to block j at each time period t are no more than one

for t in shifts:
    for i in sourceblock:
        cont_1=m.addConstr(quicksum(x[i,j,t] for j in destblock)<=2)
##      
###the number of yard cranes moving from block j to block i are no more than two
##
for t in shifts:
    for j in destblock:
        cont_2=m.addConstr(quicksum(x[i,j,t] for i in sourceblock)<=2)
#
# total number of yard cranes moving from block j to block i for each time period t are not less than the required number of yard cranes that needs to be delivered to block i
#
for t in shifts:
    for j in sourceblock:
        cont_3=m.addConstr((H[j,t]-b[j,t])<=quicksum(x[i,j,t] for i in sourceblock))        

#ensures no yard cranes moves from block ⅈ to any block j at each time period t if it’s number of required yard cranes are less than the number of yard cranes already available at the block.
for t in shifts:
    for j in destblock:
        if b[j,t]<=H[j,t]:
            cont_5=m.addConstr(quicksum(x[j,i,t] for i in sourceblock)==0)

#ensures the total number of yard cranes remaining at block j remains satisfactory after some YC(s) left block j to all blocks at each time period t.           
for t in shifts:
    for j in destblock:
        cont_6=m.addConstr(abs(b[j,t]-H[j,t])>=quicksum(x[j,i,t] for i in sourceblock))  

#ensures that the number of yard cranes moving along a row of blocks are non-negativity.
for t in shifts:
    for i in sourceblock:
        for j in destblock:
            cont_6=m.addConstr(x[i,j,t]>=0)
        
# objective function
m.setObjective(quicksum(x[i,j,t] * y[i,j] * 0.0085 for i in sourceblock for j in destblock for t in shifts),GRB.MINIMIZE)

#print(quicksum(x[i,j,t] * y[i,j] for i in sourceblock for j in destblock for t in shifts)
        
m.write("mod.lp")
#m.computeIIS()
#m.write('modi.ilp')
m.optimize()
m.printAttr("x","x*")
