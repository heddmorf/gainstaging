#!/usr/bin/python
# coding=utf-8
from math import log10, sqrt

class Level():
    references = {'SPL':0.00002,
                  'Pa': 1.0,
                  'V':  1.0,
                  'FS': 1.0,
                  'mV': 0.001,
                  'u':  0.775}
    def __init__(self, value = 0, field = ''):
        if type(value) in (int, float):
            self.value = value
            self.field = field
        elif 'dB' in value:
            [v,ref] = value.split('dB',1)
            ref = ref.strip(' 1()')
            if   ref == 'SPL' or ref == 'Pa':
                self.field = 'P'
            elif ref == 'u' or 'V' in ref:
                self.field = 'V'
            elif ref ==('FS'):
                self.field = 'D'
            self.value = dbta(float(v)) * Level.references[ref.strip(' 1()')]
        elif value.endswith('FS'):
            self.field = 'D'
            self.value = value.rstrip('FS')
        elif value.endswith('V'):
            self.field = 'V'
            self.value = value.rstrip('V')
        elif value.endswith('Pa'):
            self.field = 'P'
            self.value = value.rstrip('Pa')
        else:
            self.value = value
            self.field = field
        SI = {'G':1e9, 'M':1e6, 'k':1e3, 'm':1e-3, 'µ':1e-6, 'n':1e-9, ' ':1}
        try:
            self.value = float(self.value)
        except ValueError:
            self.value = float(self.value[:-1]) * SI[self.value[-1]]
    def __repr__(self):
        return str(self.value)+' '+ \
               {'P':'Pressure (Pascals)', \
                'V':'Voltage (Volts)',\
                'D':'Digital (w.r.t. FSS)'}[self.field]
    def dB(self, reference = 1):
        """
        Return value in dB relative to reference.
        Recognises 'SPL', 'u', 'mV', and 'Pa', 'V', 'FS'
        """
        if reference in Level.references:
            reference = Level.references[reference]
        #try:
        #reference = float(reference)
        #except ValueError:
        if self.value == 0:
            return float('-inf')
        else:
            return 20*log10(self.value / reference)

references = {'Pa': Level("1 Pa") \
             ,'SPL':Level("0.00002 Pa") \
             ,'FS': Level(1,'FS') \
             ,'V':  Level("1 V") \
             ,'mV': Level("0.001 V") \
             ,'u':  Level("0.775 V") \
             }
fields2SI = {'P':'Pa', 'V':'V', 'D':'FSS'}

class Gain():
    def __init__(self, inLevel, outLevel = None):
        if isinstance(inLevel, str):
            if '/' in inLevel:
                [l,r] = inLevel.rsplit('/',1)
                outLevel = Level(l)
                inLevel = Level('1'+r.strip('()'))
            else:
                inLevel = Level(inLevel)
        if isinstance(outLevel, str):
            outLevel = Level(outLevel)
        self.gain     = outLevel.value / inLevel.value
        self.infield  = inLevel.field
        self.outfield = outLevel.field
    def __repr__(self):
        return str(self.gain)+' '+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]
    def dB(self):
        return str(20 * log10(self.gain))+' dB('+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]+')'
    def __rmul__(self, other):
        if isinstance(other, Level):
            if other.field is self.infield:
                return Level(other.value * self.gain, self.outfield)
            else:
                raise ValueError, "value and gain input are different fields"
        elif type(other) in (int, float):
            return self * other
        else:
            raise TypeError, "applying gain to something other than a Level"
        return None
    def __mul__(self, other):
        if isinstance(other, Gain):
            if other.infield is self.outfield:
                return Gain(Level(1, self.infield), \
                            Level(self.gain * other.gain, other.outfield))
            else:
                raise ValueError, "inside fields of gains do not match"
        elif type(other) in (int, float):
            return Gain(Level(1, self.infield),\
                        Level(self.gain * other, self.outfield))
        else:
            raise TypeError
        return None

class GainStructure():
    """
    Help work out gain structures by tracking clipping levels and noise level
    contributions at different 'zones' of a gain structure.
    Levels are internally stored in SI RMS values (Pa, V, FSS)
    """

    from math import log10, sqrt
    
    #def Level as [number, unitid]
    def __init__(self):
        self.gains  = [] # between zones
        self.fields = [] # {P,V,D} (presure, voltage, or digital), for each zone
        self.noises = [] # tuples, level and zone
        self.clips  = [] # tuples, level and zone
    def systemNoiseAtZone(self, zone):
        p = 0
        for i in self.noises:
            p = p + atp(self.levelAtZone(i[0],i[1], zone))
        return pta(p)
    def systemClipAtZone(self, zone):
        ret = float('+inf')
        for i in self.clips:
            t = self.levelAtZone(i[0],i[1], zone)
            if t < ret :
                ret = t
        return ret
    def addClip(self, level, zone):
        self.clips = self.clips + [[level, zone]]
        return
    def addNoise(self, level, zone):
        self.noises = self.noises + [[level, zone]]
        return
    
    def levelAtZone(self, level, originalZone, returnZone):
        if (originalZone == returnZone):
            return level
        elif (originalZone < returnZone):
            ret = level
            for i in range(originalZone, returnZone):
                ret = ret * self.gains[i]
            return ret
        elif (originalZone > returnZone):
            ret = level
            for i in range(returnZone, originalZone):
                ret = ret / float(self.gains[i])
            return ret
        else:
            print "shouldn't get here!!!"


def dbta(dB):
    return pow(10, dB / 20.)
def atdb(a):
    return 20 * log10(a)
def dbtp(dB):
    return pow(10, dB / 10.)
def ptdb(p):
    return 10 * log10(p)
def atp(a):
    return a ** 2
def pta(p):
    return sqrt(p)

if __name__ == "__main__":
    gs = GainStructure()
    gs.fields = ['P','V','V','D']
    gs.gains = [0.04, 1, dbta(-10.5)]
    gs.addClip(dbta(132-94),0)
    gs.addNoise(dbta(15-94),0)
    print gs.systemNoiseAtZone(3)

