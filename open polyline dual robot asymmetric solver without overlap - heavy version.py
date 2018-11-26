# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 10:39:18 2018

@author: יניב אשרת
"""

import numpy as np
import pandas as pd
import random
from timeit import default_timer as timer
import itertools
from time import gmtime, strftime
import sys

   
#--------------------------------------------------------------------------
def random_step(robot_id, robot_location, robot_direction, Pr, Pl):
    
    if robot_direction == 1:
        coin = Pr[robot_id,robot_location]
    else:
        coin = Pl[robot_id,robot_location]   
    val = random.random() # flip the coin
    #print('coin=',coin, 'val=',val)
    if val > coin:
        return(-1)
    return(1)
#----------------------------------------------------------------------
#this function simulates patrol N times and returns the ratio of successful catch
def compute_ppd(intruder, robot1_start, robot2_start, Pr, Pl, N):
    catch_count = np.zeros([4])
    round_counter = 0
    
    for a in [-1,1]:
        for b in [-1,1]:
            #print('robot1=',robot1_start,'robot2=',robot2_start, 'intruder=',intruder)
            for n in range(N):        
                robot1_location = robot1_start
                robot2_location = robot2_start
                robot1_direction = a
                robot2_direction = b
                #print('start game: intruder=', intruder,'location 1=', robot1_location, 'location 2=', robot2_location, 'direction1=', robot1_direction, 'direction2=', robot2_direction)
                for i in range(T[intruder]):
                    robot1_direction = robot1_direction * (random_step(0, robot1_location, robot1_direction, Pr, Pl))
                    robot1_location = robot1_location + robot1_direction
                    #if robot2 is already in the new location of robot1 then robot1 moves to the other direction
                    if robot1_location == robot2_location:
                        robot1_location = robot1_location - 2
                        robot1_direction = robot1_direction * (-1)
                        #print('collision prevention robot 1')
                    
                    robot2_direction = robot2_direction * (random_step(1, robot2_location, robot2_direction, Pr, Pl))
                    robot2_location = robot2_location + robot2_direction
                    if robot2_location == robot1_location:
                        robot2_location = robot1_location + 2
                        robot2_direction = robot2_direction * (-1)
                        #print('collision prevention robot 2')
                    
                    #print('location1=', robot1_location, 'location2=', robot2_location, 'direction=', robot1_direction) 
                    if (robot1_location == intruder):
                        #print('gotcha 1')
                        catch_count[round_counter] =  catch_count[round_counter] + 1
                        break
                    if (robot2_location == intruder):
                        #print('gotcha 2')
                        catch_count[round_counter] =  catch_count[round_counter] + 1
                        break
            round_counter = round_counter + 1

    #print('configuration', intruder,robot1_start,robot2_start, 'catch ratio =', catch_count/N)            
    return(catch_count/N)
#------------------------------------------------------------------------
def simulate(d,P1,P2,N):
  
    #for a in range(d):
     #   for b in range(d):
      #      mat[a,b] = compute_ppd(a,b,P,N)

    mat = np.empty((d,d,d),np.ndarray)
    Pr = np.zeros((2,d))
    Pl = np.zeros((2,d))

    Pr[0,0:d//2+1] = P1
    #Pr[0,0:d//2+1] = [1,.7,1,.5,1,0]
    Pl[0,0:d//2+1] = P2

    Pr[1,:] = Pl[0,:][::-1]
    Pl[1,:] = Pr[0,:][::-1]
 
    minval = 1
    for a in range(d): #intruder
        for b in range(d//2+1): #robot1
            for c in range(max(d//2-1,b+1),d): #robot2
                mat[a,b,c] = compute_ppd(a,b,c,Pr,Pl,N)
                if ((mat[a,b,c]).min() < minval):
                    minval = (mat[a,b,c]).min()
                    ret_val = mat[a,b,c]
                    
    return(ret_val)
              
"""-----------------------------------------------------------------------"""
PYTHONUNBUFFERED = "true"
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
first_timer = timer() 
start = timer()
#-------------------------------------
#mode = 'solver' #optimizer
#method = 1 #1 for simulator, 2 for function matrix 
d = 10
#t = 6
N = 1000
T = np.array([6,6,6,6,6,6,6,6,6,6])
#use_matrices = True
resolution = 0.1
stack_size = 4

if (T.min()<d//2):
    print('t is to small, intruder will penetrate with probability 1')
    sys.exit(0)
if (T.min()>d-2):
    print('t is too big, deteministic patrol will do')
    sys.exit(0)
   
start = timer()  
  
print('Commencing Variant P function matrix production')
print('Line length (d) =', d, ', T=', T)

start = timer()   
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})     

MaxMinPPD = np.zeros([4])
'''
#build the iterator
my_iter=[]
my_iter.append([1]) #entering the first (leftmost) value = 1
num = 2 #int((.6/resolution)+1)
print('num=',num)
values = np.linspace(.5,1.0,num)
print('The iterator:')
print(values)
print(flush=True)
for i in range(1,d//2):
    my_iter.append(values) #entering the middle values
my_iter.append([0]) #entering the last (rightmost) value=0

number_of_steps = int(num**(d-2))
'''

 # A trial with shirt iterator - only 2 middle values in each direction iterate
my_iter=[]
my_iter.append([1]) #entering the first (leftmost) value = 1
my_iter.append([1])
num = 2 #int((.6/resolution)+1)
print('num=',num)
values = np.linspace(.5,1.0,num)
print('The iterator:')
print(values)
print(flush=True)
for i in range(1,3):
    my_iter.append(values) #entering the middle values
my_iter.append([1]) 
my_iter.append([0]) #entering the last (rightmost) value=0

number_of_steps = int(num**(4)) 


print('my_iter=', my_iter)
reversed_iter = my_iter[::-1]
print('reversed_iter', reversed_iter)

#build the stack of best results
defaultp = np.zeros(d)
my_tuple = [MaxMinPPD,defaultp,defaultp]
stack=[]
disc_list = pd.DataFrame(stack) #empty DataFrame for writing to disc
for i in range(stack_size):
    stack.append(my_tuple)
stack_counter = 0
#print(stack)
#print('aaa=',(stack[stack_size-1])[1])

#building a DataFrame for saving to disc



print('Commencing dual robot asymmetric solver, d=',d,', T=',T,', N=',N)
print('resolution=',resolution, ', number of steps=',number_of_steps)
print('starting at',strftime("%d.%m.%Y %H+2:%M:%S", gmtime()))
print(flush=True)

MaxMinVector = [defaultp,defaultp]
counter = 0
first_double_check_counter = 0
second_double_check_counter = 0
third_double_check_counter = 0
major_double_check_counter = 0
work_time = timer()
last_time = timer()

for combination1 in itertools.product(*my_iter):
    for combination2 in itertools.product(*reversed_iter):    
        counter = counter + 1
        #start_loop = timer()
        #print(combination)
        calc_time = timer()
        local_maxmin = simulate(d,combination1,combination2,N)
        basic_calc = timer()-calc_time
        #if (counter % 500 == 1):
         #   print('===')
          #  print('counter=',counter,', basic simulation took %3.3f' % (timer() - calc_time), 'sec, result=%3.3f' % local_maxmin)
        #print(local_maxmin)

# in double-check mode, new best result is checked again in the matrices   
        if local_maxmin.min() > (((stack[stack_size-1])[0]).min()*0.9): #factor 0.9 to avoid miss
            print('===')
            print('counter=',counter)
            print('basic simulation took %3.3f' % basic_calc,'value=', local_maxmin)
            calc_time = timer()
            #local_maxmin = simulate(d,combination,5*N)
            print('first double check (Nx5) - DISABLED')
            #print('first double check (Nx5), took %3.3f' % (timer()-calc_time),'sec, result=', local_maxmin)
            first_double_check_counter = first_double_check_counter + 1
            if local_maxmin.min() > (((stack[stack_size-1])[0]).min()*0.9): #factor 0.9 to avoid miss
                #print('second double check (Nx50 - DISABLED)')
                calc_time = timer()
                local_maxmin = simulate(d,combination1,combination2,15*N)
                print('second double check (Nx15), took %3.3f'% (timer()-calc_time),'sec, result=', local_maxmin)
                second_double_check_counter = second_double_check_counter + 1
                if local_maxmin.min() > ((stack[stack_size-1])[0]).min():
                    #print('third double check (Nx500) - DISABLED')
                    #local_maxmin = simulate(d,combination,500*N)
                    third_double_check_counter = third_double_check_counter + 1
                    if local_maxmin.min() > ((stack[stack_size-1])[0]).min():
                        #print('major double check for ppd',local_maxmin,'vector',np.around(combination,decimals=3),flush=True)
                        #local_maxmin = min_matrix(final_mat,combination[1:d-1])
                        #major_double_check_counter = major_double_check_counter + 1
                        #if local_maxmin > (stack[stack_size-1])[0]:
                        print('new maxmin enters list', local_maxmin,'. Lowest value in stack=',(stack[stack_size-1])[0])
                        print('counter=', counter,'out of', number_of_steps, ',%3.3f' % (counter*100/number_of_steps), '%', flush=True)
                        stack[stack_size-1] = [local_maxmin,combination1,combination2]
                        stack.sort(key=lambda tup: (tup[0]).min(), reverse=True)
                        stack_counter = stack_counter + 1
                        if stack_counter == stack_size:
                            print('cleaning stack')
                            i = 0
                            while (i < stack_size):
                                if ((stack[i])[0]).min() > MaxMinPPD.min():
                                    print('current MaxMinPPD:', MaxMinPPD)
                                    print('stack value number',i,'=',(stack[i])[0],'for vector',(stack[i])[1],(stack[i])[2])
                                    #strong simulation
                                    calc_time = timer()
                                    val = simulate(d,(stack[i])[1],(stack[i])[2],200000)
                                    #val = simulate(d,t,combination,1000000)
                                    print('200,000 simulation took %3.3f'% (timer()-calc_time))                          
                                    print('value as computed in 200,000-simulation is',val)                                
                                    major_double_check_counter = major_double_check_counter + 1                             
                                    print('The former MaxMinPPD=',MaxMinPPD)
                                    if val.min() > MaxMinPPD.min():
                                        print('New MaxMinPPD =',val)
                                        MaxMinPPD = val
                                        MaxMinVector = [(stack[i])[1],(stack[i])[2]]
                                        #clean the satck
                                        new_tuple = [MaxMinPPD,MaxMinVector]
                                        stack=[]
                                        for i in range(stack_size):
                                            stack.append(new_tuple)
                                        for i in range(stack_size):
                                            print(((stack[i])[0]), (np.around((stack[i])[1],decimals=3)))
                                        #clean_stack(stack,stack_counter,MaxMinPPD,MaxMinVector)
                                        stack_counter = 0
                                        print()
                                        break;
                                    else:
                                        print('it was false alarm')
                                i = i+1
                        
        if (counter % 1000 == 0):
            #write best result to disc
            disc_list = pd.DataFrame(stack)
            disc_list.to_csv('best_result')
            
            print()
            print('round time:', np.around(timer()-last_time),'sec')
            print('average roung time:', np.around(((timer()-work_time)/counter*1000),decimals=3),'sec')
            last_time = timer()
            print('resolution =', resolution)
            print('counter=', counter,'out of', number_of_steps, ',%3.3f' % (counter*100/number_of_steps), '%')
            print('major double checks:', major_double_check_counter)
            print('stack counter:', stack_counter)
            print('Best result so far:')
            #print('MaxMinPPD=', (stack[0])[0], 'With P=',(np.around((stack[0])[1],decimals=3)))
            print('MaxMinPPD=', MaxMinPPD,'With P=',(np.around((MaxMinVector),decimals=3)))
            print('current position:', (np.around(combination1,decimals=3)),(np.around(combination2,decimals=3)))
            print('time from begining: %3.3f' % ((timer()-first_timer)/60), 'min')     
            print(flush=True)

#finalizing the process
        
print('cleaning stack for conclusion')
i = 0
while (i < stack_size):
    if ((stack[i])[0]).min() > MaxMinPPD.min():
        print('current MaxMinPPD:', MaxMinPPD)
        print('stack value number',i,'=',(stack[i])[0],'for vector',(stack[i])[1])
        
        #strong simulation
        val = simulate(d,(stack[i])[1],(stack[i])[2],200000)
        #val = simulate(d,t,combination,1000000)
        print('value as computed in 100,000-simulation is',val)  
            
        major_double_check_counter = major_double_check_counter + 1        
        if val.min() > MaxMinPPD.min():
            MaxMinPPD = val
            print('New MaxMinPPD =', MaxMinPPD)
            MaxMinVector = [(stack[i])[1],(stack[i])[2]]
            break;
        else:
            print('it was false alarm')            
    i = i+1
print()
print('Concluding MinMax ,search, d=',d,'T=',T,'N=',N)
print('stack size=', stack_size)
print('resolution=',resolution, ', number of steps=',number_of_steps)
#print('MaxMinPPD=', (stack[0])[0], 'With P=',(np.around((stack[0])[1],decimals=3)))
print('MaxMinPPD=', MaxMinPPD,'With P=',(np.around((MaxMinVector),decimals=3)))
print('my_iter=', my_iter)
print('first double checks:', first_double_check_counter)
print('second double checks:', second_double_check_counter)
print('third double checks:', third_double_check_counter)
print('major double checks:', major_double_check_counter)
print('run time: %3.3f' % ((timer() - first_timer)/60),'min') 
