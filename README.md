# gainstaging
A utility to help calculate and keep track of levels and gains within the gain structure of an audio signal chain.

Currently, gain settings for microphone input channels are often set by 'feel' using meters while the acoustic source is near its expected loudest, leaving a chosen headroom.
With the performance of modern studio equipment, and the availability of data sheets, I believe a range of 'optimum' gains could be calculated.
Handling the different units and positions in the gain structure is a major barrier to being able to do these calculations simply.  So lets write a program to help!

## Requirements

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

As an example, I want software help with the following:

> mic clips at X dB SPL, mic self-noise is at Y dB SPL, and has sensitivity of Z mV/Pa;
> ADC has 0-gain sensitivity of +13dBu for 0dBFS, gain of 0 -- 50dB, EIN of A dBu, DNR of B dBFS.
>
> At what gain setting will the system noise be 1 dB higher than the microphone's self noise?
> Or, what is the system noise in dB SPL equivalent, when the gain is set to match the clipping levels of the mic and ADC?


Here's a hand sketch showing working for gain alignment (85 dB SPL at microphone aligned to 85 dB SPL at calibrated listening position (set at -18 dBFS):
![hand sketch showing levels translated by different gains](./Mic%20alignment.jpg)
^ Sketch of various levels shown in pressure domain, the electrical domain at microphone output / mic amp input, electrical at mic amp output / ADC input, and Digital domain at ADC output.

## Development

I'll write this in Python initially, as I often use a Python prompt as an (extended programmable) calculator anyway.

Watch this space for developments!
