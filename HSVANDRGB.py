import numpy as np
from matplotlib import pyplot as plt
opcje={"1-0":(lambda a: np.linspace(1,0,a)),
       "0-1":(lambda a: np.linspace(0,1,a)),
       "0":(lambda a: np.zeros(a)),
       "0+x":(lambda a: np.zeros(a[0])+a[1]),
       "x-x":lambda a: np.linspace(a[0],a[1],a[2])}
interpreter={"1-0":(lambda c,x:-1*x+1 ),#gdzie c to długość x
       "0-1":(lambda c,x:x ),
       "0":(lambda a,b:0),
       "0+x":(lambda a,b: a[1]),
       "x-x":(lambda a,b: b*(a[1]-a[0])+a[0])}
suma={"1-0":(lambda a:a),
       "0-1":(lambda a:a ),
       "0":(lambda a:a),
       "0+x":(lambda a: a[0]),
       "x-x":(lambda a: a[2])}
def interpreter_warunkowy1(pytanie,gradient,wartosc):
    gradient1=gradient.split(", ")
    sum1=np.sum(np.array([suma[gradient1[i]](wartosc[i])for i in range(len(gradient1))]))
    sum2=0
    for i in range(len(wartosc)):
        if pytanie>=sum2/sum1 and pytanie <=(sum2+suma[gradient1[i]](wartosc[i]))/sum1:
            return interpreter[gradient1[i]](wartosc[i],(pytanie-sum2/sum1)/(suma[gradient1[i]](wartosc[i])/sum1))
        sum2+=suma[gradient1[i]](wartosc[i])
    return 1.0
def interpreter_warunkowy(pytanie,gradient,wartosc):
    pytanie1=pytanie.copy()
    for i in range(pytanie.shape[0]):
        for j in range(pytanie.shape[1]):
            pytanie1[i,j]=interpreter_warunkowy1(pytanie[i,j], gradient, wartosc)
    return pytanie1


def my_append(a, b):
    for i in b:
        a = np.append(a, i)
    return a
def laduj_opcje(a,b,y=70):
    a=a.split(", ")
    ax=opcje[a[0]](b[0])
    a,b=a[1:],b[1:]
    x=my_append(ax,[opcje[a[i]](b[i]) for i in range(len(a))])
    return np.array([x for i in range(y)])
def kreacja3x(ott,shapes):
    regebl = np.zeros(shapes)
    for i in range(3):
        regebl[:, :, i] = ott[i].reshape(shapes[0:2])
    return regebl

class HSV:
    def __init__(self,array):
        self.obraz=array
    def toRGB(self):
        self.RGBt=np.zeros(self.obraz.shape)
        hue,sat,val=np.copy(self.obraz[:,:,0]),np.copy(self.obraz[:,:,1]),np.copy(self.obraz[:,:,2])
        hue/=60
        i=np.floor(hue)
        f=hue-i
        p=val*(1-sat)
        q = val * (1 - (sat * f))
        t=val*(1-(sat*(1-f)))
        self.RGBt[:,:,0]=((i==0)*val+(i==1)*q+(i==2)*p + (i==3)*p+(i==4)*t+(i==5)*val)*(val!=0)
        self.RGBt[:, :, 1] = ((i == 0) * t + (i == 1)*val +(i==2) * val + ( i == 3) * q + (i == 4 )*p+( i==5) *p) * (val != 0)
        self.RGBt[:, :, 2] = ((i == 0 )*p+( i==1) * p + (i == 2) * t + (i == 3 )*val+( i==4) * val + ( i == 5) * q) * (val != 0)
        return self.RGBt
class RGB:
    def __init__(self,array):
        self.obraz=array
    def toHSV(self):
        red,grn,blu=np.copy(self.obraz[:,:,0]),np.copy(self.obraz[:,:,1]),np.copy(self.obraz[:,:,2])
        x=np.fmin(np.fmin(red,grn),blu)
        val=np.fmax(red,np.fmax(grn,blu))
        f=(red==x)*(grn-blu)+(red!=x)*((grn==x)*(blu-red)+(grn!=x)*(red-grn))
        i=(red==x)*3+(red!=x)*((grn==x)*5+(grn!=x))
        hue=(x!=val)*(((i-f/(val-x))*60)%360)
        sat=(x!=val)*((val-x)/val)
        return np.array([hue,sat,val]).T
data2array=lambda ax:np.array(list(map(float,ax.split())))
#mamy podfunkcję lambda, która znajduje minimalną wysokość i maksymalną wysokość, a następnie
procent=lambda a:(lambda b,c: (a-c)/(b-c))(np.max(a),np.min(a))
#def calculate_value(angle_deg):
#    if angle_deg >= 90:
#        return 0
#    else:
#        return -1/180 * angle_deg + 1
def calculate_value(angle_deg):
    a=0
    if angle_deg >= 90:
        a= 0
    else:
        a=-1/90 * angle_deg+1
    return a
def rozciaganie_histogramu(tab):
    vmax=0.55
    vmin=0.4
    imax=1
    nowatablica=imax/(vmax-vmin)*(tab-vmin)
    k=(nowatablica>0) == (nowatablica<1)
    nowatablica=nowatablica*(nowatablica>=0)
    nowatablica=nowatablica*(nowatablica<=1) + (nowatablica>1)
    return (nowatablica,k)
class Dem:
    def __init__(self):
        f1=open("big.dem","r")
        f=f1.readlines()
        (self.w,self.h,self.o)=tuple(list(map(int,f[0].split())))
        self.o=self.o/100
        self.tablica=my_append(data2array(f[1]),[data2array(f[i]) for i in range(2,len(f))]).reshape(self.h,self.w)
        f1.close()
    def punkt_pierwszy(self):
        return procent(self.tablica)
    def wylicz_value(self,L):
        nowatablica=np.zeros(self.tablica.shape)
        def punkty(A,B,C,L):
            AB=B-A
            AC=C-A
            N=np.cross(AB,AC)
            N_length = np.linalg.norm(N)
            N_norm=N/N_length
            # Oblicz kąt między N a wektorem idącym do obserwatora
            cosine_angle = np.dot(N_norm, L) / (np.linalg.norm(N_norm) * np.linalg.norm(L))
            angle_rad = np.arccos(cosine_angle)
            angle_deg = np.degrees(angle_rad)
            return calculate_value(angle_deg)
        for i in range(self.w-1):
            for j in range(self.h-1):
                A=np.array([0,0,self.tablica[i,j]])
                B=np.array([0,self.o,self.tablica[i,j+1]])
                C=np.array([self.o,0,self.tablica[i+1,j]])
                nowatablica[i,j]=punkty(A,B,C,L)
            A=np.array([0,0,self.tablica[i,-1]])
            B=np.array([self.o,0,self.tablica[i+1,-1]])
            C=np.array([0,-self.o,self.tablica[i,-2]])
            nowatablica[i,-1]=punkty(A,B,C,L)
        for j in range(self.h-1):
            A=np.array([0,0,self.tablica[-1,j]])
            B=np.array([-self.o,0,self.tablica[-2,j]])
            C=np.array([0,self.o,self.tablica[-1,j+1]])
            nowatablica[-1,j]=punkty(A,B,C,L)
        A=np.array([0,0,self.tablica[-1,-1]])
        B=np.array([0,-self.o,self.tablica[-1,-2]])
        C=np.array([-self.o,0,self.tablica[-2,-1]])
        nowatablica[-1,-1]=punkty(A,B,C,L)
        return nowatablica
