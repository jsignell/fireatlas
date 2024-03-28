import os
import pytest
import pandas as pd
import pathlib
import geopandas as gpd
from datetime import datetime
from shapely.geometry import Point
from unittest.mock import MagicMock

from fireatlas import preprocess
from fireatlas.FireConsts import remove_static_sources_sourcefile


@pytest.fixture
def mock_rasterio(monkeypatch):
    monkeypatch.setattr(preprocess, "rasterio", MagicMock())
    from fireatlas.preprocess import rasterio

    rasterio.open = MagicMock()
    rasterio.warp = MagicMock()
    rasterio.warp.calculate_default_transform = MagicMock(
        return_value=("transform", 100, 100)
    )
    rasterio.warp.reproject = MagicMock()
    rasterio.warp.Resampling = MagicMock()
    return rasterio


@pytest.fixture
def inputdirs(tmpdir):
    """create the intended input directory structure in tmpdir

    :param tmpdir:
    :return:
    """
    first_level_subdirs = ["NLCD", "static_sources", "VIIRS", "processed"]
    viirs_subdirs = ["VNP14IMGML", "VNP14IMGTDL", "VJ114IMGML", "VJ114IMGTDL"]

    for subdir in first_level_subdirs:
        newdir = tmpdir / subdir
        newdir.mkdir()
        if subdir == "VIIRS":
            for subdir2 in viirs_subdirs:
                newdir = tmpdir / subdir / subdir2
                newdir.mkdir()

    return tmpdir


#### static sources file fixtures


@pytest.fixture
def geojson_file(tmpdir):
    filename = tmpdir.join("geojson.json")
    gdf = gpd.GeoDataFrame(
        {
            "geometry": [Point(0, 0), Point(1, 1)],
        }
    )
    gdf.to_file(filename, driver="GeoJSON")
    return str(filename)


@pytest.fixture
def csv_file(tmpdir):
    data = {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 22],
        "city": ["New York", "San Francisco", "Los Angeles"],
    }

    df = pd.DataFrame(data)
    file_path = tmpdir.join("data.csv")
    df.to_csv(file_path, index=False)
    return str(file_path)


@pytest.fixture
def static_source_file_real(inputdirs):
    """returns the actual path to a static source"""
    data = {
        "id_key_2017": [8855, 5531],
        "Latitude": [31.026022, 9.651642],
        "Longitude": [47.283562, -63.624472],
        "Avg_Temp_K": [1679.59, 1759.32],
        "Detection_frequency_2017": [1, 1],
        "Clear_obs_2017": [196, 144],
        "Type": ["flare", "flare"],
        "ISO_Code": ["IRQ", "VEN"],
        "Country": ["Iraq", "Venuzuela"],
        "BCM_2017": [1.236847361, 0.922870061],
    }

    df = pd.DataFrame(data)
    subdir = inputdirs / "static_sources"
    file_path = subdir.join(f"{remove_static_sources_sourcefile}")
    df.to_csv(file_path, index=False)
    return str(file_path)


@pytest.fixture
def static_source_dir_fake(inputdirs):
    """returns test dir to static sources"""
    data = {
        "id_key_2017": [1, 2],
        "Latitude": [0.5, 0.7],
        "Longitude": [0.5, 0.7],
        "Avg_Temp_K": [1, 2],
        "Detection_frequency_2017": [1, 1],
        "Clear_obs_2017": [1, 2],
        "Type": ["flare", "flare"],
        "ISO_Code": ["T1", "T2"],
        "Country": ["Test1", "Test2"],
        "BCM_2017": [1.0, 2.0],
    }

    df = pd.DataFrame(data)
    subdir = inputdirs / "static_sources"
    file_path = subdir.join(f"{remove_static_sources_sourcefile}")
    df.to_csv(file_path, index=False)
    return str(inputdirs)


#### preprocessed file fixtures


@pytest.fixture
def preprocessed_nrt_snpp_tmpfile(tmpdir):
    """returns file path"""

    data = {
        "Lat": [0.9, 2],
        "Lon": [0.5, 0.7],
        "FRP": [0.5, 0.7],
        "Sat": ["SNPP", "SNPP"],
        "DT": [0.47, 0.44],
        "DS": [0.46, 0.4],
        "datetime": ["2023-08-28 00:03:00", "2023-08-28 00:03:00"],
        "ampm": ["AM", "AM"],
    }

    df = pd.DataFrame(data)
    subdir = tmpdir / "preprocessed" / "NOAA20"
    os.makedirs(str(subdir), exist_ok=True)
    # TODO: mimic the actual filename name used
    file_path = subdir.join(f"{remove_static_sources_sourcefile}")
    df.to_csv(file_path, index=False)
    return str(file_path)


@pytest.fixture
def preprocessed_nrt_noaa20_tmpfile(tmpdir):
    """returns file path"""

    data = {
        "Lat": [1, 2],
        "Lon": [0.5, 0.7],
        "FRP": [0.5, 0.7],
        "Sat": [1, 2],
        "DT": [1, 1],
        "DS": [1, 2],
        "datetime": ["flare", "flare"],
        "ampm": ["T1", "T2"],
    }

    df = pd.DataFrame(data)
    subdir = tmpdir / "preprocessed" / "SNPP"
    os.makedirs(str(subdir), exist_ok=True)
    # TODO: mimic the actual filename name used
    file_path = subdir.join(f"{remove_static_sources_sourcefile}")
    df.to_csv(file_path, index=False)
    return str(inputdirs)


#### real test data and file structure


@pytest.fixture
def test_data_dir(request):
    abs_path = pathlib.Path(os.path.abspath(f"{request.fspath.dirname}/data/"))
    return str(abs_path)


#### VNP14IMGTDL


@pytest.fixture
def nrt_snpp_tmpfile(request):
    """read_VNP14IMGTDL"""
    abs_path = pathlib.Path(os.path.abspath(f"{request.fspath.dirname}/data/"))
    subpath = abs_path / "VIIRS" / "VNP14IMGTDL"
    dt = datetime(2023, 11, 9)
    return str(
        subpath / f"SUOMI_VIIRS_C2_Global_VNP14IMGTDL_NRT_{dt.strftime('%Y%j')}.txt"
    )


#### VJ114IMGTDL


@pytest.fixture
def nrt_noaa20_tmpfile(request):
    """read_VJ114IMGTDL"""
    abs_path = pathlib.Path(os.path.abspath(f"{request.fspath.dirname}/data/"))
    subpath = abs_path / "VIIRS" / "VJ114IMGTDL"
    dt = datetime(2023, 11, 9)
    return str(
        subpath / f"J1_VIIRS_C2_Global_VJ114IMGTDL_NRT_{dt.strftime('%Y%j')}.txt"
    )


#### VNP14IMGML


@pytest.fixture
def monthly_snpp_tmpfile(request):
    """read_VNP14IMGML

    NOTE: never seems to be used
    """
    abs_path = pathlib.Path(os.path.abspath(f"{request.fspath.dirname}/data/"))
    subpath = abs_path / "VIIRS" / "VNP14IMGML"
    dt = datetime(2023, 11, 9)
    return str(subpath / f"VNP14IMGML.{dt.year}{dt.month:02}.C1.05.txt.gz")


#### VJ114IMGML


@pytest.fixture
def monthly_noaa20_tmpfile(request):
    """read_VJ114IMGML

    NOTE: never seems to be used and we don't have any files
    """
    abs_path = pathlib.Path(os.path.abspath(f"{request.fspath.dirname}/data/"))
    subpath = abs_path / "VIIRS" / "VJ114IMGML"
    dt = datetime(2023, 11, 9)
    return str(subpath / f"VJ114IMGML_{dt.year}{dt.month:02}.txt")