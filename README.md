# CCores
CCores is a package to extract convective cores from cloud top temperatures as provided by thermal-infrared imagery from geostationary satellites (e.g. Meteosat). Convective cores are defined here as convectively active areas of storms that have high likelihood for intense and extreme rain. The background of the wavelet approach is described in 
Klein, C., Belušić, D. and Taylor, C. M.: Wavelet Scale Analysis of Mesoscale Convective Systems for Detecting Deep Convection From Infrared Imagery, J. Geophys. Res. Atmos., 123(6), 3035–3050, doi:10.1002/2017JD027432, 2018.

To get started: 

- open ccore_examples jupyter notebook and simply click through. 
NOTE: The Meteosat test datacase has been already interpolated onto a regular lat/lon grid corresponding to an approximate resolution of 5km. 
The data resolution info provided to CCores should correspond to the approximate dataset resolution in km.


Module quick description:

constants.py - contains quick access dataset & wavelet input definitions. This also includes the dataset resolution (~ km) information.
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
         
         
#############
Other:

tir_testfile.nc: netCDF thermal-infrared testfile containing a single time step of brightness temperatures over West Africa for a Meteosat image interpolated onto a ~5km grid. 

ccore_examples.ipynb: jupyter notebook illustrating an example application of CCores on the testfile.

