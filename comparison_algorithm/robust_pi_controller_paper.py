import numpy as np
import cvxpy as cp
import pdb
"""Theorem 2 : Robust indirect-type ILC
from paper 'PI based indirect-type iterative learning control for batch processes with time-varying uncertainties: A 2D FM model based approach' Journal of process control,2019"""
'1. the dimensions of the state space'
m=2
n=1
r=1
l=1
'2. The original batch system'
A=np.array([[1.607, 1.0], [-0.6086, 0.0]])*0.5
B=np.array([[1.239], [-0.9282]])
C=np.array([[1.0,0.0]])
E=np.array([[1,0],[0,1]])
F_A=A*0.2
F_B=B*0.1



'3. The PI control law'
K_p=np.array([[0.42925293]])
K_i=([[0.07341834378229248]])

'4. the robust indirect-type ILC '
sigma_t=1.
sigma_k=1.
# define the unknown parameters
Q_t= cp.Variable((m+2*l,m+2*l),pos=True)
Q_k= cp.Variable((m+2*l,m+2*l),pos=True)
Q_1= cp.Variable((m,m),pos=True)
Q_2= cp.Variable((l,l),pos=True)
Q_3= cp.Variable((l,l),pos=True)
L_hat_1=cp.Variable((l,l))
L_hat_2=cp.Variable((l,l))
L_hat_3=cp.Variable((l,l))
varepsilon=cp.Variable(1,pos=True)
gamma_ILC=cp.Variable(1,pos=True)
Q=cp.bmat([[Q_1,np.zeros((m,2*l))],
           [np.zeros((l,m)),Q_2,np.zeros((l,l))],
           [np.zeros((l,m+l)),Q_3]])
Omega_1=cp.bmat([[(A-B@(K_p+K_i)@C)@Q_1,B@(K_i@Q_2+(K_p+K_i)@L_hat_1),B@(K_p+K_i)@L_hat_2],
                 [-C@Q_1,L_hat_1+Q_2,L_hat_2],
                 [-C@(A-B@(K_p+K_i)@C)@Q_1,-C@B@(K_i@Q_2+(K_p+K_i)@L_hat_1),-C@B@(K_p+K_i)@L_hat_2]
                 ])

Omega_2=cp.bmat([[np.zeros((m,m)),np.zeros((m,l)),B@(K_p+K_i)@L_hat_3],
                 [np.zeros((l,m)),np.zeros((l,l)),L_hat_3],
                 [np.zeros((l,m)),np.zeros((l,l)),Q_3-C@B@(K_p+K_i)@L_hat_3]
                 ])
Omega_3=cp.bmat([[np.zeros((m,l))],
                 [np.zeros((l,l))],
                 [Q_3]
                 ])
Omega_4=cp.bmat([[Q_1@(F_A-F_B@(K_p+K_i)@C).T],
                 [(K_i@Q_2+(K_p+K_i)@L_hat_1).T@F_B.T],
                 [L_hat_2.T@(K_p+K_i).T@F_B.T]
                 ])
Omega_5=cp.bmat([[np.zeros((m,m))],
                 [np.zeros((l,m))],
                 [L_hat_3.T@(K_p+K_i).T@F_B.T]
                 ])
Psi=np.block([[E],
              [np.zeros((l,m))],
              [-C@E]])
D_g=np.block([[np.eye(m)],
              [np.zeros((l,m))],
              [-C]])


if l==1:
    inmatrix_gamma_ILC=cp.reshape(-gamma_ILC,shape=[1,1])

else:
    inmatrix_gamma_ILC=-gamma_ILC*np.eye(n)
"5. Define the inequality"
inequalitymatrix=cp.bmat([[-Q+varepsilon*Psi@Psi.T,Omega_1,Omega_2,D_g,np.zeros((m+2*l,l)),np.zeros((m+2*l,m))],
                          [Omega_1.T,-Q_t,np.zeros((m+2*l,m+2*l)),np.zeros((m+2*l,m)),Omega_3,Omega_4],
                          [Omega_2.T,np.zeros((m+2*l,m+2*l)),-Q_k,np.zeros((m+2*l,m)),np.zeros((m+2*l,l)),Omega_5],
                          [D_g.T,np.zeros((m,m+2*l)),np.zeros((m,m+2*l)),-gamma_ILC*np.eye(m),np.zeros((m,l)),np.zeros((m,m))],
                          [np.zeros((l,m+2*l)),Omega_3.T,np.zeros((l,m+2*l)),np.zeros((l,m)),inmatrix_gamma_ILC,np.zeros((l,m))],
                          [np.zeros((m,m+2*l)),Omega_4.T,Omega_5.T,np.zeros((m,m)),np.zeros((m,l)),-varepsilon*np.eye(m)]
                          ])

'6. Define the contrains'
constraints = [inequalitymatrix << 0]
constraints += [sigma_t*Q_t+sigma_k*Q_k << Q]
prob=cp.Problem(cp.Minimize(gamma_ILC),constraints)
prob.solve(solver=cp.SCS, verbose=True,max_iters=1000000)
L_1=L_hat_1.value@np.linalg.inv(Q_2.value)
L_2=L_hat_2.value@np.linalg.inv(Q_3.value)
L_3=L_hat_3.value@np.linalg.inv(Q_3.value)
print('L1',L_1)
print('L2',L_2)
print('L3',L_3)

#L1 [[-0.14558297]]
#L2 [[-6.38077942e-14]]
#L3 [[1.0095119]]


