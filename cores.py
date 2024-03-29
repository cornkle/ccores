from ccores import constants, wav
import numpy as np
from scipy.ndimage.measurements import label
from scipy import ndimage
import xarray as xr
import os

class dataset(object):

    def __init__(self, dataname):


        if dataname in constants.NAMES:
            dic = constants.NAMES[dataname]
        else:
            print('Dataset not found')
            return

        self.name = dataname
        self.res = dic['dx']
        self.dist = dic['dist']
        self.nb = dic['nb']
        self.start = dic['start']
        self.Tcut = dic['Tcut']
        self.Twav = dic['Twav']


        obj = wav.wavelet(self.res, self.dist, self.nb, start=self.start)
        self.scales = obj.scales

        print('Initialised wavelet with scales: ', self.scales)



    def read_img(self, torig, lon, lat, edge_smoothing=False, dynamic_background=False, min_area = False):
        """
        Filters clouds of set area threshold and prepares image for wavelet analysis via adjusting background temperature
        and smoothing cloud edges.
        t: numpy array, cloud top temperature data
        lon: 1d numpy array, longitude or x
        lat: 1d numpy array, latitude or y
        edge_smoothing: optional cloud edge smoothing via gaussian filter - can help in case of excessive core
                        identification at cloud edges (default: False)
        dynamic_background: optional dynamical background temperature according to coldest pixel in image -
                            can help in case of excessive core identification at cloud edges (default: False)
        min_area: optional minimum area threshold for identified clouds. If false, minimum is defined by the minimum
                  core scale (default: False)

        :return: filtered cloud top temperatures with adjusted background temperature
        """

        londiff = lon[0:-1]-lon[1::]
        if not np.allclose(londiff, np.zeros_like(londiff)+londiff[0]):
            print('Please provide regular grid coordinates.')

        self.original = torig
        t = torig.copy()

        t[t >= self.Tcut] = 0
        t[t <= -150] = 0
        t[np.isnan(t)] = 0
        outt = t.copy()
        print('outmin', np.nanmin(outt), np.nanmax(outt))
        labels, numL = label(outt)

        u, inv = np.unique(labels, return_inverse=True)
        n = np.bincount(inv)

        # some approximate minimum cloud scales: 3 pixels across in any direction for minimum wavelet
        min_diameter_cloud = 3 * self.res

        #set optional minimum cloud area threshold
        if min_area:
            mincloud = min_area
        else:
            mincloud = (np.pi * min_diameter_cloud**2)

        # min number of pixels in circular cloud
        pix_nb = mincloud / self.res**2  # ~ 500km2 cloud = 20 pixel at 5km res

        badinds = u[(n < pix_nb)]
        goodinds = u[n >= pix_nb]

        area_img = np.zeros_like(outt)
        for bi in badinds:
            inds = np.where(labels == bi)
            outt[inds] = 0
        for bi in goodinds:
            inds = np.where(labels==bi)
            area_img[inds]= int(len(inds[0]))#*self.res**2

        #detect edge for optional edge smoothing
        outt[outt >= self.Twav] = 150
        grad = np.gradient(outt)
        outt[outt == 150] = np.nan

        invalid = np.isnan(outt)

        # T difference between cloud edge and background
        if dynamic_background:
            tdiff = np.nanmax(outt) - np.nanmin(outt)
            xmin = 0.5*tdiff
        else:
            xmin = 10

        outt[invalid] = self.Twav - xmin

        if edge_smoothing:
            nok = np.where(abs(grad[0]) > 80)
            d = 2
            i = nok[0]
            j = nok[1]

            for ii, jj in zip(i, j):
                kern = outt[ii - d:ii + d + 1, jj - d:jj + d + 1]
                outt[ii - d:ii + d + 1, jj - d:jj + d + 1] = ndimage.gaussian_filter(kern, 3, mode='nearest')


        self.image = outt

        self.minPixel = pix_nb
        self.area = area_img
        self.invalid = invalid
        self.lon = lon
        self.lat = lat



    def applyWavelet(self, ge_thresh=0, fill=0.01, le_thresh=None, normed='scale'):
        """
        Applies the wavelet functions and handles wavelet coefficient filtering.
        :param ge_thresh: greater-equal threshold for coefficient filtering.
        :param fill: fill value for filtering thresholds
        :param le_thresh: less-equal threshold for coefficient filtering.
        :return: Wavelet coefficient and wavelet power attributes of the wavelet object.
        """

        try:
            tir = self.image.copy()
        except NameError:
            print('No image found to apply wavelet. Please read in an image first.')
            return


        print('Wavelet coefficients and power normed by:', normed, 'Possible tags: "scale", "stddev"')


        tir[tir > 0] = 0
        tir = tir - np.mean(tir)

        obj = wav.wavelet(self.res, self.dist, self.nb, start=self.start)

        coeffsTIR, powerTIR = obj.calc_coeffs(tir, ge_thresh=ge_thresh, fill=fill, le_thresh=le_thresh, normed=normed)

        self.power = powerTIR
        self.coeffs = coeffsTIR

        del tir



    def scaleWeighting(self, wtype='sum', data_tag='MSG'):
        """
         Accesses the wavelet power filtering utility functions.
        :param wtype: Defines method for wavelet power weighting and core identification
        :param data_tag: Identifies input data if needed for wtype
        :return: power from weighted scales
        """

        if wtype not in constants.UTILS:
            print('Method type not found. Choose one of existing power weighting methods (UTILS in constants.py) or add a new one.')
            return

        self.data_tag = data_tag

        Sweighting = constants.UTILS[wtype]
        self.scale_weighted = Sweighting(self)
        if isinstance(self.scale_weighted, tuple):
            self.max_pos = self.scale_weighted[1]
            self.scale_weighted = self.scale_weighted[0]
            return (self.scale_weighted, self.max_pos)
        else:
            return self.scale_weighted


    def to_dataarray(self, filepath=None, date=None, CLOBBER=False, names=None, scale_factor=False):
        """
        Optional data saving function. Saves wavelet power and storm-filtered tir to netCDF files.
        :param filepath: outpath for save file
        :param date: optional datetime.datetime date for timestamp in data array
        :param CLOBBER: if True, overwrites existing file
        :param names: [str, str] format, gives custom names to power and thermal infrared (tir) data arrays.
                      If False: ['power', 'tir']
        :return: saves netcdf of xarray dataset with convective core power and original tir data
        """

        new_savet = self.original.copy()
        isnan = np.isnan(new_savet)
        new_savet[isnan] = 0

        if scale_factor:
            sfactor=100
            dtype = np.int16
        else:
            sfactor=1
            dtype=np.int8
        try:
            new_savet = (np.round(new_savet, 2) * sfactor).astype(dtype)
        except TypeError:
            print('TIR data is None, DataArray conversion failed. Return')
            return
        try:
            new_power = (np.round(self.scale_weighted.copy(), 0)).astype(np.int16)

        except TypeError:
            print('TIR data is None, DataArray conversion failed. Return')
            return
        #new_power = self.scale_weighted


        if self.lat.ndim == 2:
            latitudes = self.lat[:, 0]
        else:
            latitudes = self.lat
        if self.lon.ndim == 2:
            longitudes = self.lon[0, :]
        else:
            longitudes = self.lon

        ds = xr.Dataset()

        # latitudes = np.arange(len(latitudes)).astype(int)
        # longitudes = np.arange(len(longitudes)).astype(int)




        if date:
            if new_power.ndim > 2:

                try:
                    power_da = xr.DataArray(new_power[np.newaxis, :], coords={'time': date, 'scales': np.round(self.scales).astype(np.uint8),
                                                           'lat': latitudes, 'lon': longitudes},  # [np.newaxis, :]
                                        dims=['time', 'scales', 'lat', 'lon'])
                except ValueError:
                    print('Could not create xarray, return')
                    return

            else:
                try:
                    power_da = xr.DataArray(new_power[np.newaxis, :], coords={'time': date,'lat': latitudes, 'lon': longitudes},
                                        dims=['time', 'lat', 'lon'])
                except ValueError:
                    print('Could not create xarray, return')
                    return


            tir_da = xr.DataArray(new_savet[np.newaxis, :], coords={'time': date, 'lat': latitudes, 'lon': longitudes},  # 'time': date,
                               dims=['time', 'lat', 'lon'])

        else:

            if new_power.ndim > 2:

                try:
                    power_da = xr.DataArray(new_power,
                                            coords={'scales': np.round(self.scales).astype(np.uint8),
                                                    'lat': latitudes, 'lon': longitudes},  # [np.newaxis, :]
                                            dims=['scales', 'lat', 'lon'])
                except ValueError:
                    print('Could not create xarray, return')
                    return
            else:

                power_da = xr.DataArray(new_power,
                                        coords={'lat': latitudes, 'lon': longitudes},  # [np.newaxis, :]
                                        dims=['lat', 'lon'])


            tir_da = xr.DataArray(new_savet, coords={'lat': latitudes, 'lon': longitudes},
                                  dims=['lat', 'lon'])
        if names is not None:
            power = names[0]
            tir = names[1]
        else:
            power = 'power'
            tir = 'tir'

        ds[power] = power_da
        ds[tir] = tir_da

        ds.attrs['radii'] = (np.floor(self.scales / 2. / float(self.res))).astype(np.uint8)
        ds.attrs['scales_rounded'] = np.round(self.scales).astype(np.uint8)
        ds.attrs['scales_original'] = self.scales
        ds.attrs['cutout_T'] = self.Tcut
        ds.attrs['cutout_minPixelNb'] = self.minPixel
        ds.attrs['scaling_factor'] = sfactor
        ds.attrs['assumed_resolution'] = self.res

        if filepath:

            if CLOBBER:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            comp = dict(zlib=True, complevel=5)
            enc = {var: comp for var in ds.data_vars}

            ds.to_netcdf(path=filepath, mode='w', encoding=enc, format='NETCDF4')
            print('Saved ' + filepath)

        else:

            return ds















