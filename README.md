# gainstaging
A utility to help calculate and keep track of levels and gains within the gain structure of an audio signal chain.

Currently, gain settings for microphone input channels are often set by 'feel' using meters while the accoustic source is near its expected loudest, leaving a chosen headroom.
With the performance of modern studio equipment, and the availability of data sheets, I believe a range of 'optimum' gains could be calculated.
Handling the different units and positions in the gain structure is a major barrier to being able to do these calculations simply.  So lets write a program to help!

So, what do we want to do with it?
- enter levels in a variety of units (inc dB relative to various references)
- display levels in a variety of units (inc dB based)

- keep track of levels in different "zones"
- keep track of gains between "zones"
- display levels from one zone as their respective level at another zone

- distinguish between nominal levels, clipping levels, noise levels
- make it easy to find which clipping point stage is responsible for the entire signal-path's clipping
- display the power-sum of 'noise' sources


Stretch goal: graphic mode, showing scale for each gain zone, showing levels crossing the boundaries

Hand sketch:
![hand sketch showing levels translated by different gains](./Mic%20alignment.jpg)
sketch of various levels shown in pressure domain, the electrical domain at microphone output / mic amp input, electrical at mic amp output / ADC input, and Digital domain at ADC output.

