# CCores


To get started: 

- open ccore_examples jupyter notebook and simply click through. 


Module quick description:

constants.py - contains quick access dataset & wavelet input definitions.
It also defines the quick access to wavelet power filtering utilities in powerUtils.py.
All customised dataset and wavelet definitions should be included here. 

cores.py - the heart of the wavelet application object. Initialises the object and allows access to object functions. 
This includes image pre-processing, wavelet application and accessing the wavelet power post-processing utilities.
Functions can be extended.

powerUtils.py - defines custom wavelet power filter functions, which can be extended as needed by implementation here
and definition in constants.py

twod.py - 2d wavelet function, _do not touch_. Called by cores.py

wav.py - the wavelet object, in most cases: _do not touch_. Allows customisation of wavelet coefficient filtering.
         Called by cores.py: given we're looking at cloud top temperatures, only negative wavelet coefficients 
         are automatically considered in current cores.py setup. 

