#!/usr/bin/env python
"""
This script will create 12-year season climatology plots AND stackplots.
"""

import os
import shutil
import glob
import string
letters = string.ascii_lowercase

import datetime
import calendar

import tqdm

import numpy as np
import scipy as sp
import scipy.stats
import pandas as pd
import xarray as xr
# from datetime import datetime

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection

# https://colorcet.holoviz.org/user_guide/Continuous.html
import colorcet

import warnings
warnings.filterwarnings(action='ignore', message='Mean of empty slice')

import merra2CipsAirsTimeSeries
import gnss_dtec_gw
import lstid_ham
import HIAMCM
import sme_plot

hemisphere = "Northern"

pd.set_option('display.max_rows', None)

mpl.rcParams['font.size']      = 12
mpl.rcParams['font.weight']    = 'bold'
mpl.rcParams['axes.grid']      = True
mpl.rcParams['grid.linestyle'] = ':'
mpl.rcParams['figure.figsize'] = np.array([15, 8])
mpl.rcParams['axes.xmargin']   = 0

#cbar_title_fontdict     = {'weight':'bold','size':30}
#cbar_ytick_fontdict     = {'size':30}
#xtick_fontdict          = {'weight': 'bold', 'size':30}
#ytick_major_fontdict    = {'weight': 'bold', 'size':28}
#ytick_minor_fontdict    = {'weight': 'bold', 'size':24}
#corr_legend_fontdict    = {'weight': 'bold', 'size':24}
#keo_legend_fontdict     = {'weight': 'normal', 'size':30}
#driver_xlabel_fontdict  = ytick_major_fontdict
#driver_ylabel_fontdict  = ytick_major_fontdict
#title_fontdict          = {'weight': 'bold', 'size':36}

cbar_title_fontdict     = {'weight':'bold','size':42}
cbar_ytick_fontdict     = {'size':36}
xtick_fontdict          = {'weight': 'bold', 'size':24}
ytick_major_fontdict    = {'weight': 'bold', 'size':24}
ytick_minor_fontdict    = {'weight': 'bold', 'size':24}
title_fontdict          = {'weight': 'bold', 'size':60}
ylabel_fontdict         = {'weight': 'bold', 'size':24}
reduced_legend_fontdict = {'weight': 'bold', 'size':20}

prm_dct = {}
prmd = prm_dct['meanSubIntSpect_by_rtiCnt'] = {}
prmd['scale_0']         = -0.025
prmd['scale_1']         =  0.025
prmd['cmap']            = mpl.cm.jet
prmd['cbar_label']      = 'MSTID Index'
prmd['cbar_tick_fmt']   = '%0.3f'
prmd['title']           = '{} Hemisphere SuperDARN MSTID Index'.format(hemisphere)
prmd['hist_bins']       = np.arange(-0.050,0.051,0.001)

prmd = prm_dct['meanSubIntSpect'] = {}
prmd['hist_bins']       = np.arange(-1500,1500,50)

prmd = prm_dct['intSpect_by_rtiCnt'] = {}
prmd['hist_bins']       = np.arange(0.,0.126,0.001)

prmd = prm_dct['intSpect'] = {}
prmd['hist_bins']       = np.arange(0.,2025,25)

prmd = prm_dct['sig_001_azm_deg'] = {}
prmd['scale_0']         = -180
prmd['scale_1']         =  180
#prmd['cmap']            = mpl.cm.hsv
# https://colorcet.holoviz.org/user_guide/Continuous.html
prmd['cmap']            = mpl.cm.get_cmap('cet_CET_C6') #colorcet.cyclic_rygcbmr_50_90_c64
prmd['cbar_label']      = 'MSTID Azimuth [deg]'
prmd['cbar_tick_fmt']   = '%.0f'
prmd['title']           = 'SuperDARN MSTID Propagation Azimuth'
prmd['hist_bins']       = np.arange(-180,185,10)
prmd['hist_polar']      = True

prmd = prm_dct['sig_001_vel_mps'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 300
prmd['hist_bins']       = np.arange(0,500,10)
prmd['cbar_label']      = 'MSTID Speed [m/s]'
prmd['cbar_tick_fmt']   = '%.0f'
prmd['title']           = 'SuperDARN MSTID Speed'

prmd = prm_dct['sig_001_period_min'] = {}
prmd['scale_0']         = 15
prmd['scale_1']         = 60
prmd['cbar_label']      = 'MSTID Period [min]'
prmd['cbar_tick_fmt']   = '%.0f'
prmd['title']           = 'SuperDARN MSTID Period'
prmd['hist_bins']       = np.arange(15,65,2.5)

prmd = prm_dct['sig_001_lambda_km'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 500
prmd['cbar_label']      = 'Horizontal Wavelength [km]'
prmd['cbar_tick_fmt']   = '%.0f'
prmd['title']           = 'SuperDARN Horizontal Wavelength'

prmd = prm_dct['meanSubIntSpect_by_rtiCnt_reducedIndex'] = {}
prmd['title']           = 'Reduced SuperDARN MSTID Index'
prmd['ylabel']          = 'Reduced SuperDARN\nMSTID Index'
prmd['ylim']            = (-5,5)

prmd = prm_dct['U_10HPA'] = {}
prmd['scale_0']         = -100.
prmd['scale_1']         =  100.
prmd['cmap']            = mpl.cm.bwr
prmd['cbar_label']      = 'U 10 hPa [m/s]'
prmd['title']           = 'MERRA2 Zonal Winds 10 hPa [m/s]'
prmd['data_dir']        = os.path.join('data','merra2','preprocessed')

prmd = prm_dct['U_1HPA'] = {}
prmd['scale_0']         = -100.
prmd['scale_1']         =  100.
prmd['cmap']            = mpl.cm.bwr
prmd['cbar_label']      = 'U 1 hPa [m/s]'
prmd['title']           = 'MERRA2 Zonal Winds 1 hPa [m/s]'
prmd['data_dir']        = os.path.join('data','merra2','preprocessed')

# ['DAILY_SUNSPOT_NO_', 'DAILY_F10.7_', '1-H_DST_nT', '1-H_AE_nT']
# DAILY_SUNSPOT_NO_  DAILY_F10.7_    1-H_DST_nT     1-H_AE_nT
# count       40488.000000  40488.000000  40488.000000  40488.000000
# mean           58.125963    103.032365    -10.984427    162.772167
# std            46.528777     29.990254     16.764279    175.810863
# min             0.000000     64.600000   -229.500000      3.500000
# 25%            17.000000     76.400000    -18.000000     46.000000
# 50%            50.000000     97.600000     -8.000000     92.000000
# 75%            90.000000    122.900000     -0.500000    215.000000
# max           220.000000    255.000000     64.000000   1637.000000

prmd = prm_dct['DAILY_SUNSPOT_NO_'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 175.
prmd['cmap']            = mpl.cm.cividis
prmd['cbar_label']      = 'Daily SN'
prmd['title']           = 'Daily Sunspot Number'
prmd['data_dir']        = os.path.join('data','cdaweb_omni','preprocessed')

prmd = prm_dct['DAILY_F10.7_'] = {}
prmd['scale_0']         = 50.
prmd['scale_1']         = 200.
prmd['cmap']            = mpl.cm.cividis
prmd['cbar_label']      = 'Daily F10.7'
prmd['title']           = 'Daily F10.7 Solar Flux'
prmd['data_dir']        = os.path.join('data','cdaweb_omni','preprocessed')

prmd = prm_dct['1-H_DST_nT'] = {}
prmd['scale_0']         =  -75
prmd['scale_1']         =   25
prmd['cmap']            = mpl.cm.inferno_r
prmd['cbar_label']      = 'Dst [nT]'
prmd['title']           = 'Disturbance Storm Time Dst Index [nT]'
prmd['data_dir']        = os.path.join('data','cdaweb_omni','preprocessed')

prmd = prm_dct['1-H_AE_nT'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 400
prmd['cmap']            = mpl.cm.viridis
prmd['cbar_label']      = 'AE [nT]'
prmd['title']           = 'Auroral Electrojet AE Index [nT]'
prmd['data_dir']        = os.path.join('data','cdaweb_omni','preprocessed')

prmd = prm_dct['OMNI_R_Sunspot_Number'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 175.
prmd['cmap']            = mpl.cm.cividis
prmd['cbar_label']      = 'Daily SN'
prmd['title']           = 'Daily Sunspot Number'
prmd['data_dir']        = os.path.join('data','omni','preprocessed')

prmd = prm_dct['OMNI_F10.7'] = {}
prmd['scale_0']         = 50.
prmd['scale_1']         = 200.
prmd['cmap']            = mpl.cm.cividis
prmd['cbar_label']      = 'Daily F10.7'
prmd['title']           = 'Daily F10.7 Solar Flux'
prmd['data_dir']        = os.path.join('data','omni','preprocessed')

prmd = prm_dct['OMNI_Dst'] = {}
prmd['scale_0']         =  -75
prmd['scale_1']         =   25
prmd['cmap']            = mpl.cm.inferno_r
prmd['cbar_label']      = 'Dst [nT]'
prmd['title']           = 'Disturbance Storm Time Dst Index [nT]'
prmd['data_dir']        = os.path.join('data','omni','preprocessed')

prmd = prm_dct['OMNI_AE'] = {}
prmd['scale_0']         = 0
prmd['scale_1']         = 400
prmd['cmap']            = mpl.cm.viridis
prmd['cbar_label']      = 'AE [nT]'
prmd['title']           = 'Auroral Electrojet AE Index [nT]'
prmd['data_dir']        = os.path.join('data','omni','preprocessed')

prmd = prm_dct['merra2CipsAirsTimeSeries'] = {}
prmd['scale_0']         = -20
prmd['scale_1']         = 100
prmd['levels']          = 11
prmd['cmap']            = 'jet'
prmd['cbar_label']      = 'MERRA-2 Zonal Wind\n[m/s] (50\N{DEGREE SIGN} N)'
prmd['title']           = 'MERRA-2 Zonal Winds + CIPS & AIRS GW Variance'

prmd = prm_dct['gnss_dtec_gw'] = {}
prmd['cmap']            = 'jet'
prmd['cbar_label']      = 'aTEC Amplitude (TECu)'
prmd['title']           = 'GNSS aTEC Amplitude at 115\N{DEGREE SIGN} W'

prmd = prm_dct['lstid_ham'] = {}
prmd['title']           = 'Amateur Radio 14 MHz LSTID Observations'

prmd = prm_dct['sme'] = {}
prmd['title']           = 'SuperMAG Electrojet Index (SME)'

# prmd = prm_dct['reject_code'] = {}
# prmd['title']           = 'MSTID Index Data Quality Flag'

# Reject code colors.
reject_codes = {}
# 0: Good Period (Not Rejected)
reject_codes[0] = {'color': mpl.colors.to_rgba('green'),  'label': 'Good Period'}
# 1: High Terminator Fraction (Dawn/Dusk in Observational Window)
reject_codes[1] = {'color': mpl.colors.to_rgba('blue'),   'label': 'Dawn / Dusk'}
# 2: No Data
reject_codes[2] = {'color': mpl.colors.to_rgba('red'),    'label': 'No Data'}
# 3: Poor Data Quality (including "Low RTI Fraction" and "Failed Quality Check")
reject_codes[3] = {'color': mpl.colors.to_rgba('gold'),   'label': 'Poor Data Quality'}
# 4: Other (including "No RTI Fraction" and "No Terminator Fraction")
reject_codes[4] = {'color': mpl.colors.to_rgba('purple'), 'label': 'Other'}
# 5: Not Requested (Outside of requested daylight times)
reject_codes[5] = {'color': mpl.colors.to_rgba('0.9'),   'label': 'Not Requested'}

def season_to_datetime(season):
    str_0, str_1 = season.split('_')
    sDate   = datetime.datetime.strptime(str_0,'%Y%m%d')
    eDate   = datetime.datetime.strptime(str_1,'%Y%m%d')
    return (sDate,eDate)

def plot_cbar(ax_info):
    cbar_pcoll = ax_info.get('cbar_pcoll')

    cbar_label      = ax_info.get('cbar_label')
    cbar_ticks      = ax_info.get('cbar_ticks')
    cbar_tick_fmt   = ax_info.get('cbar_tick_fmt','%0.3f')
    cbar_tb_vis     = ax_info.get('cbar_tb_vis',False)
    ax              = ax_info.get('ax')

    fig = ax.get_figure()

    box         = ax.get_position()

    x0  = 1.01
    wdt = 0.015
    y0  = 0.250
    hgt = (1-2.*y0)
    axColor = fig.add_axes([x0, y0, wdt, hgt])

    axColor.grid(False)
    cbar        = fig.colorbar(cbar_pcoll,orientation='vertical',cax=axColor,format=cbar_tick_fmt)

    cbar.set_label(cbar_label,fontdict=cbar_title_fontdict)
    if cbar_ticks is not None:
        cbar.set_ticks(cbar_ticks)

    axColor.set_ylim( *(cbar_pcoll.get_clim()) )

    labels = cbar.ax.get_yticklabels()
    fontweight  = cbar_ytick_fontdict.get('weight')
    fontsize    = cbar_ytick_fontdict.get('size')
    for label in labels:
        if fontweight:
            label.set_fontweight(fontweight)
        if fontsize:
            label.set_fontsize(fontsize)

#    if not cbar_tb_vis:
#        for inx in [0,-1]:
#            labels[inx].set_visible(False)

def reject_legend(fig):
    x0  = 1.01
    wdt = 0.015
    y0  = 0.250
    hgt = (1-2.*y0)

    axl= fig.add_axes([x0, y0, wdt, hgt])
    axl.axis('off')

    legend_elements = []
    for rej_code, rej_dct in reject_codes.items():
        color = rej_dct['color']
        label = rej_dct['label']
        # legend_elements.append(mpl.lines.Line2D([0], [0], ls='',marker='s', color=color, label=label,markersize=15))
        legend_elements.append(mpl.patches.Patch(facecolor=color,edgecolor=color,label=label))

    axl.legend(handles=legend_elements, loc='center left', fontsize = 42)

def my_xticks(sDate,eDate,ax,radar_ax=False,labels=True,short_labels=False,
        fontdict=None,plot_axvline=True):
    if fontdict is None:
        fontdict = xtick_fontdict
    xticks      = []
    xticklabels = []
    curr_date   = sDate
    while curr_date < eDate:
        if radar_ax:
            xpos    = get_x_coords(curr_date,sDate,eDate)
        else:
            xpos    = curr_date
        xticks.append(xpos)
        xticklabels.append('')
        curr_date += datetime.timedelta(days=1)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    # Define xtick label positions here.
    # Days of month to produce a xtick label.
    doms    = [1,15]

    curr_date   = sDate
    ytransaxes = mpl.transforms.blended_transform_factory(ax.transData,ax.transAxes)
    while curr_date < eDate:
        if curr_date.day in doms:
            if radar_ax:
                xpos    = get_x_coords(curr_date,sDate,eDate)
            else:
                xpos    = curr_date

            if plot_axvline:
                axvline = ax.axvline(xpos,-0.015,color='k')
                axvline.set_clip_on(False)

            if labels:
                ypos    = -0.025
                txt     = curr_date.strftime('%d %b')
                ax.text(xpos,ypos,txt,transform=ytransaxes,
                        ha='left', va='top',rotation=0,
                        fontdict=fontdict)
            # if short_labels:    
            #     if curr_date.day == 1:
            #         ypos    = -0.025
            #         txt     = curr_date.strftime('%b %Y')
            #         ax.text(xpos,ypos,txt,transform=ytransaxes,
            #                 ha='left', va='top',rotation=0,
            #                 fontdict=fontdict)
        curr_date += datetime.timedelta(days=1)

    xmax    = (eDate - sDate).total_seconds() / (86400.)
    if radar_ax:
        ax.set_xlim(0,xmax)
    else:
        ax.set_xlim(sDate,sDate+datetime.timedelta(days=xmax))

#    ax.grid(zorder=500)

def get_x_coords(win_sDate,sDate,eDate,full=False):
    x1  = (win_sDate - sDate).total_seconds()/86400.
    if not full:
        x1  = np.floor(x1)
    return x1

def get_y_coords(ut_time,st_uts,radar,radars):
    # Find start time index.
    st_uts      = np.array(st_uts)
    st_ut_inx   = np.digitize([ut_time],st_uts)-1
    
    # Find radar index.
    radar_inx   = np.where(radar == np.array(radars))[0]
    y1          = st_ut_inx*len(radars) + radar_inx
    return y1


def get_coords(radar,win_sDate,radars,sDate,eDate,st_uts,verts=True):
    # Y-coordinate.
    x1  = float(get_x_coords(win_sDate,sDate,eDate))
    try:
        y1  = float(get_y_coords(win_sDate.hour,st_uts,radar,radars)[0])
    except:
        print("That float conversion error on radar {}".format(radar))
        y1  = float(get_y_coords(win_sDate.hour,st_uts,radar,radars)[0])

    if verts:
#        x1,y1   = x1+0,y1+0
        x2,y2   = x1+1,y1+0
        x3,y3   = x1+1,y1+1
        x4,y4   = x1+0,y1+1
        return ((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1))
    else:
        x0      = x1 + 0.5
        y0      = y1 + 0.5
        return (x0, y0)

def plot_mstid_values(data_df,ax,sDate=None,eDate=None,
        st_uts=[14, 16, 18, 20],
        xlabels=True, group_name=None,classification_colors=False,
        rasterized=False,radars=None,radar_labels=None,param=None,**kwargs):

    prmd        = prm_dct.get(param,{})

#    scale_0     = prmd.get('scale_0',-0.025)
#    scale_1     = prmd.get('scale_1', 0.025)

    scale_0     = prmd.get('scale_0')
    scale_1     = prmd.get('scale_1')
    if scale_0 is None:
        scale_0 = np.nanmin(data_df.values)
    if scale_1 is None:
        scale_1 = np.nanmax(data_df.values)
    scale       = (scale_0, scale_1)

    cmap        = prmd.get('cmap',mpl.cm.jet)
    cbar_label  = prmd.get('cbar_label',param)

    if sDate is None:
        sDate = data_df.index.min()
        sDate = datetime.datetime(sDate.year,sDate.month,sDate.day)

        eDate = data_df.index.max()
        eDate = datetime.datetime(eDate.year,eDate.month,eDate.day) + datetime.timedelta(days=1)

    if radars is None:
        radars  = list(data_df.keys())
    # Reverse radars list order so that the supplied list is plotted top-down.
    radars  = radars[::-1]
    # Height of y
    ymax    = len(st_uts) * len(radars)

    cbar_info   = {}
    bounds      = np.linspace(scale[0],scale[1],256)
    cbar_info['cbar_ticks'] = np.linspace(scale[0],scale[1],11)
    cbar_info['cbar_label'] = cbar_label

    norm    = mpl.colors.BoundaryNorm(bounds,cmap.N)

    if classification_colors:
        # Use colorscheme that matches MSTID Index in classification plots.
        from mstid.classify import MyColors
        scale_0             = -0.025
        scale_1             =  0.025
        my_cmap             = 'seismic'
        truncate_cmap       = (0.1, 0.9)
        my_colors           = MyColors((scale_0, scale_1),my_cmap=my_cmap,truncate_cmap=truncate_cmap)
        cmap                = my_colors.cmap
        norm                = my_colors.norm
                

    ################################################################################    
    current_date = sDate
    verts       = []
    vals        = []
    while current_date < eDate:
        for st_ut in st_uts:
            for radar in radars:
                win_sDate   = current_date + datetime.timedelta(hours=st_ut)

                val = data_df[radar].loc[win_sDate]

                if not np.isfinite(val):
                    continue

                if param == 'reject_code':
                    val = reject_codes.get(val,reject_codes[4])['color']

                vals.append(val)
                verts.append(get_coords(radar,win_sDate,radars,sDate,eDate,st_uts))

        current_date += datetime.timedelta(days=1)

    if param == 'reject_code':
        pcoll = PolyCollection(np.array(verts),edgecolors='0.75',linewidths=0.25,
                cmap=cmap,norm=norm,zorder=99,rasterized=rasterized)
        pcoll.set_facecolors(np.array(vals))
        ax.add_collection(pcoll,autolim=False)
    else:
        pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,
                cmap=cmap,norm=norm,zorder=99,rasterized=rasterized)
        pcoll.set_array(np.array(vals))
        ax.add_collection(pcoll,autolim=False)

    # Make gray missing data.
    ax.set_facecolor('0.90')

    # Add radar labels.
    trans = mpl.transforms.blended_transform_factory(ax.transAxes,ax.transData)
    for rdr_inx,radar in enumerate(radars):
        for st_inx,st_ut in enumerate(st_uts):
            # import ipdb; ipdb.set_trace()
            ypos = len(radars)*st_inx + rdr_inx + 0.5
            if radar_labels:
                ax.text(-0.002,ypos,radar_labels[season][radar][st_inx],transform=trans,ha='right',va='center')
            else:
                ax.text(-0.002,ypos,radar,transform=trans,ha='right',va='center')

    # Add UT Time Labels
    for st_inx,st_ut in enumerate(st_uts):
        ypos    = st_inx*len(radars)
        xpos    = -0.035
        line    = ax.hlines(ypos,xpos,1.0,transform=trans,lw=3,zorder=100)
        line.set_clip_on(False)
        
        txt     = '{:02d}-{:02d}\nUT'.format(int(st_ut),int(st_ut+2))
        ypos   += len(radars)/2.
        xpos    = -0.025
#        ax.text(xpos,ypos,txt,transform=trans,
#                ha='center',va='center',rotation=90,fontdict=ytick_major_fontdict)
#        xpos    = -0.015
#        xpos    = -0.05
        xpos    = -0.025
        ax.text(xpos,ypos,txt,transform=trans,
                ha='right',va='center',rotation=0,fontdict=ytick_major_fontdict)

    xpos    = -0.035
    line    = ax.hlines(1.,xpos,1.0,transform=ax.transAxes,lw=3,zorder=100)
    line.set_clip_on(False)

    ax.set_ylim(0,ymax)

    # Set xticks and yticks to every unit to make a nice grid.
    # However, do not use this for actual labeling.
    yticks = list(range(len(radars)*len(st_uts)))
    ax.set_yticks(yticks)
    ytls = ax.get_yticklabels()
    for ytl in ytls:
        ytl.set_visible(False)

    my_xticks(sDate,eDate,ax,radar_ax=True,labels=xlabels)
    
    txt = ' '.join([x.upper() for x in radars[::-1]])
    if group_name is not None:
        txt = '{} ({})'.format(group_name,txt)
    ax.set_title(txt,fontdict=title_fontdict)

    ax.set_title('',loc='right',fontdict=title_fontdict)

    ax_info         = {}
    ax_info['ax']   = ax
    ax_info['cbar_pcoll']   = pcoll
    ax_info['cbar_tick_fmt']= prmd.get('cbar_tick_fmt')
    ax_info.update(cbar_info)
    
    return ax_info

def list_seasons(yr_0=2010,yr_1=2022):
    """
    Give a list of the string codes for the default seasons to be analyzed.

    Season codes are in the form of '20101101_20110501'
    """
    yr = yr_0
    seasons = []
    while yr < yr_1:
        dt_0 = datetime.datetime(yr,1,1)
        dt_1 = datetime.datetime(yr+1,1,1)

        dt_0_str    = dt_0.strftime('%Y%m%d')
        dt_1_str    = dt_1.strftime('%Y%m%d')
        season      = '{!s}_{!s}'.format(dt_0_str,dt_1_str)
        seasons.append(season)
        yr += 1
    return seasons
def index_to_ts_i(ts):
    return int(ts.time().hour / 2)
def get_data_count_radar(dd_y_df):
    counts = [{},{},{},{},{},{},{},{},{},{},{},{}]
    for radar in dd_y_df:
        for c in counts:
            c[radar] = 0
        for ts in dd_y_df[radar].index:
            hour = index_to_ts_i(ts)
            if not np.isnan(dd_y_df[radar][ts]):
                counts[hour][radar] += 1
    return counts
def get_best_radars(dd_y_df):
    counts = get_data_count_radar(dd_y_df)
    top = [[],[],[],[]]
    for ts in counts:
        for i in range(4):
            max_radar = max(ts,key=ts.get)
            top[i].append(max_radar)
            ts[max_radar] = -1
    # import ipdb;ipdb.set_trace()
    return top
# selects data for a particular radar given a time series
def select_ts(ts, df_r):
    # condition = index_to_ts_i(df_r.index) == ts
    return df_r.loc[[index_to_ts_i(t) == ts for t in df_r.index]]
# Modifies a dataDct so that it only includes the top 4 radars for a given time series
def modify_for_best(dataDct):
    # import ipdb;ipdb.set_trace()
    new_radars = []
    for i in range(4):
        radar_name = "v_{}".format(i)
        new_radars.append(radar_name)
    radar_labels = {}
    for year in dataDct:
        dd_y = dataDct[year]
        dd_y['attrs_radars'] = {}
        df = dd_y['df']
        best_radars = get_best_radars(df)
        v_radar_data = []
        radar_labels[year] = {}
        for dex, vrum in enumerate(best_radars):
            ts_list = []
            for i, radar in enumerate(vrum):
                ts_list.append(select_ts(i,df[radar]))
            v_radar_data.append(pd.concat(ts_list))
            radar_name = "v_{}".format(dex)
            v_radar_data[-1].name = radar_name
            radar_labels[year][radar_name] = vrum
        new_df = pd.concat(v_radar_data,axis=1)
        dd_y['df'] = new_df
    # import ipdb; ipdb.set_trace()
    return new_radars, radar_labels
def remove_year_from_index(index):
    return index.replace(year=2000)
def normalize_series(r_series):
    series_c = r_series.copy()
    series_c.index = series_c.index.map(remove_year_from_index)
    return series_c
# merges together all seasons within the dataDct into one merged season
def merge_seasons(dataDct):
    radar_season = {}
    for season in dataDct:
        dd_s_df = dataDct[season]['df']
        for radar in dd_s_df:
            r_series = dd_s_df[radar]
            if radar not in radar_season:
                radar_season[radar] = []
            
            radar_season[radar].append(normalize_series(r_series))
            # import ipdb; ipdb.set_trace()
    new_index = pd.date_range(start=datetime.datetime(year=2001,month=1,day=1),end=datetime.datetime(year=2002,month=1,day=1),periods=4381)[:-1]
    for radar in radar_season:
        radar_season[radar] = pd.concat(radar_season[radar],axis=1).mean(axis=1,skipna=True)
    new_df = pd.concat(radar_season,axis=1)
    dataDct['20000101_20010101'] = {}
    dataDct['20000101_20010101']['df'] = new_df
    # import ipdb;ipdb.set_trace()
class ParameterObject(object):
    def __init__(self,param,radars,seasons=None,
            output_dir='output',default_data_dir=os.path.join('data','mstid_index'),
            write_csvs=True,calculate_reduced=False):
        """
        Create a single, unified object for loading in SuperDARN MSTID Index data
        generated by the DARNTIDs library and output to CSV by mongo_to_csv.py.
        """

        # Create a Global Attributes dictionary that will be be applicable to all seasons
        # and printed out in the CSV file header.
        self.attrs_global = {}

        # Create parameter dictionary.
        prmd        = prm_dct.get(param,{})
        prmd['param'] = param
        if prmd.get('data_dir') is None:
            prmd['data_dir'] = default_data_dir
        self.prmd   = prmd

        # Store radar list.
        self.radars = radars
        self.attrs_global['radars']    = radars

        # Get list of seasons.
        if seasons is None:
            # Do Not set Seasons here
            # It does not work
            seasons = list_seasons()
        self.attrs_global['seasons']    = seasons

        # Load data into dictionary of dataframes.
        self.data = {season:{} for season in seasons}
        print('Loading data...')
        self._load_data()

        # Create a attrs_season dict for each season to hold statistics and other info that applies
        # to all data in a season, not just individual radars.
        for season in seasons:
            self.data[season]['attrs_season']   = {}

        try:
            # Track and report minimum orig_rti_fraction.
            # This is the percentage of range-beam cells reporting scatter in an
            # observational window. It is a critical parameter to correctly calculate
            # the reduced MSTID index and other statistcal measures.
            orig_rti_fraction       = self._load_data('orig_rti_fraction',selfUpdate=False)

            # Only keep the RTI Fractions from ``good'' periods.
            reject_dataDct          = self._load_data('reject_code',selfUpdate=False)
            for season in seasons:
                bad = reject_dataDct[season]['df'] != 0
                orig_rti_fraction[season]['df'][bad] = np.nan
            self.orig_rti_fraction  = orig_rti_fraction

            # Calculate min_orig_rti_fraction for all loaded seasons.
            orf                     = self.flatten(orig_rti_fraction)
            min_orig_rti_fraction   = np.nanmin(orf)
            self.attrs_global['min_orig_rti_fraction']  = min_orig_rti_fraction

            # Calculate min_orig_rti_fraction for each individual season.
            for season in seasons:
                orf     = orig_rti_fraction[season]['df']
                min_orf = np.nanmin(orf.values)
                self.data[season]['attrs_season']['min_orig_rti_fraction'] = min_orf

            # Calculate min_orig_rti_fraction for each individual radar.
            for season in seasons:
                orf     = orig_rti_fraction[season]['df']
                for radar in radars:
                    min_orf = np.nanmin(orf[radar].values)
                    self.data[season]['attrs_radars'][radar]['min_orig_rti_fraction'] = min_orf
        except:
            print('   ERROR calulating min_orig_rti_fraction while creating ParameterObject for {!s}'.format(param))

        self.output_dir = output_dir
        # if write_csvs:
        #     print('Generating Season CSV Files...')
        #     for season in seasons:
        #         self.write_csv(season,output_dir=self.output_dir)

        #     csv_fpath   = os.path.join(self.output_dir,'radars.csv')
        #     self.lat_lons.to_csv(csv_fpath,index=False)



    def flatten(self,dataDct=None):
        """
        Return a single, flattened numpy array of all values from all seasons
        of a data dictionary. This is useful for calculating overall statistics.

        dataDct: Data dictionary to flatten. If None, use self.data.
        """
        if dataDct is None:
            dataDct = self.data

        data = []
        for season in dataDct.keys():
            tmp = dataDct[season]['df'].values.flatten()
            data.append(tmp)

        data = np.concatenate(data)
        return data

    def _load_data(self,param=None,selfUpdate=True):
        """
        Load data into data frames and store in self.data dictionary.
        
        param: Parameter to load. Use self.prmd.get('param') if None.
        selfUpdate:
            If True, update self.data and self.lat_lon with results and
                also return dictionary.
            If False, only return data dictionary.
        """

        data_dir    = self.prmd.get('data_dir')
        if param is None:
            param       = self.prmd.get('param')

        if selfUpdate is True:
            dataDct = self.data
        else:
            dataDct = {}
            for season in self.data.keys():
                dataDct[season] = {}

        lat_lons    = []
        for season in tqdm.tqdm(dataDct.keys(),desc='Seasons',dynamic_ncols=True,position=0):
            # Load all data from a season into a single xarray dataset.
            ds              = []
            attrs_radars    = {}

            data_vars = [] # Keep track of each column name in each data file.
            for radar in self.radars:
    #            fl  = os.path.join(data_dir,'sdMSTIDindex_{!s}_{!s}.nc'.format(season,radar))
                patt    = os.path.join(data_dir,'*{!s}_{!s}.nc'.format(season,radar))
                print('Loading: {!s}'.format(patt))
                try:
                    fl      = glob.glob(patt)[0]
                except:
                    fl = None
                    print('No data file found matching this pattern {}. Aborting'.format(patt))
                    return
                tqdm.tqdm.write('--> {!s}: {!s}'.format(param,fl))
                dsr = xr.open_dataset(fl)
                ds.append(dsr)
                attrs_radars[radar] = dsr.attrs

                # Store radar lat / lons to creat a radar location file.
                lat_lons.append({'radar':radar,'lat':dsr.attrs['lat'],'lon':dsr.attrs['lon']})

                data_vars += list(dsr.data_vars) # Add columns names from the current data file.

            # Loop through each data set and ensure it has all of the columns.
            # If not, add that column with NaNs.
            # This makes the later concatenation into an XArray much easier.
            data_vars = list(set(data_vars)) # Get the unique set of column names.
            for dsr in ds:
                dvs = list(dsr.data_vars) # Get list of variable names in the current dataset.
                for dv in data_vars: # Loop through all of the required variable names.
                    if dv not in dvs: # If not present in the current data set, add it
                        dsr[dv] = dsr['lat'].copy() * np.nan

            dss   = xr.concat(ds,dim='index')

            dss = dss.stack(new_index=[...],create_index=False)
            dss = dss.swap_dims({'new_index':'index'})
            dss = dss.set_index({'index':'date'})

            # Convert parameter of interest to a datafame.
            df      = dss[param].to_dataframe()
            dfrs = {}
            for radar in tqdm.tqdm(radars,desc='Radars',dynamic_ncols=True,position=1,leave=False):
                tf      = df['radar'] == radar
                dft     = df[tf]
                dates   = dft.index
                vals    = dft[param]

                for date,val in zip(dates,vals):
                    if date not in dfrs:
                        dfrs[date] = {}
                    dfrs[date][radar] = val

            df  = pd.DataFrame(dfrs.values(),dfrs.keys())
            df  = df.sort_index()
            df.index.name                   = 'datetime'
            dataDct[season]['df']           = df
            dataDct[season]['attrs_radars'] = attrs_radars

        # Clean up lat_lon data table
        if selfUpdate is True:
            self.lat_lons    = pd.DataFrame(lat_lons).drop_duplicates()
        merge_seasons(dataDct)
        self.radar_labels = None
        self.radars, self.radar_labels = modify_for_best(dataDct)
        self.merra2 = pd.read_csv("MERRA2.csv")
        self.merra2['DATE'] = pd.to_datetime(self.merra2['DATE'],format='%Y%m%d')
        # import ipdb; ipdb.set_trace()
        return dataDct

    def write_csv(self,season,output_dir=None):
        
        """
        Save data to CSV files.
        """

        param           = self.prmd.get('param')
        try:
            df              = self.data[season]['df']
        except:
            import ipdb; ipdb.set_trace()
        attrs_radars    = self.data[season]['attrs_radars']
        attrs_season    = self.data[season]['attrs_season']
        attrs_global    = self.attrs_global

        if output_dir is None:
            output_dir = self.output_dir

        csv_fname       = '{!s}_{!s}.csv'.format(season,param)
        csv_fpath       = os.path.join(output_dir,csv_fname)
        with open(csv_fpath,'w') as fl:
            hdr = []
            hdr.append('# SuperDARN MSTID Index Datafile')
            hdr.append('# Generated by Nathaniel Frissell, nathaniel.frissell@scranton.edu')
            hdr.append('# Generated on: {!s} UTC'.format(datetime.datetime.utcnow()))
            hdr.append('#')
            hdr.append('# Parameter: {!s}'.format(param))
            hdr.append('#')
            hdr.append('# Global Attributes (Applies to All Seasons Loaded in ParameterObject):')
            hdr.append('# {!s}'.format(attrs_global))

            hdr.append('#')
            hdr.append('# {!s} Season Attributes:'.format(season))
            hdr.append('# {!s}'.format(attrs_season))

            hdr.append('#')
            hdr.append('# Radar Attributes:')
            for radar,attr in attrs_radars.items():
                hdr.append('# {!s}: {!s}'.format(radar,attr))
            hdr.append('#')

            fl.write('\n'.join(hdr))
            fl.write('\n')
            
        df.to_csv(csv_fpath,mode='a')

    # def plot_climatology(self,output_dir=None):
    #     global hemisphere

    #     if output_dir is None:
    #         output_dir = self.output_dir

    #     seasons = self.data.keys()
    #     # import ipdb; ipdb.set_trace()
    #     radars  = self.radars
    #     param   = self.prmd['param']

    #     nrows   = 6
    #     ncols   = 2
    #     fig, ax = plt.subplots(figsize=(50,30))

    #     ax_list = []
    #     for inx,season in enumerate(seasons):
    #         print(' -->',season)
    #         # ax      = fig.add_subplot(nrows,ncols,inx+1)

    #         data_df = self.data[season]['df']
            
    #         sDate, eDate = season_to_datetime(season)
    #         ax_info = plot_mstid_values(data_df,ax,radars=radars,radar_labels=self.radar_labels,param=param,sDate=sDate,eDate=eDate,st_uts=list(range(0,24,2)))
    #         # ADD MERRA2 WINDS
    #         import ipdb; ipdb.set_trace()
    #         # ax.plot()
    #         # ENDADD
    #         min_orf   = po.data[season]['attrs_season'].get('min_orig_rti_fraction')
    #         ax_info['ax'].set_title('RTI Fraction > {:0.2f}'.format(min_orf),loc='right')
    #         ax_list.append(ax_info)

    #         season_yr0 = season[:4]
    #         season_yr1 = season[9:13]
    #         # txt = '{!s} - {!s} Southern Hemisphere'.format(season_yr0,season_yr1)
    #         ax.set_title("{} Hemisphere".format(hemisphere),fontdict=title_fontdict,fontsize=40)

    #     fig.tight_layout(w_pad=2.25)

    #     if param == 'reject_code':
    #         reject_legend(fig)
    #     else:
    #         if len(ax_list) == 1:
    #             cbar_ax_inx = 0
    #         else:
    #             cbar_ax_inx = 1
    #         plot_cbar(ax_list[cbar_ax_inx])

    #     fpath = os.path.join(output_dir,'{!s}.png'.format(param))
    #     print('SAVING: ',fpath)
    # #    fig.savefig(fpath)
    #     fig.savefig(fpath,bbox_inches='tight')

    # def plot_histograms(self,output_dir=None):
    #     if output_dir is None:
    #         output_dir = self.output_dir

    #     seasons = self.data.keys()
    #     radars  = self.radars
    #     param   = self.prmd['param']

    #     bins    = self.prmd.get('hist_bins',30)
    #     xlim    = self.prmd.get('hist_xlim',None)
    #     ylim    = self.prmd.get('hist_ylim',None)
    #     xlabel  = self.prmd.get('cbar_label',param)
    #     polar   = self.prmd.get('hist_polar',False)


    #     hist_dct    = {}
    #     ymax        = 1
    #     months      = []
    #     years       = []
    #     dates       = []
    #     for radar in radars:
    #         vals    = np.array([],dtype=float)
    #         for season,data_dct in self.data.items():
    #             df      = data_dct['df'][radar]
    #             tf      = np.isfinite(df.values)
    #             vals    = np.append(vals,df.values[tf])
    #             dates   = dates + df.index.tolist()

    #             if polar is True:
    #                 mean = sp.stats.circmean(vals,180.,-180.)
    #                 std  = sp.stats.circstd(vals,180.,-180.)
    #             else:
    #                 mean = np.mean(vals)
    #                 std  = np.std(vals)

    #             stats   = []
    #             stats.append('N: {:d}'.format(vals.size))
    #             stats.append('Mean: {:.1f}'.format(mean))
    #             stats.append('Std: {:.1f}'.format(std))

    #             dates   = list(set(dates))
    #             months  = list(set(months + [x.month for x in dates]))
    #             years   = list(set(years + [x.year for x in dates]))

    #         hist, bin_edges = np.histogram(vals,bins=bins)
    #         ymax    = np.max([ymax,np.max(hist)])

    #         tmp = {}
    #         tmp['hist']         = hist
    #         tmp['bin_edges']    = bin_edges
    #         tmp['stats']        = stats
    #         hist_dct[radar]     = tmp

    #     if xlim is None:
    #         xlim    = (np.min(bin_edges),np.max(bin_edges))

    #     if ylim is None:
    #         ylim    = (0, 1.025*ymax)

    #     rads_layout = {}
    #     rads_layout['pgr'] = (0,1)
    #     rads_layout['sas'] = (0,2)
    #     rads_layout['kap'] = (0,3)
    #     rads_layout['gbr'] = (0,4)

    #     rads_layout['cvw'] = (1,0)
    #     rads_layout['cve'] = (1,1)
    #     rads_layout['fhw'] = (1,2)
    #     rads_layout['fhe'] = (1,3)
    #     rads_layout['bks'] = (1,4)
    #     rads_layout['wal'] = (1,5)

    #     del_axs = []
    #     del_axs.append( (0,0) )
    #     del_axs.append( (0,5) )

    #     nrows           = 2
    #     ncols           = 6
    #     figsize         = (30,10)
    #     title_fontdict  = {'weight':'bold','size':18}
    #     label_fontdict  = {'weight':'bold','size':14}

    #     if polar is True:
    #         subplot_kw = {'projection':'polar'}
    #     else:
    #         subplot_kw = {}

    #     fig, axs = plt.subplots(nrows,ncols,figsize=figsize,subplot_kw=subplot_kw)
    #     for radar in radars:
    #         pos = rads_layout.get(radar)
    #         ax  = axs[pos]

    #         hist        = hist_dct[radar]['hist']
    #         bin_edges   = hist_dct[radar]['bin_edges']

    #         if polar is True:
    #             bin_edges   = np.radians(bin_edges)
    #             width       = np.diff(bin_edges)
    #             ax.bar(bin_edges[:-1],hist,width=width)
    #             ax.set_theta_zero_location("N")  # theta=0 at the top
    #             ax.set_theta_direction(-1)  # theta increasing clockwise
    #             stats_x = 0.800
    #             stats_y = 1.000
    #         else:
    #             width       = bin_edges[1]-bin_edges[0]
    #             ax.bar(bin_edges[:-1],hist,width=width)

    #             ax.set_xlabel(xlabel,fontdict=label_fontdict)
    #             ax.set_ylabel('Counts',fontdict=label_fontdict)

    #             ax.set_xlim(xlim)
    #             stats_x = 0.675
    #             stats_y = 0.975
    #         ax.set_ylim(ylim)

    #         stats       = hist_dct[radar]['stats']
    #         bbox        = {'boxstyle':'round','facecolor':'white','alpha':0.8}
    #         ax.text(stats_x,stats_y,'\n'.join(stats),va='top',transform=ax.transAxes,bbox=bbox)
    #         ax.set_title(radar,fontdict=title_fontdict)

    #     for del_ax in del_axs:
    #         ax  = axs[del_ax]
    #         ax.remove()

    #     title   = []
    #     title.append('Daytime '+self.prmd.get('title',param))
    #     year_str    = '{!s} - {!s}'.format(min(years),max(years))
    #     month_str   = ', '.join([calendar.month_abbr[x] for x in months])
    #     title.append('Years: {!s}; Months: {!s}'.format(year_str,month_str))
    #     fig.text(0.5,1.0,'\n'.join(title),ha='center',fontdict={'weight':'bold','size':28})

    #     fig.tight_layout()
    #     fpath = os.path.join(output_dir,'{!s}_histograms.png'.format(param))
    #     print('SAVING: ',fpath)
    #     fig.savefig(fpath,bbox_inches='tight')

def stackplot(po_dct,params,season,radars=None,sDate=None,eDate=None,fpath='stackplot.png',additional_data=None):
    global hemisphere
    _sDate, _eDate = season_to_datetime(season)
    if sDate is None:
        sDate = _sDate
    if eDate is None:
        eDate = _eDate

    print(' Plotting Stackplot: {!s}'.format(fpath))
    nrows   = len(params)
    ncols   = 1
    fig = plt.figure(figsize=(50,nrows*20)) # Change stackplot size

    ax_list = []
    # import ipdb; ipdb.set_trace()
    for inx,param in enumerate(params):
        # import ipdb; ipdb.set_trace()
        ax      = fig.add_subplot(nrows,ncols,inx+1)

        base_param      = param
        plotType        = 'climo'

        # Get Parameter Object
        po      = po_dct.get(base_param)

        try:
            data_df = po.data[season]['df']
        except:
            # ogkmig5ok0
            print('error IDd')
            import ipdb;ipdb.set_trace()
        prmd    = po.prmd

        if inx == nrows-1:
            xlabels = True
        else:
            xlabels = False

        if radars is None:
            _radars = po.radars
        else:
            _radars = radars
        # Begin MERRA2 CODE
        if additional_data:
            merra2_df_u = po_dct['meanSubIntSpect_by_rtiCnt'].merra2
            merra2_df = merra2_df_u.loc[merra2_df_u["DATE"].dt.year == _sDate.year]
            value_plot = additional_data
            ax2 = ax.twinx()
            ax2.yaxis.tick_right()
            ax2.yaxis.set_label_position('right')
            y = merra2_df[value_plot].tolist()
            ax2.plot(y, 'k', alpha=0.9,linewidth=10)
            ax2.set_ylabel(value_plot, fontsize=32)
            # calculate ranges
            yall = merra2_df_u[value_plot].tolist()
            # import ipdb; ipdb.set_trace()
            max_value = max(yall)
            min_value = min(yall)
            print("min={}, max={}".format(min_value, max_value))
            steps = (max_value - min_value) / 10
            max_value = max_value + steps
            # ax2.set_yticks(np.arange(min_value, max_value, steps))
            ax2.set_yticks(np.arange(-5,5,0.5))
        # END MERRA2 CODE
        # ax2.set_yticklabels([])
        # ax2.set_yticks([])
        # ax2.set_yticks(np.arange(-4.0, 4.2, 0.2))


        ax_info = plot_mstid_values(data_df,ax,radars=_radars,radar_labels=po.radar_labels,param=param,xlabels=xlabels,
                sDate=sDate,eDate=eDate,st_uts=list(range(0,24,2)))

        # min_orf   = po.data[season]['attrs_season'].get('min_orig_rti_fraction')
        # ax_info['ax'].set_title('RTI Fraction > {:0.2f}'.format(min_orf),loc='right')
        ax_info['radar_ax']     = True
        ax_list.append(ax_info)

        ylim    = prmd.get('ylim')
        if ylim is not None:
            ax.set_ylim(ylim)

        # ylabel  = prmd.get('ylabel')
        # if ylabel is not None:
        #     ax.set_ylabel(ylabel,fontdict=ylabel_fontdict)

        txt = '({!s}) '.format(letters[inx])+prmd.get('title',param)
        left_title_fontdict  = {'weight': 'bold', 'size': 24}
        ax.set_title('')
        ax.set_title(txt,fontdict=left_title_fontdict,loc='left')

        season_yr0 = season[:4]
        season_yr1 = season[9:13]
        # txt = '{!s} - {!s} Southern Hemisphere'.format(season_yr0,season_yr1)
        if season_yr0 == "2000":
            fig.text(0.5,1.0,"{} Hemisphere Multi Year Average".format(hemisphere),ha='center',fontdict=title_fontdict)
        else:
            fig.text(0.5,1.0,"{} Hemisphere {}".format(hemisphere,season_yr0),ha='center',fontdict=title_fontdict)

    # Set X-Labels and X-Tick Labels
    for inx,(param,ax_info) in enumerate(zip(params,ax_list)):
        ax          = ax_info.get('ax')
        ax.set_xlabel('')
        radar_ax    = ax_info.get('radar_ax',False)

        if inx != nrows-1:
            fontdict = ylabel_fontdict.copy()
            fontdict['weight']  = 'normal'
            fontdict['size']    = 18
        else:
            fontdict = ylabel_fontdict.copy()

        my_xticks(sDate,eDate,ax,radar_ax=radar_ax,fontdict=fontdict,
                  labels=False,short_labels=True,plot_axvline=False)

    fig.tight_layout()
# SIDEBAR
    # for param,ax_info in zip(params,ax_list):
    #     # Plot Colorbar ################################################################
    #     ax  = ax_info.get('ax')
    #     if param == 'reject_code':
    #         ax_pos  = ax.get_position()
    #         x0  = 1.005
    #         wdt = 0.015
    #         y0  = ax_pos.extents[1]
    #         hgt = ax_pos.height

    #         axl= fig.add_axes([x0, y0, wdt, hgt])
    #         axl.axis('off')

    #         legend_elements = []
    #         for rej_code, rej_dct in reject_codes.items():
    #             color = rej_dct['color']
    #             label = rej_dct['label']
    #             # legend_elements.append(mpl.lines.Line2D([0], [0], ls='',marker='s', color=color, label=label,markersize=15))
    #             legend_elements.append(mpl.patches.Patch(facecolor=color,edgecolor=color,label=label))

    #         axl.legend(handles=legend_elements, loc='center left', fontsize = 18)
    #     elif ax_info.get('cbar_pcoll') is not None:
    #         ax_pos  = ax.get_position()
    #         x0  = 1.01
    #         wdt = 0.015
    #         y0  = ax_pos.extents[1]
    #         hgt = ax_pos.height
    #         axColor = fig.add_axes([x0, y0, wdt, hgt])
    #         axColor.grid(False)

    #         cbar_pcoll      = ax_info.get('cbar_pcoll')
    #         cbar_label      = ax_info.get('cbar_label')
    #         cbar_ticks      = ax_info.get('cbar_ticks')
    #         cbar_tick_fmt   = prmd.get('cbar_tick_fmt')
    #         cbar_tb_vis     = ax_info.get('cbar_tb_vis',False)

	# 		# fraction : float, default: 0.15
	# 		#     Fraction of original axes to use for colorbar.
	# 		# 
	# 		# shrink : float, default: 1.0
	# 		#     Fraction by which to multiply the size of the colorbar.
	# 		# 
	# 		# aspect : float, default: 20
	# 		#     Ratio of long to short dimensions.
	# 		# 
	# 		# pad : float, default: 0.05 if vertical, 0.15 if horizontal
	# 		#     Fraction of original axes between colorbar and new image axes.
    #         cbar  = fig.colorbar(cbar_pcoll,orientation='vertical',
    #                 cax=axColor,format=cbar_tick_fmt)

    #         cbar_label_fontdict = {'weight': 'bold', 'size': 24}
    #         cbar.set_label(cbar_label,fontdict=cbar_label_fontdict)
    #         if cbar_ticks is not None:
    #             cbar.set_ticks(cbar_ticks)

    #         cbar.ax.set_ylim( *(cbar_pcoll.get_clim()) )

    #         labels = cbar.ax.get_yticklabels()
    #         fontweight  = cbar_ytick_fontdict.get('weight')
    #         fontsize    = 18
    #         for label in labels:
    #             if fontweight:
    #                 label.set_fontweight(fontweight)
    #             if fontsize:
    #                 label.set_fontsize(fontsize)

    fig.savefig(fpath,bbox_inches='tight')

def prep_dir(path,clear=False):
    if clear:
        if os.path.exists(path):
            shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == '__main__':

    output_base_dir     = 'output'
#    mstid_data_dir      = os.path.join('data','mongo_out','mstid_MUSIC','guc')
#    mstid_data_dir      = os.path.join('data','mongo_out','mstid_GSMR_fitexfilter_using_mstid_2016_dates','guc')
#    mstid_data_dir      = os.path.join('data','mongo_out','mstid_2016','guc')
    mstid_data_dir      = os.path.join('data','mongo_out','mstid_GSMR_fitexfilter','guc')
    plot_climatologies  = False
    plot_histograms     = False
    plot_stackplots     = True

    radars          = []
    # 'High Latitude Radars'
    # radars.append('pgr')
    # radars.append('sas')
    # radars.append('kap')
    # radars.append('gbr')
    # 'Mid Latitude Radars'
    # radars.append('cvw')
    # radars.append('cve')
    # radars.append('fhw')
    # radars.append('fhe')
    # radars.append('bks')
    # radars.append('wal')

#    # Ordered by Longitude
#    radars          = []
# Northern Radars
    radars.append('ade')
    radars.append('adw')
    radars.append('bks')
    radars.append('cve')
    radars.append('cvw')
    radars.append('cly')
    radars.append('fhe')
    radars.append('fhw')
    radars.append('gbr')
    radars.append('han')
    radars.append('hok')
    radars.append('hkw')
    radars.append('inv')
    radars.append('jme')
    radars.append('kap')
    radars.append('ksr')
    radars.append('kod')
    radars.append('lyr')
    radars.append('pyk')
    radars.append('pgr')
    radars.append('rkn')
    radars.append('sas')
    radars.append('sch')
    radars.append('sto')
    radars.append('wal')

    # Southern Radars
    # radars.append('san')
    # radars.append('bpk')
    # radars.append('dce')
    # radars.append('dcn')
    # radars.append('fir')
    # radars.append('hal')
    # radars.append('mcm')
    # radars.append('sps')
    # radars.append('san')
    # radars.append('sys')
    # radars.append('sye')
    # radars.append('ker')
    # radars.append('tig')
    # radars.append('unw')
    # radars.append('zho')
    params = []
    params.append('meanSubIntSpect_by_rtiCnt') # This is the MSTID index.
    # layover_datas = ["SAM_INDEX", "SH_UBAR", "SH_DTDY"]
    layover_datas = ["NAM_INDEX","NH_UBAR","NH_DTDY"]
    seasons = list_seasons(yr_0=2010, yr_1=2024)
    # seasons = list_seasons(yr_0=2012, yr_1=2013) + list_seasons(yr_0=2016,yr_1=2024)
    print(seasons)


################################################################################
# LOAD RADAR DATA ##############################################################

    po_dct  = {}
    for param in params:
        # Generate Output Directory
        output_dir  = os.path.join(output_base_dir,param)
        prep_dir(output_dir,clear=True)

        if param == 'meanSubIntSpect_by_rtiCnt':
            calculate_reduced=True
        else:
            calculate_reduced=False

        po = ParameterObject(param,radars=radars,seasons=seasons,
                output_dir=output_dir,default_data_dir=mstid_data_dir,
                calculate_reduced=calculate_reduced)

        po_dct[param]   = po


################################################################################
# STACKPLOTS ###################################################################

    stack_sets  = {}


    ss = stack_sets['mstid_index_reduced'] = []
    # ss.append('reject_code')
    ss.append('meanSubIntSpect_by_rtiCnt')
    # ss.append('meanSubIntSpect_by_rtiCnt_reducedIndex')
    # ss.append('intSpect')
    seasons.append("20000101_20010101")
    # import ipdb;ipdb.set_trace()
    if plot_stackplots:
        for stack_code,stack_params in stack_sets.items():
            stack_dir  = os.path.join(output_base_dir,'stackplots',stack_code)
            prep_dir(stack_dir,clear=True)
            # import ipdb; ipdb.set_trace()
            for season in seasons:
                # if stack_code == 'figure_3':
                #     if season != '20181101_20190501':
                #         continue
                    for layover_data in layover_datas:
                        png_name    = '{!s}_stack_{!s}_{!s}.jpg'.format(season,stack_code,layover_data)
                        png_path    = os.path.join(stack_dir,png_name) 
                        stackplot(po_dct,stack_params,season,fpath=png_path,additional_data=layover_data)
                    else:
                        png_name    = '{!s}_stack_{!s}.jpg'.format(season,stack_code)
                        png_path    = os.path.join(stack_dir,png_name)
                        stackplot(po_dct,stack_params,season,fpath=png_path)
