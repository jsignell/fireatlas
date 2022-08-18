""" DataUpdate
This module include functions used to check and update needed data files
"""

# ------------------------------------------------------------------------------
# Check external dataset
# ------------------------------------------------------------------------------
def check_VNP14IMGML_avail(year, month, ver="C1.05"):
    """ Check if the monthly VIIRS data exist (C1.05 or C1.04)

    Parameters
    ----------
    year : int
        the year
    month : int
        the month
    """

    from FireConsts import dirextdata
    import os
    from glob import glob
    from datetime import date

    # derive monthly file name with path
    t = date(year, month, 1)
    dirFC = os.path.join(dirextdata, "VNP14IMGML") + "/"
    fnmFC = os.path.join(dirFC, "VNP14IMGML." + t.strftime("%Y%m") + "." + ver + ".txt")

    # check if the file exist
    if os.path.exists(fnmFC):
        print("[Yes] Monthly VNP14IMGML exists at ", dirFC)
        fnms = glob(dirFC + "VNP14IMGML." + t.strftime("%Y") + "*.txt")
        mons = max([int(os.path.basename(fnm)[15:17]) for fnm in fnms])
        print(f"The latest VNP14IMGML available month for {year} is {mons}")
    else:
        print("[No] Monthly VNP14IMGML is not available at ", dirFC)
        # if the file does not exist, also find the last available month
        fnms = glob(dirFC + "VNP14IMGML." + t.strftime("%Y") + "*.txt")
        if len(fnms) == 0:
            print("No any monthly VNP14IMGML is not available at ", dirFC)
        else:
            mons = max([int(os.path.basename(fnm)[15:17]) for fnm in fnms])
            print(f"The latest VNP14IMGML available month for {year} is {mons}")


def check_VNP14IMGTDL_avail(year, month, day):
    """ Check if the daily NRT VIIRS data exist

    Parameters
    ----------
    year : int
        the year
    month : int
        the month
    day : int
        the day
    """

    from FireConsts import dirextdata
    import os
    from glob import glob
    from datetime import date, timedelta

    # derive monthly file name with path
    t = date(year, month, day)
    dirFC = os.path.join(dirextdata, "VNP14IMGTDL") + "/"
    fnmFC = os.path.join(
        dirFC, "SUOMI_VIIRS_C2_Global_VNP14IMGTDL_NRT_" + t.strftime("%Y%j") + ".txt"
    )

    # check if the file exist
    if os.path.exists(fnmFC):
        print("[Yes] Daily VNP14IMGTDL exists!")
    else:
        print("[No] Daily VNP14IMGTDL is not available!")

        # if the file does not exist, also find the last available day
        fnms = glob(
            dirFC
            + "SUOMI_VIIRS_C2_Global_VNP14IMGTDL_NRT_"
            + t.strftime("%Y")
            + "*.txt"
        )
        if len(fnms) > 0:
            days = max([int(os.path.basename(fnm)[42:45]) for fnm in fnms])
            tmax = date(t.year, 1, 1) + timedelta(days=days - 1)
            print(
                "The latest VNP14IMGTDL available date is "
                + tmax.strftime("%Y%m%d")
                + "(doy = "
                + tmax.strftime("%j")
                + ")"
            )


def check_GridMET_avail(year, month, day):
    """ Check if the GridMET fm1000 data exist

    Parameters
    ----------
    year : int
        the year
    month : int
        the month
    day : int
        the day
    """

    from FireConsts import dirextdata
    import os
    from datetime import date
    import xarray as xr
    import pandas as pd

    import warnings

    warnings.simplefilter("ignore")

    t = date(year, month, day)
    dirGridMET = os.path.join(dirextdata, "GridMET") + "/"
    fnmFM1000 = dirGridMET + "fm1000_" + t.strftime("%Y") + ".nc"

    if os.path.exists(fnmFM1000):
        print("[Yes] Annual GridMET FM1000 exists!")

        # if the file exist, check whether the date is beyond the time range in the data
        ds = xr.open_dataarray(fnmFM1000)
        tmax = pd.to_datetime(ds["day"][-1].values).date()
        print("The last time in GridMET data is " + tmax.strftime("%Y-%m-%d"))
    else:
        print("[No] Annual GridMET FM1000 is not available!")


def check_data_avail(year, month, day):
    """ A tool used to check the availability of NRT fire and FM1000 data:
    1. monthly suomi VIIRS active fire (VNP14IMGML)
    2. daily suomi VIIRS NRT active fire (VNP14IMGTDL)
    3. annual GridMET FM1000 data

    Parameters
    ----------
    year : int
        the year
    month : int
        the month
    day : int
        the day
    """

    # VIIRS VNP14IMGML data
    check_VNP14IMGML_avail(year, month)

    # VIIRS VNP14IMGTDL data
    check_VNP14IMGTDL_avail(year, month, day)

    # GridMET fm1000 data
    check_GridMET_avail(year, month, day)


# ------------------------------------------------------------------------------
# update external dataset
# ------------------------------------------------------------------------------
def update_VNP14IMGTDL(local_dir=None):

    """ Batch read and extract SNPP NRT VIIRS (VNP14IMGTDL) data
    Usage : update_VNP14IMGTDL(local_dir)

    Parameters
    ----------
    local_dir : str
        the directory containing the downloaded data
    """
    from datetime import date, timedelta
    import pandas as pd
    import ycpy
    from glob import glob

    # The directory to save VNP14IMGTDL data
    if local_dir == None:
        local_dir = "/Users/yangchen/Jacaranda/Data/VIIRS/VNP14IMGTDL/Global/"

    # Derive the date periods needed to download
    today = date.today()
    fnms = glob(
        local_dir + "SUOMI_VIIRS_C2_Global_VNP14IMGTDL_NRT_" + str(today.year) + "*.txt"
    )
    if len(fnms) == 0:
        ndays = 0
    else:
        doys = [int(d[-7:-4]) for d in fnms]
        ndays = max(doys)
    dstart = date(today.year, 1, 1) + timedelta(days=ndays)
    dstart = dstart - timedelta(
        days=1
    )  # downloaded the last file again to avoid incomplete data

    # Do the download process
    urldir = "https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/FIRMS/suomi-npp-viirs-c2/Global/"
    for d in pd.date_range(dstart, today):
        urlfnm = (
            urldir
            + "SUOMI_VIIRS_C2_Global_VNP14IMGTDL_NRT_"
            + d.strftime("%Y%j")
            + ".txt"
        )
        strcmd = ycpy.util.wget(
            url=urlfnm,
            locdir=local_dir,
            robots_off=True,
            no_wget=False,
            timestamping=True,
            header="NASA",
        )


def update_VJ114IMGTDL(local_dir=None):

    """ Batch read and extract NOAA20 VIIRS (VJ114IMGTDL) data
    Usage : update_VJ114IMGTDL(local_dir)

    Parameters
    ----------
    local_dir : str
        the directory containing the downloaded data
    """
    from datetime import date, timedelta
    import pandas as pd
    import ycpy
    from glob import glob

    # The directory to save VNP14IMGTDL data
    if local_dir == None:
        local_dir = "/Users/yangchen/Jacaranda/Data/VIIRS/VJ114IMGTDL/Global/"

    # Derive the date periods needed to download
    today = date.today()
    fnms = glob(
        local_dir
        + "NOAA20_VIIRS_C2_Global_VJ114IMGTDL_NRT_"
        + str(today.year)
        + "*.txt"
    )
    if len(fnms) == 0:
        ndays = 0
    else:
        doys = [int(d[-7:-4]) for d in fnms]
        ndays = max(doys)
    dstart = date(today.year, 1, 1) + timedelta(days=ndays)
    dstart = dstart - timedelta(
        days=1
    )  # downloaded the last file again to avoid incomplete data

    # Do the download process
    urldir = "https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/FIRMS/noaa-20-viirs-c2/Global/"
    for d in pd.date_range(dstart, today):
        urlfnm = (
            urldir
            + "NOAA20_VIIRS_C2_Global_VJ114IMGTDL_NRT_"
            + d.strftime("%Y%j")
            + ".txt"
        )
        strcmd = ycpy.util.wget(
            url=urlfnm,
            locdir=local_dir,
            robots_off=True,
            no_wget=False,
            timestamping=True,
            header="NASA",
        )


def update_GridMET_fm1000(local_dir=None):
    """ Get updated GridMET data (including fm1000)
    """
    import subprocess
    from datetime import date

    # The directory to save GridMET data
    if local_dir == None:
        local_dir = "/Users/yangchen/Jacaranda/Data/GridMET/"

    today = date.today()

    # Do the download process
    urldir = "http://www.northwestknowledge.net/metdata/data/"
    # strvars = ['vpd','pr','tmmn','tmmx','vs','fm100','fm1000','bi','pdsi']
    strvars = ["fm1000"]
    for strvar in strvars:
        urlfnm = urldir + strvar + "_" + str(today.year) + ".nc"
        strget = " ".join(["wget", "-N", "-c", "-nd", urlfnm, "-P", local_dir])
        subprocess.run(strget, shell=True)


if __name__ == "__main__":
    """ Do check or update the data
    """
    # check_data_avail(year,month,day)
    check_VNP14IMGML_avail(2021, 1, ver="C1.05")
