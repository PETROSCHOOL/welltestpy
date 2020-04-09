# -*- coding: utf-8 -*-
"""
welltestpy subpackage providing input-output routines.

.. currentmodule:: welltestpy.data.data_io

The following functions are provided

.. autosummary::
"""
import os
import csv
import shutil
import zipfile
import tempfile
from io import TextIOWrapper as TxtIO, BytesIO as BytIO

import numpy as np

from . import varlib, campaignlib, testslib


# TOOLS ###


def _formstr(string):
    # remove spaces, tabs, linebreaks and other separators
    return "".join(str(string).split())


def _formname(string):
    # remove slashes
    string = "".join(str(string).split(os.path.sep))
    # remove spaces, tabs, linebreaks and other separators
    return _formstr(string)


def _nextr(data):
    return tuple(filter(None, next(data)))


# SAVE ###


def save_var(var, path="", name=None):
    """Save a variable to file.

    This writes the variable to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Var_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".var"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Var_" + var.name
    # ensure the name ends with '.var'
    if name[-4:] != ".var":
        name += ".var"
    name = _formname(name)
    file_path = os.path.join(path, name)
    # write the csv-file
    with open(file_path, "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Variable"])
        writer.writerow(["name", var.name])
        writer.writerow(["symbol", var.symbol])
        writer.writerow(["units", var.units])
        writer.writerow(["description", var.description])
        if np.asanyarray(var.value).dtype == np.int:
            writer.writerow(["integer"])
        else:
            writer.writerow(["float"])
        if var.scalar:
            writer.writerow(["scalar"])
            writer.writerow(["value", var.value])
        else:
            writer.writerow(["shape"] + list(np.shape(var.value)))
            tmpvalue = np.reshape(var.value, -1)
            writer.writerow(["values", len(tmpvalue)])
            for val in tmpvalue:
                writer.writerow([val])
    return file_path


def save_obs(obs, path="", name=None):
    """Save an observation to file.

    This writes the observation to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Obs_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".obs"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Obs_" + obs.name
    # ensure the name ends with '.obs'
    if name[-4:] != ".obs":
        name += ".obs"
    name = _formname(name)
    # create temporal directory for the included files
    patht = tempfile.mkdtemp(dir=path)
    # write the csv-file
    # with open(patht+name[:-4]+".csv", 'w') as csvf:
    with open(os.path.join(patht, "info.csv"), "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Observation"])
        writer.writerow(["name", obs.name])
        writer.writerow(["state", obs.state])
        writer.writerow(["description", obs.description])
        if obs.state == "steady":
            obsname = name[:-4] + "_ObsVar.var"
            writer.writerow(["observation", obsname])
            obs._observation.save(patht, obsname)
        else:
            timname = name[:-4] + "_TimVar.var"
            obsname = name[:-4] + "_ObsVar.var"
            writer.writerow(["time", timname])
            writer.writerow(["observation", obsname])
            obs._time.save(patht, timname)
            obs._observation.save(patht, obsname)
    # compress everything to one zip-file
    file_path = os.path.join(path, name)
    with zipfile.ZipFile(file_path, "w") as zfile:
        # zfile.write(patht+name[:-4]+".csv", name[:-4]+".csv")
        zfile.write(os.path.join(patht, "info.csv"), "info.csv")
        if obs.state == "transient":
            zfile.write(os.path.join(patht, timname), timname)
        zfile.write(os.path.join(patht, obsname), obsname)
    shutil.rmtree(patht, ignore_errors=True)
    return file_path


def save_well(well, path="", name=None):
    """Save a well to file.

    This writes the variable to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Well_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".wel"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Well_" + well.name
    # ensure the name ends with '.csv'
    if name[-4:] != ".wel":
        name += ".wel"
    name = _formname(name)
    # create temporal directory for the included files
    patht = tempfile.mkdtemp(dir=path)
    # write the csv-file
    # with open(patht+name[:-4]+".csv", 'w') as csvf:
    with open(os.path.join(patht, "info.csv"), "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Well"])
        writer.writerow(["name", well.name])
        # define names for the variable-files
        radiuname = name[:-4] + "_RadVar.var"
        coordname = name[:-4] + "_CooVar.var"
        welldname = name[:-4] + "_WedVar.var"
        aquifname = name[:-4] + "_AqdVar.var"
        # save variable-files
        writer.writerow(["radius", radiuname])
        well.wellradius.save(patht, radiuname)
        writer.writerow(["coordinates", coordname])
        well.coordinates.save(patht, coordname)
        writer.writerow(["welldepth", welldname])
        well.welldepth.save(patht, welldname)
        writer.writerow(["aquiferdepth", aquifname])
        well.aquiferdepth.save(patht, aquifname)
    # compress everything to one zip-file
    file_path = os.path.join(path, name)
    with zipfile.ZipFile(file_path, "w") as zfile:
        # zfile.write(patht+name[:-4]+".csv", name[:-4]+".csv")
        zfile.write(os.path.join(patht, "info.csv"), "info.csv")
        zfile.write(os.path.join(patht, radiuname), radiuname)
        zfile.write(os.path.join(patht, coordname), coordname)
        zfile.write(os.path.join(patht, welldname), welldname)
        zfile.write(os.path.join(patht, aquifname), aquifname)
    # delete the temporary directory
    shutil.rmtree(patht, ignore_errors=True)
    return file_path


def save_campaign(campaign, path="", name=None):
    """Save the campaign to file.

    This writes the campaign to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Cmp_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".cmp"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Cmp_" + campaign.name
    # ensure the name ends with '.csv'
    if name[-4:] != ".cmp":
        name += ".cmp"
    name = _formname(name)
    # create temporal directory for the included files
    patht = tempfile.mkdtemp(dir=path)
    # write the csv-file
    # with open(patht+name[:-4]+".csv", 'w') as csvf:
    with open(os.path.join(patht, "info.csv"), "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Campaign"])
        writer.writerow(["name", campaign.name])
        writer.writerow(["description", campaign.description])
        writer.writerow(["timeframe", campaign.timeframe])
        # define names for the variable-files
        if campaign.fieldsite is not None:
            fieldsname = name[:-4] + "_Fieldsite.fds"
            # save variable-files
            writer.writerow(["fieldsite", fieldsname])
            campaign.fieldsite.save(patht, fieldsname)
        else:
            writer.writerow(["fieldsite", "None"])

        wkeys = tuple(campaign.wells.keys())
        writer.writerow(["Wells", len(wkeys)])
        wellsname = {}
        for k in wkeys:
            wellsname[k] = name[:-4] + "_" + k + "_Well.wel"
            writer.writerow([k, wellsname[k]])
            campaign.wells[k].save(patht, wellsname[k])

        tkeys = tuple(campaign.tests.keys())
        writer.writerow(["Tests", len(tkeys)])
        testsname = {}
        for k in tkeys:
            testsname[k] = name[:-4] + "_" + k + "_Test.tst"
            writer.writerow([k, testsname[k]])
            campaign.tests[k].save(patht, testsname[k])

    # compress everything to one zip-file
    file_path = os.path.join(path, name)
    with zipfile.ZipFile(file_path, "w") as zfile:
        zfile.write(os.path.join(patht, "info.csv"), "info.csv")
        if campaign.fieldsite is not None:
            zfile.write(os.path.join(patht, fieldsname), fieldsname)
        for k in wkeys:
            zfile.write(os.path.join(patht, wellsname[k]), wellsname[k])
        for k in tkeys:
            zfile.write(os.path.join(patht, testsname[k]), testsname[k])
    # delete the temporary directory
    shutil.rmtree(patht, ignore_errors=True)
    return file_path


def save_fieldsite(fieldsite, path="", name=None):
    """Save a field site to file.

    This writes the field site to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Field_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".fds"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Field_" + fieldsite.name
    # ensure the name ends with '.csv'
    if name[-4:] != ".fds":
        name += ".fds"
    name = _formname(name)
    # create temporal directory for the included files
    patht = tempfile.mkdtemp(dir=path)
    # write the csv-file
    # with open(patht+name[:-4]+".csv", 'w') as csvf:
    with open(os.path.join(patht, "info.csv"), "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Fieldsite"])
        writer.writerow(["name", fieldsite.name])
        writer.writerow(["description", fieldsite.description])
        # define names for the variable-files
        if fieldsite.coordinates is not None:
            coordname = name[:-4] + "_CooVar.var"
            # save variable-files
            writer.writerow(["coordinates", coordname])
            fieldsite.coordinates.save(patht, coordname)
        else:
            writer.writerow(["coordinates", "None"])
    # compress everything to one zip-file
    file_path = os.path.join(path, name)
    with zipfile.ZipFile(file_path, "w") as zfile:
        zfile.write(os.path.join(patht, "info.csv"), "info.csv")
        if fieldsite.coordinates is not None:
            zfile.write(os.path.join(patht, coordname), coordname)
    # delete the temporary directory
    shutil.rmtree(patht, ignore_errors=True)
    return file_path


def save_pumping_test(pump_test, path="", name=None):
    """Save a pumping test to file.

    This writes the variable to a csv file.

    Parameters
    ----------
    path : :class:`str`, optional
        Path where the variable should be saved. Default: ``""``
    name : :class:`str`, optional
        Name of the file. If ``None``, the name will be generated by
        ``"Test_"+name``. Default: ``None``

    Notes
    -----
    The file will get the suffix ``".tst"``.
    """
    path = os.path.normpath(path)
    # create the path if not existing
    if not os.path.exists(path):
        os.makedirs(path)
    # create a standard name if None is given
    if name is None:
        name = "Test_" + pump_test.name
    # ensure the name ends with '.csv'
    if name[-4:] != ".tst":
        name += ".tst"
    name = _formname(name)
    # create temporal directory for the included files
    patht = tempfile.mkdtemp(dir=path)
    # write the csv-file
    # with open(patht+name[:-4]+".csv", 'w') as csvf:
    with open(os.path.join(patht, "info.csv"), "w") as csvf:
        writer = csv.writer(
            csvf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
        )
        writer.writerow(["Testtype", "PumpingTest"])
        writer.writerow(["name", pump_test.name])
        writer.writerow(["description", pump_test.description])
        writer.writerow(["timeframe", pump_test.timeframe])
        writer.writerow(["pumpingwell", pump_test.pumpingwell])
        # define names for the variable-files (file extension added autom.)
        pumprname = name[:-4] + "_PprVar"
        aquidname = name[:-4] + "_AqdVar"
        aquirname = name[:-4] + "_AqrVar"
        # save variable-files
        pumpr_path = pump_test.pumpingrate.save(patht, pumprname)
        pumpr_base = os.path.basename(pumpr_path)
        writer.writerow(["pumpingrate", pumpr_base])
        aquid_path = pump_test.aquiferdepth.save(patht, aquidname)
        aquid_base = os.path.basename(aquid_path)
        writer.writerow(["aquiferdepth", aquid_base])
        aquir_path = pump_test.aquiferradius.save(patht, aquirname)
        aquir_base = os.path.basename(aquir_path)
        writer.writerow(["aquiferradius", aquir_base])
        okeys = tuple(pump_test.observations.keys())
        writer.writerow(["Observations", len(okeys)])
        obsname = {}
        for k in okeys:
            obsname[k] = name[:-4] + "_" + k + "_Obs.obs"
            writer.writerow([k, obsname[k]])
            pump_test.observations[k].save(patht, obsname[k])
    # compress everything to one zip-file
    file_path = os.path.join(path, name)
    with zipfile.ZipFile(file_path, "w") as zfile:
        zfile.write(os.path.join(patht, "info.csv"), "info.csv")
        zfile.write(pumpr_path, pumpr_base)
        zfile.write(aquir_path, aquir_base)
        zfile.write(aquid_path, aquid_base)
        for k in okeys:
            zfile.write(os.path.join(patht, obsname[k]), obsname[k])
    # delete the temporary directory
    shutil.rmtree(patht, ignore_errors=True)
    return file_path


# LOAD ###


def load_var(varfile):
    """Load a variable from file.

    This reads a variable from a csv file.

    Parameters
    ----------
    varfile : :class:`str`
        Path to the file
    """
    try:
        with open(varfile, "r") as vfile:
            data = csv.reader(vfile)
            if next(data)[0] != "Variable":
                raise Exception
            name = next(data)[1]
            symbol = next(data)[1]
            units = next(data)[1]
            description = next(data)[1]
            integer = next(data)[0] == "integer"
            shapenfo = _nextr(data)
            if shapenfo[0] == "scalar":
                if integer:
                    value = np.int(next(data)[1])
                else:
                    value = np.float(next(data)[1])
            else:
                shape = tuple(np.array(shapenfo[1:], dtype=np.int))
                vcnt = np.int(next(data)[1])
                vlist = []
                for __ in range(vcnt):
                    vlist.append(next(data)[0])
                if integer:
                    value = np.array(vlist, dtype=np.int).reshape(shape)
                else:
                    value = np.array(vlist, dtype=np.float).reshape(shape)

        var = varlib.Variable(name, value, symbol, units, description)
    except Exception:
        try:
            data = csv.reader(varfile)
            if next(data)[0] != "Variable":
                raise Exception
            name = next(data)[1]
            symbol = next(data)[1]
            units = next(data)[1]
            description = next(data)[1]
            integer = next(data)[0] == "integer"
            shapenfo = _nextr(data)
            if shapenfo[0] == "scalar":
                if integer:
                    value = np.int(next(data)[1])
                else:
                    value = np.float(next(data)[1])
            else:
                shape = tuple(np.array(shapenfo[1:], dtype=np.int))
                vcnt = np.int(next(data)[1])
                vlist = []
                for __ in range(vcnt):
                    vlist.append(next(data)[0])
                if integer:
                    value = np.array(vlist, dtype=np.int).reshape(shape)
                else:
                    value = np.array(vlist, dtype=np.float).reshape(shape)

            var = varlib.Variable(name, value, symbol, units, description)
        except Exception:
            raise Exception("loadVar: loading the variable was not possible")
    return var


def load_obs(obsfile):
    """Load an observation from file.

    This reads a observation from a csv file.

    Parameters
    ----------
    obsfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(obsfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            if next(data)[0] != "Observation":
                raise Exception
            name = next(data)[1]
            steady = next(data)[1] == "steady"
            description = next(data)[1]
            if not steady:
                timef = next(data)[1]
            obsf = next(data)[1]

            if not steady:
                time = load_var(TxtIO(zfile.open(timef)))
            else:
                time = None

            obs = load_var(TxtIO(zfile.open(obsf)))

        observation = varlib.Observation(name, obs, time, description)
    except Exception:
        raise Exception("loadObs: loading the observation was not possible")
    return observation


def load_well(welfile):
    """Load a well from file.

    This reads a well from a csv file.

    Parameters
    ----------
    welfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(welfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            if next(data)[0] != "Well":
                raise Exception
            name = next(data)[1]
            radf = next(data)[1]
            coordf = next(data)[1]
            welldf = next(data)[1]
            aquidf = next(data)[1]

            rad = load_var(TxtIO(zfile.open(radf)))
            coord = load_var(TxtIO(zfile.open(coordf)))
            welld = load_var(TxtIO(zfile.open(welldf)))
            aquid = load_var(TxtIO(zfile.open(aquidf)))

        well = varlib.Well(name, rad, coord, welld, aquid)
    except Exception:
        raise Exception("loadWell: loading the well was not possible")
    return well


def load_campaign(cmpfile):
    """Load a campaign from file.

    This reads a campaign from a csv file.

    Parameters
    ----------
    cmpfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(cmpfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            if next(data)[0] != "Campaign":
                raise Exception
            name = next(data)[1]
            description = next(data)[1]
            timeframe = next(data)[1]
            row = _nextr(data)
            if row[1] == "None":
                fieldsite = None
            else:
                fieldsite = load_fieldsite(BytIO(zfile.read(row[1])))
            wcnt = np.int(next(data)[1])
            wells = {}
            for __ in range(wcnt):
                row = _nextr(data)
                wells[row[0]] = load_well(BytIO(zfile.read(row[1])))

            tcnt = np.int(next(data)[1])
            tests = {}
            for __ in range(tcnt):
                row = _nextr(data)
                tests[row[0]] = load_test(BytIO(zfile.read(row[1])))

        campaign = campaignlib.Campaign(
            name, fieldsite, wells, tests, timeframe, description
        )
    except Exception:
        raise Exception(
            "loadPumpingTest: loading the pumpingtest " + "was not possible"
        )
    return campaign


def load_fieldsite(fdsfile):
    """Load a field site from file.

    This reads a field site from a csv file.

    Parameters
    ----------
    fdsfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(fdsfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            if next(data)[0] != "Fieldsite":
                raise Exception
            name = next(data)[1]
            description = next(data)[1]
            coordinfo = next(data)[1]
            if coordinfo == "None":
                coordinates = None
            else:
                coordinates = load_var(TxtIO(zfile.open(coordinfo)))
        fieldsite = campaignlib.FieldSite(name, description, coordinates)
    except Exception:
        raise Exception(
            "loadFieldSite: loading the fieldsite " + "was not possible"
        )
    return fieldsite


def load_test(tstfile):
    """Load a test from file.

    This reads a test from a csv file.

    Parameters
    ----------
    tstfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(tstfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            row = _nextr(data)
            if row[0] != "Testtype":
                raise Exception
            if row[1] == "PumpingTest":
                routine = _load_pumping_test
            else:
                raise Exception
    except Exception:
        raise Exception("loadTest: loading the test " + "was not possible")

    return routine(tstfile)


def _load_pumping_test(tstfile):
    """Load a pumping test from file.

    This reads a pumping test from a csv file.

    Parameters
    ----------
    tstfile : :class:`str`
        Path to the file
    """
    try:
        with zipfile.ZipFile(tstfile, "r") as zfile:
            info = TxtIO(zfile.open("info.csv"))
            data = csv.reader(info)
            if next(data)[1] != "PumpingTest":
                raise Exception
            name = next(data)[1]
            description = next(data)[1]
            timeframe = next(data)[1]
            pumpingwell = next(data)[1]
            rate_raw = TxtIO(zfile.open(next(data)[1]))
            try:
                pumpingrate = load_var(rate_raw)
            except Exception:
                pumpingrate = load_obs(rate_raw)
            aquiferdepth = load_var(TxtIO(zfile.open(next(data)[1])))
            aquiferradius = load_var(TxtIO(zfile.open(next(data)[1])))
            obscnt = np.int(next(data)[1])
            observations = {}
            for __ in range(obscnt):
                row = _nextr(data)
                observations[row[0]] = load_obs(BytIO(zfile.read(row[1])))

        pumpingtest = testslib.PumpingTest(
            name,
            pumpingwell,
            pumpingrate,
            observations,
            aquiferdepth,
            aquiferradius,
            description,
            timeframe,
        )
    except Exception:
        raise Exception(
            "loadPumpingTest: loading the pumpingtest " + "was not possible"
        )
    return pumpingtest
