#!/usr/bin/python
# coding=utf-8
from math import log10, sqrt

class Level():
    """
    A class to represent audio levels.  It stores an RMS level in the SI unit
    of the field/domain, i.e. Pa for pressure, V for electrical, and FS (full
    scale sine) for digital, and the type of field/domain.
    
    levels can be set using a value-field pair, or with a string in many
    natural forms.

    >>> x = Level(1, 'P'); [x.value, x.field]
    [1.0, 'P']
    >>> x = Level("1Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("1 Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("0dB Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("0 dB(Pa)"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("94 dB SPL"); [x.value, x.field] #doctest: +ELLIPSIS 
    [1.00..., 'P']
    >>> x = Level("1V"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("1000 mV"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("1µV"); [x.value, x.field] 
    [1e-06, 'V']
    >>> x = Level("1nV"); [x.value, x.field] 
    [1e-09, 'V']
    >>> x = Level("1kV"); [x.value, x.field] 
    [1000.0, 'V']
    >>> x = Level("1MV"); [x.value, x.field] 
    [1000000.0, 'V']
    >>> x = Level("1GV"); [x.value, x.field] 
    [1000000000.0, 'V']
    >>> x = Level("0dBV"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("0dB(1V)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("60dB(mV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("120dB(µV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("180dB(nV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-60dB(kV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-120dB(MV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-180dB(GV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("0 dBu"); [x.value, x.field] 
    [0.775, 'V']
    >>> x = Level("1 FS"); [x.value, x.field] 
    [1.0, 'D']
    >>> x = Level("0dBFS"); [x.value, x.field] 
    [1.0, 'D']
    >>> x = Level("0 dB (FS)"); [x.value, x.field] 
    [1.0, 'D']
    """

    references = {'SPL': (0.00002, 'P'),
                  'Pa':  (1.0,     'P'),
                  'V':   (1.0,     'V'),
                  'FS':  (1.0,     'D'),
                  'u':   (0.775,   'V')}

    def __init__(self, value = 0, field = ''):
        """
        Check if 'value' is a number, in which case simply using arguments.
        Otherwise, parse 'value' for dB, references, etc.
        """
        SI = {'G':1e9, 'M':1e6, 'k':1e3, 'm':1e-3, u'µ':1e-6, 'n':1e-9, \
              ' ':1}
        self.field = field
        if type(value) in (int, float):
            self.value = float(value)
        else:
            if type(value) == str:
                value = unicode(value, 'utf-8')
                
            for i in range(len(value), 0, -1):
                try:
                    self.value = float(value[:i])
                    ref = value[i:].strip()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Could not parse '"+value+"' into a level.")

            if ref.startswith('dB'):
                self.value = dbta(self.value)
                ref = ref.split('dB', 1)[1].strip(' 1()')
                
            for i in Level.references:
                if ref.endswith(i):
                    self.value *= Level.references[i][0]
                    self.field =  Level.references[i][1]
                    ref = ref.rsplit(i, 1)[0].strip()
            for i in SI:
                if ref.endswith(i):
                    self.value *= SI[i]
                    ref = ref.rsplit(i, 1)[0].strip()
            if ref:
                raise ValueError("Could not parse the units '"+ref+"'")
    
    def __repr__(self):
        """
        Pretty print value in SI unit, and the domain with unit in parenthesis.
        
        >>> Level("0dBu")
        0.775 Voltage (Volts)
        >>> Level("0dB SPL")
        2e-05 Pressure (Pascals)
        >>> Level("0dBFS")
        1.0 Digital (w.r.t. FSS)
        """
        return str(self.value)+' '+ \
               {'P':'Pressure (Pascals)', \
                'V':'Voltage (Volts)', \
                'D':'Digital (w.r.t. FSS)'}[self.field]

    def dB(self, reference = 1):
        """
        Return value in dB relative to reference.
        Recognises 'SPL', 'u', 'mV', and 'Pa', 'V', 'FS'
        
        >>> Level(1, 'P').dB()
        0.0
        >>> round( Level(1, 'P').dB('SPL')  , 1)
        94.0
        >>> Level(1, 'V').dB('u') #doctest: +ELLIPSIS
        2.2...
        """
        if reference in Level.references:
            reference = Level.references[reference][0]
        #try:
        #reference = float(reference)
        #except ValueError:
        if self.value == 0:
            return float('-inf')
        else:
            return 20*log10(self.value / reference)

class Gain():
    """
    A class representing gains in an audio signal path.  Keeps track of the
    input and output domains, raising exceptions if the gain is being applied to
    a level in the wrong different domain.

    Can take an two arguments, an input Level and output Level:
    >>> Gain(Level('1Pa'), Level('2V'))
    2.0 V/Pa
    >>> Gain(Level("+18dBu"), Level("0dBFS")) #doctest: +ELLIPSIS
    0.162... FS/V

    If arguments are strings, they are casted to a Level instance:
    >>> Gain("+4dBu","0.1FS") #doctest: +ELLIPSIS
    0.0814... FS/V

    Can be used with one argument, allowing a gain using a '/' to show the two
    units, as in:
    >>> Gain("40mV/Pa")
    0.04 V/Pa
    
    This works with dB as well:
    >>> Gain("-18dB(FS/u)") #doctest: +ELLIPSIS
    0.162... FS/V

    Gains within a single domain still need to show the domains, to preserve
    domains.
    >>> Gain("+40 dB(V/V)")
    100.0 V/V
    """

    fields2SI = {'P':'Pa', 'V':'V', 'D':'FS'}
    
    def __init__(self, inLevel, outLevel = None):
        if isinstance(inLevel, (str, unicode)):
            if '/' in inLevel:
                [l,r] = inLevel.rsplit('/',1)
                outLevel = Level(l)
                inLevel = Level('1'+r.strip('()'))
            else:
                inLevel = Level(inLevel)
        if isinstance(outLevel, (str, unicode)):
            outLevel = Level(outLevel)
        self.gain     = outLevel.value / inLevel.value
        self.infield  = inLevel.field
        self.outfield = outLevel.field

    def __repr__(self):
        return str(self.gain)+' '+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]

    def dB(self):
        """
        Return pretty-print string of the gain in dB
        
        >>> Gain("10V/Pa").dB()
        '20.0 dB(V/Pa)'
        >>> Gain("+18dBu","0dBFS").dB() #doctest: +ELLIPSIS
        '-15.78... dB(FS/V)'
        """
        return str(20 * log10(self.gain))+' dB('+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]+')'

    def __rmul__(self, other):
        """
        A Level can be multiplied by a Gain to produce a new Level in the
        correct domain.
        
        >>> Level("0dB SPL") * Gain("40mV/Pa")
        8e-07 Voltage (Volts)

        ditto numbers
        >>> 2 * Gain("1 V/V")
        2.0 V/V
        """
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
        """
        Gains can be multiplied together, creating a new gain and daisy-
        chaining the domains.

        >>> Gain("40mV/Pa") * Gain("+18dBu","0dBFS") #doctest: +ELLIPSIS
        0.00649... FS/Pa

        ditto numbers
        >>> Gain("1V/FS") * 10
        10.0 V/FS
        """ 
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

    def __init__(self):
        self.gains  = [] # between zones
        self.fields = [] # {P,V,D} (pressure, voltage, or digital) for each zone
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

"""Helper functions"""
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
    """"gs = GainStructure()
    gs.fields = ['P','V','V','D']
    gs.gains = [0.04, 1, dbta(-10.5)]
    gs.addClip(dbta(132-94),0)
    gs.addNoise(dbta(15-94),0)
    print gs.systemNoiseAtZone(3)
    """
