[![Build Status](https://travis-ci.org/heddmorf/gainstaging.svg?branch=master)](https://travis-ci.org/heddmorf/gainstaging)

# gainstaging
A utility to help calculate and keep track of levels and gains within the gain structure of an audio signal chain.

## Rationale

Currently, gain settings for microphone input channels are often set by 'feel' using meters while the acoustic source is near its expected loudest, leaving a chosen headroom.
With the performance of modern studio equipment, and the availability of data sheets, I believe a range of 'optimum' gains could be calculated.

Handling the different units and positions in the gain structure is a major barrier to being able to do these calculations simply.
After messing around with complicated spreadsheet to calculate optimal mic gains, I though it really shouldn't be that hard.

So I wrote this python module to take care of the heavy lifting.

For more background on what lead to here, see the [original post about calculating gains for classical recording][classicalpost]
and the [first post about this utility][part1].

Initial coding done (with only some pain &mdash; see [Part 2][part2]), so lets have a look at the new `gainstaging` utility.

## Usage overview

To load up the utility, open Python from the directory containing `gainstaging.py`.
When greeted with the Python prompt, load the utility by typing:
```python
>>> from gainstaging import *
```

### Levels and Gains

Levels and gains have special classes to represent them.
They are crated as follows:
```python
>>> Level("0dBu")
0.775 V
>>> Gain("40 mV/Pa")
0.04 V/Pa
```
Gains can also be set by giving the input and output levels, as often used for ADC alignments:
```python
>>> Gain("+18 dBu", "0dBFS")
0.162441988619 FS/V
```

dB values can be printed from these by using `.dB()` afterwards.
```python
>>> Gain("+18 dBu", "0dBFS").dB()
'-15.7860340501 dB(FS/V)
```
For levels, you can provide a reference for dB too, rather than the default SI unit.
```python
>>> Level("1V").dB('u')
2.213965949873794
>>> Level("1Pa").dB('SPL')
93.97940008672037
```

A gain can be applied to a level by multiplying, and the units are correctly handled:
```python
>>> Level("+4dBu") * Gain("+24dBu","0dBFS")
0.1 FS
```

When we start dealing with complex signal chains, we will need to know which side of which gain stage a level refers to.
For this, the Level class has a `zone` attribute.
These are simply numbers for the stages, starting with 0 for the extreme left side of the chain.
```python
>>> mic = Gain("40mV/Pa")
>>> ADC = Gain("+18dBu", "0dBFS")
>>> Level("85 dB SPL", zone=0) * mic
0.0142262352803 V zone: 1
>>> Level("85 dB SPL", zone=0) * mic * ADC
0.00231093794949 FS zone: 2
>>> (Level("85 dB SPL", zone=0) * mic * ADC).dB("FS")
-52.72423431028695
```
### Other functions

#### levelAtZone()

The basic function of the utility is to take a level stated at one zone, and calculate what the level would be in another zone accounting for the various gains in between.
This is performed by the `levelAtZone()` function.
```
levelAtZone(gainList, level, desiredZone)
```
In common with the other functions to follow, the first argument you need to give the function is a list of the gains.
These can either be defined within the square brackets Python uses to define lists, or if you define the gains elsewhere first, the variable names can appear in the square brackets instead:
```python
>>> micDPA4006 = Gain("40mV/Pa")
>>> adcEBU = Gain("+18dBu","1FS")

>>> levelAtZone( [micDPA4006, adcEBU], Level("85dB(SPL)"), 2)
0.00231093794949 FS zone: 2
```
Alternatively, in dB:
```python
>>> levelAtZone( [micDPA4006, adcEBU], Level("85dB(SPL)"), 2).dB("FS")
-52.72423431028695
```

#### powersum()

To find the sum of noise sources, you can use the `powersum()` function.
Usage is similar to the `levelAtZone()` function, except that a list of levels is expected.
```python
powersum(gainList, levelList, desiredZone)

>>> micnoise = Level("15dB SPL", zone = 0)
>>> ADCnoise = Level("-119dBFS", zone = 2)
>>> powersum( [micDPA4006, adcEBU], [micnoise, ADCnoise], 1).dB("u")
-99.46427259808596
>>> powersum( [micDPA4006, adcEBU], [micnoise, ADCnoise], 0).dB("SPL")
20.259961712180292
```

#### findClip()

For finding the clipping point of a signal path, `findClip()` is a little different, in that it doesn't ask what zone you want reported, rather it shows the clipping level that clips the system at its original zone.

levelList can also be a Python `dict` dictionary, which means the returned value will say the name of the clipping point.
```python
findClip(gainList, levelList)

>>> micClip = Level("132dB SPL")
>>> adcClip = Level("1FS")

>>> findClip( [ micDPA4006, adc10dBu ], [ micClip, adcClip ] )
1.0 FS zone: 2

>>> findClip( [ micDPA4006, adc10dBu ], { 'Mic': micClip, 'ADC': adcClip } )
{'ADC': 1.0 FS zone: 2}
```




[classicalpost]: blog.morfaudio.co.uk/2017/03/classical-concert-mic-gain.html
[part1]: blog.morfaudio.co.uk/2017/03/gainstaging-utility-part-1.html
[part2]: blog.morfaudio.co.uk/2017/03/creating-gainstaging-utility-part-2.html
