import os

#parent class for ATHLET calculations
class ATHLET:
    #exe="/mnt/pool/1/pazman.koppany/ATHLET/ATHLET_31A_release_x64/bin/athlet_exe.release.64.ifort/athlet31a.omp.64.ifort"
    exe="/home/pazmank/ATHLET/ATHLET_31A_release_x64/bin/athlet_exe.release.64.ifort/athlet31a.omp.64.ifort"
    #exe="/home/pazmank/ATHLET/ATHLET_31A_release_x64/bin/athlet_exe.release.64.ifort/athlet31a.release.64.ifort"

    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        self.fname=fname
        self.fold=fold
        self.setvars(vars)

    #runs the program with or without restart option
    def run(self, it=0, res=-1):
        self.settime(it, res)
        if(res<0):
            os.system("time "+self.exe+" "+self.fold+self.fname+" "+self.fname+" r"+str(it)+" -td "+self.fold+"out/")
        else:
            #os.system("time "+self.exe+" "+self.fold+self.fname+" "+self.fname+" r"+str(it)+" -td "+self.fold+"out/")
            os.system("time "+self.exe+" "+self.fold+self.fname+" "+self.fname+" r"+str(it)+" -td "+self.fold+"out/ -r r"+str(res)+" -rd "+self.fold+"out/")

    #sets the time steps
    def settime(self, it=0, res=-1, t0=800.0, tr=200.0):
        time=str(t0+it*tr)
        if(res<0):
            r="0"
        else:
            #r="0"
            r="1"
        timestr="@  MZEIT    MCPU  ICPUTM  MIZS       TE    SGEND\n600       0       0     0   %s 'DEFAULT'\n@  IWBER   IPUNC  ISREST\n%s       2       0"
        print("Updating time steps in ATHLET input...")
        fout=open(self.fold+"time.dat","w", encoding="ISO-8859-15")
        fout.write(timestr %(time, r))
        fout.close()
        print("Time steps in ATHLET input updated.")

    #setting some variables defined in the input file (like power level)
    def setvars(self, vars):
        print("Updating variables in ATHLET input...")
        fout=open(self.fold+"vars.dat","w", encoding="ISO-8859-15")
        fout.write("POWER.NZ=%s" %(str(vars[0])) )   #% of nominal power
        fout.close()
        print("Variables in ATHLET input updated.")

    #setting power distribution
    def setQ(self, p):
        print("define through inheritence")
    
    #extracting output data
    def output(self, it):
        print("Reading ATHLET output files...")

        #stripping the long output
        fin=open(self.fold+"out/"+self.fname+".r"+str(it)+".out", "r", encoding="ISO-8859-15")
        line=" "
        while(line!=""):
            line=fin.readline()
            if(line.find("BEGINNING OF ATHLET MAIN EDIT")!=-1):
                fout=open("out_temp.txt", "w")
                fout.write(line)
                line=fin.readline()
                while(line.find("END OF ATHLET MAIN EDIT")==-1):
                    fout.write(line)
                    line=fin.readline()
                fout.write(line)
                fout.close()
        fin.close()

        state=[]    #the desired return values depend on the output
        fin=open("out_temp.txt", "r", encoding="ISO-8859-15")
        self._getstate(fin, state)  #through inheritence
        fin.close()
        
        os.remove("out_temp.txt")

        print("ATHLET output files read.")

        return state

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        print("define through inheritence")
       
class ATHLQ1(ATHLET):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLET.__init__(self, fold, fname, vars)

    #setting power distribution
    #sets the power distribution for an input file with 1 layer radial heat source
    def setQ(self, p):
        print("Updating power distribution in ATHLET input...")
        fout=open(self.fold+"Q.dat","w", encoding="ISO-8859-15")

        for i in range(len(p)):
            fout.write("F001.1."+"{:d}".format(i+1)+"="+str(p[i])+"\n")

        for i in range(len(p)):
            for j in range(1,3):
                fout.write("F001."+"{:d}".format(j+1)+"."+"{:d}".format(i+1)+"=0.000\n")

        for i in range(len(p)):
            fout.write("C001.1."+"{:02d}".format(i+1)+"=0.000\n")
            fout.write("W001.1."+"{:02d}".format(i+1)+"=0.000\n")

        print("Power distribution in ATHLET input updated.")

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        print("define through inheritence")

class ATHLQ3(ATHLET):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLET.__init__(self, fold, fname, vars)

    #setting power distribution
    #sets the power distribution in the input file with 3 layers radial heat source
    def setQ(self, p):
        print("Updating power distribution in ATHLET input...")
        fout=open(self.fold+"Q.dat","w", encoding="ISO-8859-15")
    
        for i in range(len(p)):
            for j in range(3):
                fout.write("F001."+"{:d}".format(j+1)+"."+"{:d}".format(i+1)+"="+str(p[i]/3)+"\n")
    
        for i in range(len(p)):
            fout.write("C001.1."+"{:02d}".format(i+1)+"=0.000\n")
            fout.write("W001.1."+"{:02d}".format(i+1)+"=0.000\n")
    
        print("Power distribution in ATHLET input updated.")

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        print("define through inheritence")

class ATHLQ1T1(ATHLQ1):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLQ1.__init__(self, fold, fname)

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        line=" "
        while(line!=""):
            line=fin.readline()
            #TL: coolant temp.
            if(line.find("V-CHA                I/J PRESS      TFLUID     TL")!=-1):
                state.append([])
                line=fin.readline()
                state[-1].append(float(line.split()[5]))
                for i in range(1,12):
                    line=fin.readline()
                    state[-1].append(float(line.split()[3]))
            #ROF: coolant dens.
            elif(line.find("GBOR       MLI        MVI        HF         ROF")!=-1):
                state.append([])
                for i in range(11):
                    line=fin.readline()
                    r=line.split()[7]
                    state[-1].append(float(r)/1000)
                line=fin.readline()
                r=line.split()[8]
                state[-1].append(float(r)/1000)
            #TT/1 first fuel then cladding temperatures
            elif(line.find("I/J TT/1       TT/2       TT/3       QAXH/1     QAXH/2     QAXH/3")!=-1):
                state.append([])
                for i in range(10):
                    line=fin.readline()
                    state[-1].append(float(line.split()[1]))

class ATHLQ1T5(ATHLQ1):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLQ1.__init__(self, fold, fname)

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        line=" "
        while(line!=""):
            line=fin.readline()
            #TL: coolant temp.
            if(line.find("V-CHA                I/J PRESS      TFLUID     TL")!=-1):
                state.append([])
                line=fin.readline()
                state[-1].append(float(line.split()[5]))
                for i in range(1,12):
                    line=fin.readline()
                    state[-1].append(float(line.split()[3]))
            #ROF: coolant dens.
            elif(line.find("GBOR       MLI        MVI        HF         ROF")!=-1):
                state.append([])
                for i in range(11):
                    line=fin.readline()
                    r=line.split()[7]
                    state[-1].append(float(r)/1000)
                line=fin.readline()
                r=line.split()[8]
                state[-1].append(float(r)/1000)
            #TT/1 - TT/5 fuel temperatures
            elif(line.find("I/J TT/1       TT/2       TT/3       TT/4       TT/5")!=-1):
                state.append([])
                for i in range(10):
                    line=fin.readline()
                    tarr=[float(i) for i in line.split()[1:6]]   #average temp
                    state[-1].append(sum(tarr)/len(tarr))
            #TT/1 cladding temperature
            elif(line.find("I/J TT/1       TT/2       TT/3       QAXH/1     QAXH/2     QAXH/3")!=-1):
                state.append([])
                for i in range(10):
                    line=fin.readline()
                    state[-1].append(float(line.split()[1]))

class ATHLQ3T3(ATHLQ3):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLQ3.__init__(self, fold, fname)

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        line=" "
        while(line!=""):
            line=fin.readline()
            #TL: coolant temp.
            if(line.find("V-CHA                I/J PRESS      TFLUID     TL")!=-1):
                state.append([])
                line=fin.readline()
                state[-1].append(float(line.split()[5]))
                for i in range(1,12):
                    line=fin.readline()
                    state[-1].append(float(line.split()[3]))
            #ROF: coolant dens.
            elif(line.find("GBOR       MLI        MVI        HF         ROF")!=-1):
                state.append([])
                for i in range(11):
                    line=fin.readline()
                    r=line.split()[7]
                    state[-1].append(float(r)/1000)
                line=fin.readline()
                r=line.split()[8]
                state[-1].append(float(r)/1000)
            #TT/1 - TT/3 fuel or cladding temperatures
            elif(line.find("I/J TT/1       TT/2       TT/3       QAXH/1     QAXH/2     QAXH/3")!=-1):
                state.append([])
                for i in range(10):
                    line=fin.readline()
                    if(len(state)==3):  #fuel
                        tarr=[float(i) for i in line.split()[1:4]]   #average temp
                        state[-1].append(sum(tarr)/len(tarr))
                    else:   #cladding
                        state[-1].append(float(line.split()[1]))

class ATHLQ1T10_PINTVS2M(ATHLET):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLET.__init__(self, fold, fname, vars)

    #setting power distribution
    #sets the power distribution for an input file with 1 layer radial heat source
    def setQ(self, p):
        print("Updating power distribution in ATHLET input...")
        fout=open(self.fold+"Q.dat","w", encoding="ISO-8859-15")
        for i in range(len(p)):
            fout.write("PIN{:03d}.RW=1.000\n".format(i+1))
            for j in range(len(p[i])):
                fout.write("W%s.%s=%s\n" %("{:03d}".format(i+1), "{:02d}".format(j), "{:3f}".format(p[i][j])))

        print("Power distribution in ATHLET input updated.")

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        for i in range(4):
            state.append([]) #allocating tf, tc, tm, rho

        line=" "
        while(line!=""):
            line=fin.readline()
            #TL: coolant temp.
            if(line.find(" V-CHA")!=-1):
                line=fin.readline()
                state[2].append(float(line.split()[5]))
                for i in range(1,12):
                    line=fin.readline()
                    state[2].append(float(line.split()[3]))
            #ROF: coolant dens.
            elif(line.find("GBOR       MLI        MVI        HF         ROF")!=-1):
                for i in range(11):
                    line=fin.readline()
                    r=line.split()[7]
                    state[3].append(float(r)/1000)
                line=fin.readline()
                r=line.split()[8]
                state[3].append(float(r)/1000)
            #TT/1 - TT/7 fuel temperatures
            elif(line.find("I/J RODSEGPOW  DNBR       ICDNBR     TT/1       TT/2       TT/3       TT/4       TT/5       TT/6       TT/7")!=-1):
                for i in range(10):
                    line=fin.readline()
                    tarr=[float(i) for i in line.split()[4:]]   #average temp
                    state[0].append(sum(tarr)/len(tarr))
            #TT/8 - TT/10 fuel temperatures TT/11 cladding temperature
            elif(line.find("I/J TT/8       TT/9       TT/10      TT/11")!=-1):
                for i in range(10):
                    line=fin.readline()
                    tarr=[float(i) for i in line.split()[1:4]]
                    state[0][-(10-i)]=(sum(tarr)+7*state[0][-(10-i)])/(len(tarr)+7)
                    state[1].append(float(line.split()[4].split("-")[0]))

class CORE_PIN3_GAP_HeWL_CW_Q1T10(ATHLET):
    def __init__(self, fold="./athlet/", fname="input", vars=[1.0]):
        ATHLET.__init__(self, fold, fname, vars)

    #setting power distribution
    #sets the power distribution for an input file with 1 layer radial heat source
    def setQ(self, p):
        print("Updating power distribution in ATHLET input...")
        fout=open(self.fold+"Q.dat","w", encoding="ISO-8859-15")

        for k in range(len(p)):
            for i in range(len(p[k])):
                fout.write("F{:03d}.1.{:d}={:3f}\n".format(k+1,i+1,p[k][i]))
                fout.write("F{:03d}.2.{:d}=0.000\n".format(k+1,i+1))
                fout.write("F{:03d}.3.{:d}=0.000\n".format(k+1,i+1))
                fout.write("C{:03d}.1.{:02d}=0.000\n".format(k+1,i+1))
                fout.write("W{:03d}.1.{:02d}=0.000\n".format(k+1,i+1))

        fout.close()          
        print("Power distribution in ATHLET input updated.")

    #finding the state variables in the trimmed output file
    def _getstate(self, fin, state):
        for i in range(4):
            state.append([]) #allocating tf, tc, tm, rho

        line=" "
        while(line!=""):
            line=fin.readline()
            #TL: coolant temp.
            if(line.find(" V-CHA")!=-1):
                line=fin.readline()
                state[2].append(float(line.split()[5]))
                for i in range(1,12):
                    line=fin.readline()
                    state[2].append(float(line.split()[3]))
            #ROF: coolant dens.
            elif(line.find("GBOR       MLI        MVI        HF         ROF")!=-1):
                for i in range(11):
                    line=fin.readline()
                    r=line.split()[7]
                    state[3].append(float(r)/1000)
                line=fin.readline()
                r=line.split()[8]
                state[3].append(float(r)/1000)
            #TT/1 - TT/10 fuel temperatures
            elif(line.find("I/J TT/1       TT/2       TT/3       TT/4       TT/5       TT/6       TT/7       TT/8       TT/9       TT/10")!=-1):
                for i in range(10):
                    line=fin.readline()
                    tarr=[float(i) for i in line.split()[1:]]   #average temp
                    state[0].append(sum(tarr)/len(tarr))
            #TT/1 cladding temperature
            elif(line.find("I/J TT/1       TT/2       TT/3       QAXH/1     QAXH/2     QAXH/3")!=-1):
                for i in range(10):
                    line=fin.readline()
                    state[1].append(float(line.split()[1]))


def test():
    p=40*[0.100]
    athl=ATHLQ1T10_PINTVS2M(NZ=10, NA=4, fold="/home/pazmank/ATHLET/Utilities/", fname="core_PIN-TVS2M")
    #athl.setQ(p)
    #athl.run(0)
    #athl.setQ(p)
    #athl.run(1,0)
    [print(i[-10:]) for i in athl.output(0)]

if(__name__=="__main__"): test()
