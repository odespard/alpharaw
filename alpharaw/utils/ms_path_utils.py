import os

_special_ms_exts:list = [
    '.ms_data.hdf', # alphapept
    '.tims.hdf', # alphatims (from alpharaw)
    '.tims.hdf5', # alphatims (from alpharaw)
    '.d.hdf', # alphatims (from alpharaw)
    '.d.hdf5', # alphatims (from alpharaw)
    '.atms.hdf', # alphatims (from alpharaw)
    '.atms.hdf5', # alphatims (from alpharaw)
    '_hcdft.mgf', # p
]

def parse_ms_files_to_dict(
    ms_file_list:list,
    special_ms_exts:list = _special_ms_exts
)->dict:
    """
    Parse spectrum file paths into a dict:
        "/Users/xxx/raw_name1.raw" -> {"raw_name1":"/Users/xxx/raw_name1.raw"}

    Parameters
    ----------
    spectrum_file_list : list
        File path list

    special_ms_exts : list, optional
        Special extension cases for some MS files 
        which contains multiple dot (`.`) after raw_name.
        `_special_ms_exts` by default

    Returns
    -------
    dict
        {"raw_name1" : "/Users/xxx/raw_name1.raw", ...}
    """

    ms_file_dict = {}
    for ms_file in ms_file_list:
        raw_name = os.path.basename(ms_file)
        lower_name = raw_name.lower()
        for _ext in special_ms_exts:
            if lower_name.endswith(_ext.lower()):
                raw_name = raw_name[:-len(_ext)]
                break
        if len(raw_name) == len(lower_name):
            raw_name = os.path.splitext(raw_name)[0]
        ms_file_dict[raw_name] = ms_file
    return ms_file_dict
