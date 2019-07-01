import numpy as np
import datetime
import time
import config.dataconfig as dc
from scipy.misc import derivative
class PIDataConverter(object):
     def __init__(self):
         self.rope = []
         self.delz = 0
         self.dz = 6.5
         self.AV_Pos = []
         self.Xs = []
         self.Matrix = []
     
     def GetRopeValue(self,rope):
         del rope[1]
         self.rope = rope
         

     def partial_derivative(self,func,var=0,point=[]):
         args = point[:]
         def wraps(x):
             args[var] = x
             return func(*args)
         return derivative(wraps,point[var],dx=1e-6)

     def Get_dz(self):
         if self.delz<11.5:
            dz = 6.5
         else:
            dz = 6.5 + (self.delz-9)
         self.dz = dz
     

     def Calculate_Xs(self):
         Z = self.dz
         Xs_init = np.array([[dc.X[0],dc.Y[0],Z,0,0,0],
                            [dc.X[1],dc.Y[1],Z,0,0,0],
                            [dc.X[2],dc.Y[2],Z,0,0,0],
                            [dc.X[4],dc.Y[4],Z,0,0,0],
                            [dc.X[5],dc.Y[5],Z,0,0,0],
                            [dc.X[6],dc.Y[6],Z,0,0,0]])
         self.Xs = Xs_init

     def length_B1(self,x, y, z, Phi1, Phi2, Phi3):
         return (np.sqrt((((np.cos(Phi2)*np.cos(Phi3))*x+(-np.cos(Phi1)*np.sin(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.cos(Phi3))*y+(np.sin(Phi1)*np.sin(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.cos(Phi3))*z-dc.B[0][0])**2)+(((np.cos(Phi2)*np.sin(Phi3))*x+(np.cos(Phi1)*np.cos(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.sin(Phi3))*y+(-np.sin(Phi1)*np.cos(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.sin(Phi3))*z-dc.B[0][1])**2)+(((-np.sin(Phi2))*x+(np.sin(Phi1)*np.cos(Phi2))*y+(np.cos(Phi1)*np.cos(Phi2))*z-dc.B[0][2])**2)))


     def length_B2(self,x, y, z, Phi1, Phi2, Phi3):
         return (np.sqrt((((np.cos(Phi2)*np.cos(Phi3))*x+(-np.cos(Phi1)*np.sin(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.cos(Phi3))*y+(np.sin(Phi1)*np.sin(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.cos(Phi3))*z-dc.B[1][0])**2)+(((np.cos(Phi2)*np.sin(Phi3))*x+(np.cos(Phi1)*np.cos(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.sin(Phi3))*y+(-np.sin(Phi1)*np.cos(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.sin(Phi3))*z-dc.B[1][1])**2)+(((-np.sin(Phi2))*x+(np.sin(Phi1)*np.cos(Phi2))*y+(np.cos(Phi1)*np.cos(Phi2))*z-dc.B[1][2])**2)))

     def length_B3(self,x, y, z, Phi1, Phi2, Phi3):
           return (np.sqrt((((np.cos(Phi2)*np.cos(Phi3))*x+(-np.cos(Phi1)*np.sin(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.cos(Phi3))*y+(np.sin(Phi1)*np.sin(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.cos(Phi3))*z-dc.B[2][0])**2)+(((np.cos(Phi2)*np.sin(Phi3))*x+(np.cos(Phi1)*np.cos(Phi3)+np.sin(Phi1)*np.sin(Phi2)*np.sin(Phi3))*y+(-np.sin(Phi1)*np.cos(Phi3)+np.cos(Phi1)*np.sin(Phi2)*np.sin(Phi3))*z-dc.B[2][1])**2)+(((-np.sin(Phi2))*x+(np.sin(Phi1)*np.cos(Phi2))*y+(np.cos(Phi1)*np.cos(Phi2))*z-dc.B[2][2])**2)))

     def Calculate_Matrix(self):
           deriv = []
           j = 0
           while j < 6:
               n = 0
               temp = []
               while n < 6:
	           if j < 2:
                      Entrie = float(self.partial_derivative(self.length_B1,n,[self.Xs[j,0],self.Xs[j,1],self.Xs[j,2],self.Xs[j,3],self.Xs[j,4],self.Xs[j,5]]))
                 
                   elif j < 4:
                      Entrie = float(self.partial_derivative(self.length_B2,n,[self.Xs[j,0],self.Xs[j,1],self.Xs[j,2],self.Xs[j,3],self.Xs[j,4],self.Xs[j,5]]))
                  
                   else:
                      Entrie = float(self.partial_derivative(self.length_B3,n,[self.Xs[j,0],self.Xs[j,1],self.Xs[j,2],self.Xs[j,3],self.Xs[j,4],self.Xs[j,5]]))

                   temp.append(Entrie)
                   n = n + 1
               deriv.extend(temp)
               j = j + 1
           M = np.reshape(deriv,(6,6))
           Matrix = np.linalg.inv(M)
           self.Matrix = Matrix

     def Rope_to_AVPos(self,rope):
           x = []
           self.GetRopeValue(rope)
           self.Get_dz()
           self.Calculate_Xs()
           self.Calculate_Matrix()
           for i in range(6):
              x.append(np.dot(self.Matrix[i,:],self.rope) + dc.offset[i])
           self.AV_Pos = x 
           self.delz = self.AV_Pos[2]
           return self.AV_Pos 
def main():
    Rope = [61.5,52.5,58.4,56.0,46.5,53.6]
    Test = PIDataConverter()
    for i in range(10):
       AVPOS = Test.Rope_to_AVPos(Rope)
       print("AVPOS= ",AVPOS)

if __name__ == '__main__':
   main()


