import sys
import sketch
import athlet

#Class for performing iterations
class Iterate:
    #Class for storing distributions of state variables
    class State:
        def __init__(self, NZ, NR):
            self.NZ=NZ
            self.NR=NR

            self.p=[]
            self.tf=[]
            self.tc=[]
            self.tm=[]
            self.rho=[]

            self.keff=0
            for i in range(NR):
                self.p.append([])
                self.tf.append([])
                self.tc.append([])
                self.tm.append([])
                self.rho.append([])
                for j in range(NZ):
                    self.p[-1].append(0)
                    self.tf[-1].append(0)
                    self.tc[-1].append(0)
                    self.tm[-1].append(0)
                    self.rho[-1].append(0)

    def __init__(self, NZ, NR, pwr, pwrlvl=1.0, init='null', idx0=0, resdir="./res/"):
        self.resdir=resdir
        self.NZ=NZ
        self.NR=NR
        self.pwr=pwr
        self.pwrlvl=pwrlvl
        self.idx0=idx0

        self.steps=[]   #array for State objects
        self.diffs=['null'] #array for power differences between iterations

        #Setting starting power profie: null, uniform or read from file (TBA)
        if(init=='null'):
            self.steps.append(self.State(self.NZ, self.NR))
            self._thermal()     #the temperature profile has to be calculated
        elif(init=='uni'):
            self.steps.append(self.State(self.NZ, self.NR))
            for i in range(self.NR):    #uniform power values are set (egyébként szar)
                for j in range(1,self.NZ):
                    self.steps[-1].p[i][j]=1000000*self.pwr/(self.NZ-2)/self.NR/312    #pin power in W
            self._thermal()          #the temperature profile has to be calculated
        elif(init=='read'):
            self.steps.append(self.State(self.NZ, self.NR))
            self._read_state(self.idx0)

    def _read_state(self, idx):
        print("define through inheritence")

    def iterate(self):
        self.steps.append(self.State(self.NZ, self.NR))
        self._neut()
        self._thermal()
        self.diffs.append(self._diff(self.steps[-1].p, self.steps[-2].p))

    #get relative difference in %
    def _diff(self, act, prev):
        d=[]
        for i in range(len(act)):
            d.append([])
            for j in range(1,len(act[i])-1):        #loops through the power values
                d[-1].append(100*(act[i][j]-prev[i][j])/act[i][j])
        return d

    def write_diff(self, idx):
        fout=open("{}diff_{}--{}-{}.txt".format(self.resdir, self.pwrlvl*100, self.idx0+idx-1, self.idx0+idx), "w")
        fout.write("power differences between state {} and {}\n".format(self.idx0+idx-1, self.idx0+idx))
        maxsum=0
        maxidx=0
        for i in range(self.NR):
            fout.write("Assembly {}\n".format(i+1))
            fout.write(("Layer\tDiff[%]\n").expandtabs(10))
            diffsum=0
            for j in range(self.NZ-2):
                fout.write("{:02d}\t{:+.3f}\n".format(j+1, self.diffs[idx][i][j]).expandtabs(10))
                diffsum+=abs(self.diffs[idx][i][j])
            fout.write("Sum:\t{:.3f}\n".format(diffsum).expandtabs(10))
            fout.write('\n')
            if(diffsum>maxsum): 
                maxsum=diffsum
                maxidx=i+1
        fout.write("Max: {:.3f} at: {:02d}\n".format(maxsum, maxidx).expandtabs(10))
        fout.close()

    def _thermal(self):
        print("define through inheritence")

    def _neut(self):
        print("define through inheritence")

class ATHLET(Iterate):
    th=athlet.ATHLQ1T10_PINTVS2M()
    #th=athlet.CORE_PIN3_GAP_HeWL_CW_Q1T10()

    def __init__(self, NZ, NR, pwr, pwrlvl=1.0, init='null', idx0=0, resdir="./res/"):
        super(ATHLET, self).__init__(NZ, NR, pwr, pwrlvl, init, idx0, resdir)
        self.th.setvars([self.pwrlvl])

    def _thermal(self):
        i=self.idx0+len(self.steps)-1
        self.th.settime(i)
        self.th.setQ(self.steps[-1].p)  #set FA power in kW
        #self.th.setQ(1000*self.steps[-1].p/312)  #set pin power in W
        self.th.run(i,i-1)
        out=self.th.output(i)

        for i in range(self.NR):
            for j in range(1, self.NZ-1):
                self.steps[-1].tf[i][j]=out[0][i*(self.NZ-2)+j-1]
                self.steps[-1].tc[i][j]=out[1][i*(self.NZ-2)+j-1]
            for j in range(self.NZ):
                self.steps[-1].tm[i][j]=out[2][i*self.NZ+j]
                self.steps[-1].rho[i][j]=out[3][i*self.NZ+j]

class SKETCH(Iterate):
    nf=sketch.SKETCH()

    def __init__(self, NZ, NR, pwr, pwrlvl=1.0, init='null', idx0=0, resdir="./res/"):
        super(SKETCH, self).__init__(NZ, NR, pwr, pwrlvl, init, idx0, resdir)
        self.nf.setpow(self.pwr)

    def _neut(self):
        self.nf.settemp(self.zcoords, self.steps[-2].tf, self.steps[-2].tc, self.steps[-2].tm, self.steps[-2].rho)   #old format
        #self.nf.settemp(self.steps[-2].tf, self.steps[-2].tm, self.steps[-2].rho)   #new format
        self.nf.run()
        pout=self.nf.output()

        for i in range(self.NR):
            for j in range(1,self.NZ-1):
                self.steps[-1].p[i][j]=pout[i*(self.NZ-2)+j-1]  #FA power in kW
                #self.steps[-1].p[i][j]=1000*pout[i*(self.NZ-2)+j-1]/312  #pin power in W

class SKETCH_ATHLET(SKETCH, ATHLET):
    #legacy, valamit kell vele csinálni
    headers=['Layer', 'coord[m]', 'P[kW]', 'Tf[K]', 'Tc[K]', 'Tm[K]', 'rhom[g/cm^3]']
    zcoords=[0.119, 0.489, 0.859, 1.229, 1.599, 1.969, 2.339, 2.709, 3.079, 3.449, 3.819, 4.078] 

    def write_state(self, idx):
        fout=open("{}iteration_{}--{}.txt".format(self.resdir, self.pwrlvl*100, self.idx0+idx), "w")

        try:
            fout.write("Iteration: {}: power {}%, keff={}\n".format(self.idx0+idx, self.pwrlvl*100, self.steps[idx].keff))

            for i in range(self.NR):
                fout.write("Assembly {}\n".format(i+1))
                fout.write(('\t'.join(self.headers)+'\n').expandtabs(10))
                for j in range(self.NZ):
                    fout.write("{:02d}\t{:.3f}\t{:.3f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.4f}\n".format(j, self.zcoords[j], self.steps[idx].p[i][j], self.steps[idx].tf[i][j], self.steps[idx].tc[i][j], self.steps[idx].tm[i][j], self.steps[idx].rho[i][j]).expandtabs(10))
                fout.write('\n')

        except IndexError as e:
            fout.write("Writing faied: "+str(e))
            print("Writing faied: ", e)

        fout.close()

    def _read_state(self, idx):
        fin=open("{}iteration_{}--{}.txt".format(self.resdir, self.pwrlvl*100, idx), "r")
        line=fin.readline()
        for i in range(self.NR):
            line=fin.readline()
            line=fin.readline()
            for j in range(self.NZ):
                line=fin.readline()
                self.steps[-1].p[i][j]=float(line.split()[2])
                self.steps[-1].tf[i][j]=float(line.split()[3])
                self.steps[-1].tc[i][j]=float(line.split()[4])
                self.steps[-1].tm[i][j]=float(line.split()[5])
                self.steps[-1].rho[i][j]=float(line.split()[6])
            line=fin.readline()
        fin.close()

def main():
    #---Parameters of the model----
    core_power_nominal=2965.0 #in MW 2965.0 MW for KLN3
    N_assembly=163
    assembly_power_nominal=core_power_nominal/N_assembly  #in MW
    N_pin=312
    pin__power_nominal=assembly_power_nominal/N_pin     #in MW

    #---Parameters of the problem
    ax_layers=12
    rad_layers=N_assembly
    power=core_power_nominal

    #---Initializing the iteration---
    pwrlvl=float(sys.argv[1])/100   #argv[1]: power level in % nominal
    if(int(sys.argv[2])==0):        #argv[2]: starting state index
        it=SKETCH_ATHLET(NZ=ax_layers, NR=rad_layers, pwr=power*pwrlvl, pwrlvl=pwrlvl, init="null")
        it.write_state(0)
    else:
        it=SKETCH_ATHLET(NZ=ax_layers, NR=rad_layers, pwr=power*pwrlvl, pwrlvl=pwrlvl, init="read", idx0=int(sys.argv[2]))
    
    #---Iterative cycle---
    for i in range(it.idx0,it.idx0+int(sys.argv[3])):  #argv[3] number of steps
        it.iterate()
        it.write_state(i-it.idx0+1)
        it.write_diff(i-it.idx0+1)

def test():
    power_nominal=2965.0 #in MW 2965.0 MW for KLN3
    assembly_power_nominal=18.4049  #in MW

    pwrlvl=float(sys.argv[1])/100   #argv[1]: power level in % nominal
    it=SKETCH_ATHLET(NZ=12, NR=163, pwr=power_nominal*pwrlvl, pwrlvl=pwrlvl, init="read", idx0=int(sys.argv[2]))
    it.write_state(0)

if(__name__=="__main__"): main()
    
