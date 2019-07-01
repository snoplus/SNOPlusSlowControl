import numpy as np
pi = np.pi
eps = 0
R_b = 33.5*2.54
R_s = 42*2.54
DtoR = pi/180
Theta_D = [50,170,290]
theta_d = [31,80,140,170,200,260,320]
Theta = [i*DtoR for i in Theta_D]
theta = [j*DtoR+eps for j in theta_d]
B = [[R_b*np.sin(ii),R_b*np.cos(ii),0] for ii in Theta]
X = [R_s*np.sin(i) for i in theta]
Y = [R_s*np.cos(i) for i in theta]
offset = [-0.52008,-0.10307,5.8482,0,0,0]
