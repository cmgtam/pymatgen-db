#!/usr/bin/env python
##
#@package   util_tom
#@ingroup   vasp
#@ingroup   python
#@brief     Utility Package with various functionalities
#@author    Tom Angsten
#@date      7/25/11 created
#@date      10/3/11 TTM added getNumAtoms and made modifications to getVolume
###

import os
import sys
import shutil
import math

def is_int(str = ""): #TA 2/4/12 returns true if string represents an int
    try:
        int(str)
        return True
    except ValueError:
        return False
    

def calculate_hvf(bulkdir="",vacdir="",numatoms=108): #TA 1/29/12 added hvf calculation feature
    """
    Purpose: Calculates Enthalpy of Vacancy Formation
    inputs:  
        [$1] path for bulk
        [$2] path for vac
        [$3] number of atoms in cell (default = 108)
    """
    
    bulkdir = os.path.abspath(bulkdir)
    vacdir = os.path.abspath(vacdir)

    if (os.path.exists(bulkdir) == False):
        print 'Bulk directory does not exist'
        return None
    elif (os.path.exists(vacdir) == False):
        print 'Vacancy directory does not exist'
        return None

    bulk_oszicar = bulkdir + '/OSZICAR'
    vac_oszicar = vacdir + '/OSZICAR'

    bulk_energy = getEnergy(bulk_oszicar)
#    print "BULK ENERGY: " + str (bulk_energy)
    vac_energy = getEnergy(vac_oszicar)
#    print "VAC ENERGY: " + str (vac_energy)
    normalized_energy = ( bulk_energy/float(numatoms) )
    return ( (vac_energy+normalized_energy)-bulk_energy )

def getnumAtoms(poscar=""):
    '''
    Takes in path to poscar, outputs number of atoms in poscar TA 1/29/12
    '''
    poscar = os.path.abspath(poscar)
    readf = open(poscar,'rb')

    num_atoms = int(extractNumbers(readf.readlines()[6])[0])
#    print "NUM ATOMS IS " + str(num_atoms)
    readf.close()
    return num_atoms

def getName(poscar=""):
    '''
    Takes in path to poscar, outputs system name in poscar TA 1/29/12
    '''
    poscar = os.path.abspath(poscar)
    readf = open(poscar,'rb')

    name = readf.readlines()[0]
#    print "NUM ATOMS IS " + str(num_atoms)
    readf.close()
    return name.strip()

def getnebEnergy(neb_path="",static=False):
    '''
    TA 1/29/12 only supports one image so far
    '''
    append = ""
    if(static):
        append = "static"
        
    image_zero_path = os.path.join(neb_path,'00'+append,'OSZICAR')
    image_one_path = os.path.join(neb_path,'01'+append,'OSZICAR')
    image_two_path = os.path.join(neb_path,'02'+append,'OSZICAR')

    E0 = getEnergy(image_zero_path)
    E1 = getEnergy(image_one_path)
    E2 = getEnergy(image_two_path)

#    print "E0 " + str(E0)
#    print "E1 " + str(E1)
#    print "E2 " + str(E2)
    E02diff = math.fabs(E2 - E0)

#    if(E02diff > 0.2):
 #       return "Endpoint energy difference too great"

    return (E1 - E0)

def normalizePoscar(poscar="",outputfile=""):
    """
    Takes in poscar (or contcar) file and changes direct coordinates to between 0 and 1.  Places the
    normalized file in the specified outputfile path
    """

    poscar = os.path.abspath(poscar)
    readf = open(poscar,'rb')

    outputfile = os.path.abspath(outputfile)
    writef = open(outputfile,'wb')
    
    lines = readf.readlines()

    stage = 0
    
    for line in lines:
        if(stage == 0):
            writef.write(line)
            if(line.find("D") != -1):
                stage = 1
                continue
        if(stage == 1):
            if(len(line) < 5):
                writef.write(line)
                stage = 0
                continue

            integers = extractNumbers(line)
            int1 = normalizeNumber(integers[0])
            int2 = normalizeNumber(integers[1])
            int3 = normalizeNumber(integers[2])
            
            writef.write(str(int1) + " " + str(int2) + " " + str(int3) + "\n")

def normalizeNumber(number):
    """
    Normalizes number to a number between 0.0 and 1.0 and returns the normalized number
    """

    if(number > 1.0):
        number -= 1.0
    if(number < 0.0):
        number += 1.0

    return number

def getEnergy(oszicar=""):
    """
    Gets the last E0 printed in the OSZICAR and returns it as a float.
    """

    oszicar = os.path.abspath(oszicar)
    
    if not os.path.isfile(oszicar):
        return None
    
    readf = open(oszicar,'rb')
    
    def getLastE0(f):
        ret = ""
        while True:
            line = f.readline()
            if(not line):
                f.close()
                return "0"
            elif (line.find("E0") != -1):
                ret = getLastE0(f)
                if(ret == "0"):
                    f.close()
                    return line
                else:
                    return ret
    
    def getValue(line):
        start = line.find("E0")
        
        if(start == -1):
            return None
        
        start = start + 4
        line = line[start:]
        end = line.index(" ")
        line = line[:end]
        val = float(line)

        return val

    line = getLastE0(readf)
    val = getValue(line)

    return val

def getMag(oszicar=""):
    """
    Gets the last mag printed in the OSZICAR and returns it as a float.
    """

    oszicar = os.path.abspath(oszicar)
    
    if not os.path.isfile(oszicar):
        return None
    
    readf = open(oszicar,'rb')
    
    def getLastMag(f):
        ret = ""
        while True:
            line = f.readline()
            if(not line):
                f.close()
                return "0"
            elif (line.find("mag") != -1):
                ret = getLastMag(f)
                if(ret == "0"):
                    f.close()
                    return line
                else:
                    return ret
    
    def getValueMag(line):
        start = line.find("mag")
        
        if(start == -1):
            return None
        
        start = start + 5
        line = line[start:]

        val = float(line)
        return val

    line = getLastMag(readf)
    val = getValueMag(line)

    return val

def getVolume(path_outcar):
    def getLastVol(f):
        ret = ""
        while True:
            line = f.readline()
            if(not line):
                return "0"
            elif(line.find("volume of cell") != -1):
                ret = getLastVol(f)
                if(ret == "0"):
                    return line
                else:
                    return ret
        

    def getValue(line):
        val = 0
        #TTM+2 10/3/11 prevent fail if there is no volume
        if (line == "0"):
            return 0
        val = float(line[22:39])
        return val

    if not os.path.isfile(path_outcar):
        return None
    
    file = open(path_outcar,'rb')
    val = getValue(getLastVol(file))
    file.close() #TTM 10/3/11 added
    return val

def getTime(outcar=""):
    """
    Returns processors*usertime divided by ten.  Takes in OUTCAR file path.
    """

    def findLine(lines):
        for line in lines:
            if(line.find("User time") != -1):
                newline = line[-13:]
                break
        time = 0
        newline = newline.strip()
        time = float(newline)
        return time

    def getNumProc(lines):
        for line in lines:
            if(line.find("running on") != -1):
                newline = line.strip()
                break
        num_proc = extractNumbers(line)[0]
        return num_proc

    f = open(outcar,'rb')
    lines = f.readlines()

    time = findLine(lines)
    num_proc = getNumProc(lines)

    final_time = (time*num_proc)/100.0

    final_time = int(round(final_time,0))
    
    return final_time


def isComplete(outcar=""): #TA 1/15/12 checks to see if outcar has finished

    def findLine(lines):
        found = False
        for line in lines:
            if(line.find("User time") != -1):
                found = True
                break
        return found

    f = open(outcar,'rb')
    lines = f.readlines()

    return findLine(lines)

def extractNumbers(string=""):
    """
    Extracts all numbers separated by non-number/decimal-place characters and returns in list
    If numbers are in form x,aaa  output will be x and aaa. Return values are numbers, not strings.
    """

    list = []

    if(not isinstance(string,basestring)):
        string = str(string)

    char = ''
    begin = 0
    end = 0
    
    while( begin < len(string) ):
        char = string[begin]
        dot_count = 0
        
        if(char.isdigit() == True or char == '.'):
            end = begin+1
            if (char == '.'):
                dot_count += 1
            while( ( end < len(string) ) and (string[end].isdigit() or string[end] == '.') ):
                if( string[end] == '.' ):
                    dot_count += 1
                    if(dot_count > 1):
                        break
                end += 1

            if(dot_count <= 1):        
                list.append(float(string[begin:end]))
            else:
                if( len(string[begin:end-1]) > 1 ):
                    list.append(float(string[begin:end-1]))
            begin = (end+1)
        else:
            begin += 1
        
    return list

def extractJobid(string = ""):
    final = ""
    for char in string:
        if(char != '.'):
            final += char
        else:
            return int(final)

#TTM 2/10/12 add new job extraction function from ranger
def extractJobid_ranger(string = ""):
    findme=0
    findstr=""
    findme = string.find("Your job") # ..... Your job 12345678 has been submitted.
    if findme == -1: #TTM+1 2/11/12 if not found, return negative 1
        return -1
    findstr = string[findme+9:]
    splitstr=[]
    splitstr = findstr.split()
    return int(splitstr[0])

def posMap(file1 = "", file2 = "", numatoms = 0):
    """
    Prints out a position mapping file of file1 POSCAR relative to file2 POSCAR.  File1 and file2
    must be cleaned up: nothing but the direct coordinates.  Maping will have 9 added to each so
    that the mapping can be used for normal POSCARS with the first 8 lines present.  Outputs to
    a .mapping file.  Make sure num atoms is 1 less than bulk for endpoints.
    """
    
    import sys
    import os

    mapping = ["" for row in range(numatoms)]

    file1 = os.path.abspath(file1)
    file2 = os.path.abspath(file2)
    
    f1 = open(file1,'rb')
    w1 = open(file1 + '.mapping','wb')


    count1 = 9
    while(count1 < (numatoms+9)):
        line1 = f1.readline()
        strpos = extractNumbers(line1)
        
        x1 = round(float(strpos[0]), 4)
        y1 = round(float(strpos[1]), 4)
        z1 = round(float(strpos[2]), 4)
        
        string1 =  str(x1) + " " + str(y1) + " " + str(z1)
        count2 = 9

        f2 = open(file2,'rb')

        while(count2 < (numatoms+9)):
            line2 = f2.readline()
            strpos2 = extractNumbers(line2)
            x2 = round(float(strpos2[0]), 4)
            y2 = round(float(strpos2[1]), 4)
            z2 = round(float(strpos2[2]), 4)
            
            string2 = str(x2) + " " + str(y2) + " " + str(z2)
            
            if(string1 == string2):
                mapping[count1 - 9] = str(count1) + ":" + str(count2)
            count2 += 1

        f2.close()

        count1 += 1


    for x in mapping:
        w1.write(x + '\n')

    w1.close()

def translatePoscar(poscar="", x=0.3333333333, y=0.0000000000, z=0.0000000000, numatoms=0, mapkey=""):
    """
    Purpose: Translate direct coordinates of hcp poscar by vector <x,y,z>
        1. path of POSCAR file
        2. x component of translation vector (direct coordinates)
        3. y component
        4. z component
        5. number of atoms
        6. atom position mapping file
    """

    import add_coord_tom

    x = float(x)
    y = float(y)
    z = float(z)
    
    poscar = os.path.abspath(poscar)

    readf = open(poscar,'rb')
    writef = open(poscar + '.work','wb')
    
    slot = 0
    for line in readf:
        if(slot == 0):
            writef.write(line)
            if(line.find('D') != -1):
                slot = 1
        elif(slot == 1):
            if(len(line) < 5):
                slot = 0
                writef.write(line)
                continue
            newline = add_coord_tom.main(line,x,y,z)
            writef.write(newline + '\n')
    readf.close()
    writef.close()
    
    transf = open(poscar + '.work','rb')
    mapfile = open(mapkey,'rb')
    wfin = open(poscar + '.final','wb')
    
    translisting = transf.readlines()
    maplisting = mapfile.readlines()

    pos = 1
    while(pos < 9):
        wfin.write(translisting[pos-1])
        pos += 1
        
    
    while(pos < (9+numatoms)):
        mapcount = 0
        while(mapcount < len(maplisting)):
            indices = extractNumbers(maplisting[mapcount])
            if(int(indices[1]) == pos):
                wfin.write(translisting[int(indices[0])-1])
                
            mapcount += 1
        pos += 1

    while(pos < len(translisting)+1):
        wfin.write(translisting[pos-1])
        pos += 1

    os.remove(poscar + '.work')
    shutil.move(poscar + '.final', poscar)

def synthEp(ep2dir = "", ep1statdir = "", structure=""):
    """
    Purpose: Sythesize one endpoint from another
    [$1] synthesized endpoint two destination directory
    [$2] endpoint one static directory from which to synthesize CONTCAR
    [$3] structure type (fcc, hcpb, hcpz)
    """

    #shutil.copytree(ep1statdir,ep2dir) #TTM 052312 edit out because interface class will create ep2 direcdtory and populate it
    shutil.copy(ep1statdir + '/CONTCAR', ep2dir) #TTM 052312 added
    poscarfile = ep2dir + "/CONTCAR"

    map_path = os.path.expanduser("~/bin/map.file") #TA 1/15/12 must have map file in bin directory
    if(structure == "fcc"):
        translatePoscar(poscarfile, 0.0000000000, 0.1666666667, 0.1666666667, 108, map_path)

    if(structure == "hcpb"):
        translatePoscar(poscarfile, 0.3333333333, 0.0000000000, 0.0000000000, 36,
            "/home/angsten/bin/tscripts/mappings_tom/hcp36basal.mapping")
            
    
def compressString(string, char=' '):
    """
    Takes all repetitions of given char in a string and removes them. i.e. hello   world would become hello world.
    Returns the compressed form of string.
    """
    deadlist = []
    retstr = ""
    
    count = 0
    hit = False
    
    while(count < len(string)):
        if(string[count] == char):
            if(hit):
                deadlist.append(count)
            else:
                hit = True
        else:
            hit = False
        count += 1
    
    count = 0
    while(count < len(string)):
        if(count not in deadlist):
            retstr += string[count]
        count += 1
    return retstr

def makexyz(poscar=""):
    """
    Takes in a poscar-like file and outputs .xyz file form to stdout.  Vasp version 5 poscars only.
    Poscar file atom positions  must be in direct coordinates.
    """
    system_name = ""
    scalar = 0.0
    v1 = [0.0, 0.0, 0.0]
    v2 = [0.0, 0.0, 0.0]
    v3 = [0.0, 0.0, 0.0]
    species = ["",""]
    numatoms = [0,0]
    spec1lines = []
    spec2lines = []
    twospec = True
    
    poscar = os.path.abspath(poscar)

    readf = open(poscar,'rb')

    lines = readf.readlines()

    system_name = compressString(lines[0]).strip()
    
    scalar = extractNumbers(lines[1])[0]

    vec1list = extractNumbers(lines[2])
    v1[0] = vec1list[0]
    v1[1] = vec1list[1]
    v1[2] = vec1list[2]

    vec2list = extractNumbers(lines[3])
    v2[0] = vec2list[0]
    v2[1] = vec2list[1]
    v2[2] = vec2list[2]

    vec3list = extractNumbers(lines[4])
    v3[0] = vec3list[0]
    v3[1] = vec3list[1]
    v3[2] = vec3list[2]

    specstr = compressString(lines[5].strip())
    species[0] = specstr.split(' ')[0]
    if(len(specstr.split(' ')) > 1):
        species[1] = specstr.split(' ')[1]
    else:
        species[1] = ""
        twospec = False
    numatoms[0] = str(int(extractNumbers(lines[6])[0]))
    if(twospec):
        numatoms[1] = str(int(extractNumbers(lines[6])[1]))
    else:
        numatoms[1] = "0"

    i = 0
    while( i < int(numatoms[0]) ):
        spec1lines.append(lines[8+i])
        i += 1
    i = 0
    while( i < int(numatoms[1])):
        print spec2lines.append( lines[8+int(numatoms[0])+i])
        i += 1

    print "XYZ file output:\n\n"
    print str(int(numatoms[0])+int(numatoms[1]))
    print system_name

    def filter(num):
        if( (1.0-num) < 0.07 or num >= 1.0 ):
            return (num-1.0)
        else:
            return num
    i = 0
    while( i < int(numatoms[0]) ):
        x = filter( extractNumbers(spec1lines[i])[0] )
        y = filter( extractNumbers(spec1lines[i])[1] )
        z = filter( extractNumbers(spec1lines[i])[2] )
        
        coords = [0.0,0.0,0.0]
        coords[0] = scalar*(x*v1[0] + y*v2[0] + z*v3[0])
        coords[1] = scalar*(x*v1[1] + y*v2[1] + z*v3[1])
        coords[2] = scalar*(x*v1[2] + y*v2[2] + z*v3[2])
                
        print species[0] + str(i+1) + " " + str(coords[0]) + " " + str(coords[1]) + " " + str(coords[2])
        i += 1

    i = 0
    while( i < int(numatoms[1]) ):
        x = filter( extractNumbers(spec2lines[i])[0] )
        y = filter( extractNumbers(spec2lines[i])[1] )
        z = filter( extractNumbers(spec2lines[i])[2] )
        
        coords = [0.0,0.0,0.0]
        coords[0] = scalar*(x*v1[0] + y*v2[0] + z*v3[0])
        coords[1] = scalar*(x*v1[1] + y*v2[1] + z*v3[1])
        coords[2] = scalar*(x*v1[2] + y*v2[2] + z*v3[2])
        
        print species[1] + str(i+1) + " " + str(coords[0]) + " " + str(coords[1]) + " " + str(coords[2])
        i += 1
          
    print "\n"

def findEnmax(pot_path="POTCAR"):
    """
    To be called in directory containing POTCAR. Returns 1.5 * enmax.
    """

    cwd = os.getcwd()
    if(pot_path == "POTCAR"):
        file = cwd + '/POTCAR'
    else:
        file = pot_path
        
    readf = open(file,'rb')
    linef = ""
    
    for line in readf:
        if (line.find("ENMAX") != -1):
            linef = line

    enmax = extractNumbers(linef)[0]

    return int(round(enmax*1.5,0))

    readf.close()

def getNumAtoms(existdir="", usefile='POSCAR', total=1):
    """
    get number of atoms
    TTM 10/3/11 added from Vnumatoms, but only returns total number of atoms (not species by species string)
    total: 1 - return total number of atoms (default)
           0 - return comma-delimited string
    """
    import os
    import sys
    import Xvaliddirectory
    import Xvalidinteger
    import Pgetline
#   Validation
#   #  directory
    existdir = Xvaliddirectory.main(existdir)
    if (existdir == None):
        print '(Exiting.)'
        return 0
    total = Xvalidinteger.main(total, 0, 1)
    if (total == None):
        print '(Exiting.)'
        return 0
#   get appropriate line from POSCAR
    numline=""
    numlist=[]
    firstnum=0
    if (os.path.isfile(existdir + '/' + usefile) != True):
        existdir = existdir + '/00'
    numline = Pgetline.main(existdir, usefile, 0, 6)
    if (numline == None):
        return 0
    numlist = numline.split() # split out by whitespace
#   #   handle both VASP 4 and VASP 5
    if len(numlist) == 0:
        print 'Error trying to find number of atoms.'
        print '(Exiting.)'
        return 0
    try:
        firstnum = int(numlist[0])
    except (ValueError, TypeError):
        numline = Pgetline.main(existdir, usefile, 0, 7)
        if (numline == None):
            return 0
        numlist = numline.split()
        if len(numlist) == 0:
            print 'Error trying to find number of atoms.'
            print '(Exiting.)'
            return 0
        try:
            firstnum = int(numlist[0])
        except (ValueError, TypeError):
            print 'Error trying to find number of atoms.'
            print '(Exiting.)'
            return 0
#   #   presumably what is left should be a list of numbers as strings
    listnum=""
    myint=0
    totalnum=0
    returnstr=""
    count=0
    for listnum in numlist:
        try:
            myint = int(listnum)
        except (ValueError, TypeError):
            print 'Error separating some number to add to number of atoms.'
            print '(Exiting.)'
            return 0
        totalnum = totalnum + myint
        if (count == 0):
            returnstr = returnstr + listnum
        else:
            returnstr = returnstr + ',' + listnum
        count = count + 1
    if (total == 0):
        return returnstr
    else:
        return totalnum
    
