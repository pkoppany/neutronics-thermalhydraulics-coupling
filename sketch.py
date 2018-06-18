import os

class SKETCH:
    path="/home/pazmank/SKETCH/"

    def __init__(self,NZ=10, NA=163, inp="Input/VVER1000.DAT", feedb="Input/Athlet.dat", outp="Output/SKETCH_POW.dat"):
        self.NZ=NZ
        self.NA=NA
        self.inp=inp
        self.feedback=feedb
        self.outp=outp

    #runs the program
    def run(self):
        cwd = os.getcwd()
        os.chdir(self.path)
        os.system("time ./sketch")
        os.chdir(cwd)

    #sets the total power, value in MW
    def setpow(self, power):
        print("Updating power level in SKETCH...")
        fin=open(self.path+self.inp, 'r', encoding="windows-1251")
        fout=open('temp.txt','w', encoding="windows-1251")

        line=' '
        while(line!=''):
            line=fin.readline()
            if(line.find("CNT_RCT_POWR")!=-1):
                fout.write(line)
                line=fin.readline()
                fout.write(line)
                line=fin.readline()
                fout.write(str(power)+"\n")
            else:
                fout.write(line)
        fin.close()
        fout.close()

        os.remove(self.path+self.inp)
        os.rename('temp.txt', self.path+self.inp)
        print("Power level in SKETCH updated.")

    #sets feedbacks from TH program
    def settemp(self,zcoords, tf, tc, tm, rho):     #old format
    #def settemp(self,tf, tm, rho):     #new format
        print("Updating TH feedback in SKETCH...")
        fout=open(self.path+self.feedback,'w')

        fout.write("Thermohydraulic feedback form ATHLET"+'\n')
        fout.write("NZ*NASS rows of data\n")

        #old format
        fout.write(('\t'.join(['Layer', 'coord,m', 'TF,K', 'TC,K', 'TM,K', 'rhoM,g/cm3'])+'\n').expandtabs(10))
        for i in range(len(tf)):
            for j in range(len(tf[i])):
                line=[j, zcoords[j], tf[i][j], tc[i][j], tm[i][j], rho[i][j]]
                fout.write(('\t'.join(['{:02d}'.format(line[0]), '{:.3f}'.format(line[1])]+list(map('{:.4f}'.format, line[2:])))+'\n').expandtabs(10))
        fout.close()

        '''
        #new format
        fout.write(('\t'.join(['TF,K', 'TM,K', 'rhoM,g/cm3'])+'\n').expandtabs(10))
        for i in range(len(tf)):
            for j in range(len(tf[i])):
                fout.write("{:.2f}\t{:.2f}\t{:.4f}\n".format(tf[i][j], tm[i][j], rho[i][j]).expandtabs(10))
        fout.close()
        print("TH feedback in SKETCH updated.")
        '''

    #returns keff and the value of power in each layer in kW
    #input: power of FA in kW
    def output(self):
        print("Reading SKETCH output files...")

        #reading
        pread=[]
        fin=open(self.path+self.outp, 'r')
        for j in range(self.NZ*self.NA):
            line=fin.readline()
            pread.append(line.split()[1])
        fin.close()

        #sorting
        psort=[]
        for i in range(self.NA):
            for j in range(self.NZ):
                psort.append(float(pread[i+j*self.NA]))

        print("SKETCH output files read.")

        return psort

def test():
    sk=SKETCH()
    #sk.run()
    pwr=sk.output()

    avg=0
    for i in range(sk.NA*sk.NZ):
        avg+=pwr[i]
    avg=avg/(sk.NA*sk.NZ)

    fout=open("SKETCH_POW_CHECK.dat", "w") 
    for i in range(sk.NA):
        fout.write("Assembly %s\n" % str(i+1))
        for j in range(sk.NZ):
            fout.write("%s %s\n" % (str(j+1), '{:.3f}'.format(float(pwr[j+i*sk.NZ])/avg)))
        fout.write("\n")
    fout.close()

if(__name__=="__main__"): test()