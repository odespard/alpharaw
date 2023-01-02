import numpy as np

from alphabase.io.hdf import HDF_File

from alpharaw.ms_data_base import (
    MSData_Base, ms_reader_provider
)

def get_peak_lists(starts, ends, peak_df):
    mass_list = [peak_df.mz.values[start:end].tolist() for start,end in zip(starts,ends)]
    inten_list = [peak_df.intensity.values[start:end].tolist() for start,end in zip(starts,ends)]
    return mass_list, inten_list

def extract_ms1(raw_data:MSData_Base, query_data:dict):
    spec_df = raw_data.spectrum_df.query("ms_level==1")
    scans = spec_df.spec_idx.values
    rts = spec_df.rt.values
    ms_levels = spec_df.ms_level.values

    mass_list_ms1, int_list_ms1 = get_peak_lists(
        spec_df.peak_start_idx.values, 
        spec_df.peak_stop_idx.values,
        raw_data.peak_df
    )

    query_data["scan_list_ms1"] = scans
    query_data["rt_list_ms1"] = rts
    query_data["mass_list_ms1"] = np.array(mass_list_ms1, dtype=object)
    query_data["int_list_ms1"] = np.array(int_list_ms1, dtype=object)
    query_data["ms_list_ms1"] = ms_levels

def extract_ms2(raw_data:MSData_Base, query_data:dict):
    spec_df = raw_data.spectrum_df.query("ms_level==2")
    scans = spec_df.spec_idx.values
    rts = spec_df.rt.values
    ms_levels = spec_df.ms_level.values
    precursor_mzs2 = spec_df.precursor_mz.values
    charges = spec_df.charge.values
    charges[charges<=0] = 2


    mass_list_ms2, int_list_ms2 = get_peak_lists(
        spec_df.peak_start_idx.values, 
        spec_df.peak_stop_idx.values,
        raw_data.peak_df
    )

    query_data["scan_list_ms2"] = scans
    query_data["rt_list_ms2"] = rts
    query_data["mass_list_ms2"] = mass_list_ms2
    query_data["int_list_ms2"] = int_list_ms2
    query_data["ms_list_ms2"] = ms_levels
    query_data["prec_mass_list2"] = precursor_mzs2
    query_data["mono_mzs2"] = precursor_mzs2
    query_data["charge2"] = charges

def parse_msdata_to_alphapept(raw_data:MSData_Base):
    query_data = {}
    extract_ms1(raw_data, query_data)
    extract_ms2(raw_data, query_data)

    return query_data, raw_data.creation_time

class AlphaPept_HDF_MS2_Reader(MSData_Base):
    """MS2 from AlphaPept HDF"""
    def _import(self, _path):
        return _path

    def _reset_peaks(self):
        if 'mobility' in self.spectrum_df.columns:
            self.spectrum_df['_mobility'] = -self.spectrum_df.mobility
            self.spectrum_df.sort_values(['rt','_mobility'],inplace=True)
            self.spectrum_df.drop(columns=['_mobility'],inplace=True)
        else:
            self.spectrum_df.sort_values('rt',inplace=True)
        mzs_list = []
        intens_list = []
        idx_list = []
        for start,end in self.spectrum_df[['peak_start_idx','peak_stop_idx']].values:
            mzs_list.append(self.peak_df.mz.values[start:end])
            intens_list.append(self.peak_df.intensity.values[start:end])
            idx_list.append(end-start)
        peak_indices = np.empty(len(idx_list)+1,dtype=np.int64)
        peak_indices[0] = 0
        peak_indices[1:] = np.cumsum(idx_list)
        self.peak_df.mz.values[:] = np.concatenate(mzs_list)
        self.peak_df.intensity.values[:] = np.concatenate(intens_list)
        self.spectrum_df['peak_start_idx'] = peak_indices[:-1]
        self.spectrum_df['peak_stop_idx'] = peak_indices[1:]
    
    def _set_dataframes(self, _path):
        hdf = HDF_File(_path)
        self.peak_df['mz'] = hdf.Raw.MS2_scans.mass_list_ms2.values
        self.peak_df['intensity'] = hdf.Raw.MS2_scans.int_list_ms2.values
        if hasattr(hdf.Raw.MS2_scans, 'mobility2'):
            spec_idxes = np.arange(
                len(hdf.Raw.MS2_scans.rt_list_ms2), 
                dtype=np.int64
            )
        else:
            spec_idxes = hdf.Raw.MS2_scans.scan_list_ms2.values-1

        spec_num = spec_idxes.max()+1
        self.create_spectrum_df(spec_num)

        peak_indices = hdf.Raw.MS2_scans.indices_ms2.values
        start_idxes = np.full(spec_num, -1, dtype=np.int64)
        start_idxes[spec_idxes] = peak_indices[:-1]
        end_idxes = np.full(spec_num, -1, dtype=np.int64)
        end_idxes[spec_idxes] = peak_indices[1:]
        rt_values = np.zeros(spec_num)
        rt_values[spec_idxes] = hdf.Raw.MS2_scans.rt_list_ms2.values

        self.set_peaks_by_cat_array(
            hdf.Raw.MS2_scans.mass_list_ms2.values,
            hdf.Raw.MS2_scans.int_list_ms2.values,
            start_idxes, end_idxes
        )

        self.add_column_in_spec_df(
            'rt', rt_values
        )
        self.spectrum_df['ms_level'] = 2

        if hasattr(hdf.Raw.MS2_scans, 'mobility2'):
            self.add_column_in_spec_df(
                'mobility', hdf.Raw.MS2_scans.mobility2.values
            )

        if hasattr(hdf.Raw.MS2_scans, 'mono_mzs2'):
            precursor_mzs = np.zeros(spec_num)
            precursor_mzs[spec_idxes] = hdf.Raw.MS2_scans.mono_mzs2.values
            self.set_precursor_mz(
                precursor_mzs
            )
            self.set_precursor_mz_windows(
                precursor_mzs-2, precursor_mzs+2
            )
        self._reset_peaks()

ms_reader_provider.register_reader('alphapept', AlphaPept_HDF_MS2_Reader)
ms_reader_provider.register_reader('alphapept_hdf', AlphaPept_HDF_MS2_Reader)
