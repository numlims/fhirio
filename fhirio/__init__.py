# automatically generated, DON'T EDIT. please edit init.ct from where this file stems.

import re
from functools import cmp_to_key
import os
import natsort
import json
from dip import dig
from datetime import datetime
import math
import json
OS_SORTED="os_sorted"
PAGE_SORTED="page_sorted"
def page_cmp(a:str, b:str):
    """
     page_cmp sorts fhir file names first by page-number, then by time, like t1_p0, t2_p0, t3_p0, ..., t1_p1, t2_p1, t3_p1...
     
     assumes file name format 2026-06-25_16-41-05-999-Specimen_P131.json.
     
     see https://stackoverflow.com/a/36075587.
    """
    #print("hello page_cmp")
    pagea = int(re.findall('_P(\d+).json', a)[0])
    pageb = int(re.findall('_P(\d+).json', b)[0])
    #print("pagea: " + str(pagea))
    if pagea > pageb:
        return 1
    elif pagea < pageb:
        return -1
    datetimea = re.findall('^([0-9\-_]+)', a)
    datetimeb = re.findall('^([0-9\-_]+)', b)
    if datetimea > datetimeb:
        return 1
    elif datetimea < datetimeb:
        return -1
    else:
        return 0

@staticmethod
def read_entries(dir, encoding="utf-8", sort=OS_SORTED): # todo could be static?
    """
     read_entries returns the fhir entries from all json files in a directory.
     
     sort PAGE_SORTED: it sorts the files page-number first, T1_p0, T2_p0, T3_p0, ..., T1_p1,
     T2_p1..., that's the way the cxx importer reads them.
     
     sort OS_SORTED: sort with the OS natsort.
    """
    entries = []
    files = os.listdir(dir)
    if sort == OS_SORTED:
        #files = natsorted(files)  ## doesn't sort by page numbers first
        files = natsort.os_sorted(files)
    elif sort == PAGE_SORTED:
        files.sort(key=cmp_to_key(page_cmp))
    for file in files:
      _, ext = os.path.splitext(file)
      # print("ext: " + ext)
      if ext != ".json":
        continue
      with open(os.path.join(dir, file), "r", encoding=encoding) as f:    
        jsonin = json.load(f)
        for entry in dig(jsonin, "entry"):
          entry["_filename"] = file
          entries.append(entry)
    return entries
def read_bundles_by_file(dir, encoding="utf-8"):
    """
     read_bundles_by_file returns a dictionary of the whole contents of fhir files keys by filename.
    """
    files = os.listdir(dir)
    bundles = {}
    for filename in files:
        with open(os.path.join(dir, filename), "r") as f:
            jsonin = json.load(f)
            bundles[filename] = jsonin
    return bundles
def bundle(entries, n, restype:str=None, cxx:int=None) -> list:
    """
     bundle puts n entries in a bundle each and returns the list of bundles.
    """
    bundles = []
    batch = []
        
    for i, entry in enumerate(entries):
        # after each n entries
        if i > 0 and i % n == 0:
            # append a bundle of the full batch
            bundles.append(fhir_bundle(batch, restype=restype, cxx=cxx))
            # reset the batch
            batch = []
        # add to the batch
        batch.append(entry)
    bundles.append(fhir_bundle(batch, restype=restype, cxx=cxx))

    return bundles
def write_bundles(bundles:list, dir:str, typ:str=None, wrap:bool=False, outname:str=None):
    """
     write_bundles writes fhir bundles into a directory one bundle per
     file, returning a list of the files written. it wraps the files into a
     timestamped directory if wrap is True. outname overwrites the default
     timestamps and typ names for the written.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if outname is None:
        outname = timestamp
        if typ is not None:
            outname += "_" + typ
    outdir = None
    if wrap:
        outdir = os.path.join(dir, timestamp)
    else:
        outdir = dir
    os.makedirs(outdir, exist_ok=True)    
    page_num_width = str(int(math.log10(len(bundles))) + 1)

    out = []
    for i, bundle in enumerate(bundles):
        fstring = "%s_P%0" + page_num_width + "d.json"
        filename = fstring % (outname, i)
        # filename = timestamp + "_" + type + "_p" + str(i) + ".json"
        path = os.path.join(outdir, filename)
        out.append(path)
        with open(path, 'w', encoding='utf-8') as outf:
            json.dump(bundle, outf, indent=4, ensure_ascii=False)
    return out
def write_bundles_by_file(bundles:dict, outdir:str):
    """
     write_bundles_by_file writes a dict of fhir bundles keyed by
     filename into a given directory, one bundle per file.
    """
    os.makedirs(outdir, exist_ok=True)
    for filename, bundle in bundles.items():
        path = os.path.join(outdir, filename)
        with open(path, "w") as outfile:
            json.dump(bundle, outfile, indent=4, ensure_ascii=False)
def fhir_bundle(entries:list, restype:str=None, cxx:int=3):
    """
     fhir_bundle packs a list of entries into a fhir bundle.
    """
    bundle = {
        "type": "transaction",
        "entry": entries
    }
    if cxx == 3:
        bundle["resourceType"] = "Bundle"
    elif cxx == 4:
        bundle["resourceType"] = restype
    return bundle

