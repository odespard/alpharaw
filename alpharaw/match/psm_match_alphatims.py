# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbdev_nbs/match/psm_match_alphatims.ipynb.

# %% auto 0
__all__ = ['PepSpecMatchAlphaTims']

# %% ../../nbdev_nbs/match/psm_match_alphatims.ipynb 1
import pandas as pd
import numpy as np

from alphatims.bruker import TimsTOF

from alpharaw.ms_data_base import (
    MSData_Base, ms_reader_provider
)

from alpharaw.match.match_utils import (
    match_centroid_mz, match_profile_mz
)

from alpharaw.wrappers.alphatims_wrapper import (
    AlphaTimsWrapper
)

from .psm_match import PepSpecMatch

# %% ../../nbdev_nbs/match/psm_match_alphatims.ipynb 2
class PepSpecMatchAlphaTims(PepSpecMatch):
    """
    This can be used for DIA PSM matching by selecting spectrum with RT values
    """
    def get_ms2_peaks(self,
        ms_data:TimsTOF,
        rt_sec:float,
        precursor_mz:float,
        im_value:float=0,
    ):
        im_slice = (
            slice(None) if im_value == 0 else 
            slice(im_value-0.05,im_value+0.05)
        )
        rt_slice = slice(rt_sec-0.5,rt_sec+0.5)

        spec_df = ms_data[
            rt_slice, im_slice
        ]
        spec_df = spec_df[
            (spec_df.quad_low_mz_values <= precursor_mz)
            &(spec_df.quad_high_mz_values >= precursor_mz)
        ].sort_values('mz_values')
        return (
            spec_df.mz_values.values, 
            spec_df.intensity_values.values
        )

    def match_ms2_one_raw(self, 
        psm_df_one_raw: pd.DataFrame,
        ms_file:str,
        ms_file_type:str='hdf',
        use_ppm:bool=True, 
        tol:float=20.0,
        dda:bool=False,
    )->tuple:
        """Matching psm_df_one_raw against ms_file

        Parameters
        ----------
        psm_df_one_raw : pd.DataFrame
            psm dataframe 
            that contains only one raw file

        ms_file : str
            ms2 file path

        ms_file_type : str, optional
            ms2 file type, could be 
            ["thermo","sciex","alphapept","mgf","hdf"].
            Default to 'hdf'

        use_ppm : bool, optional
            if use ppm tolerance. Defaults to True.

        tol : float, optional
            tolerance value. Defaults to 20.0.

        Returns
        -------
        tuple:
            pd.DataFrame: psm dataframe with fragment index information.
            
            pd.DataFrame: fragment mz dataframe.
            
            pd.DataFrame: matched intensity dataframe.
            
            pd.DataFrame: matched mass error dataframe. 
            np.inf if a fragment is not matched.
            
        """
        self._preprocess_psms(psm_df_one_raw)
        psm_df = psm_df_one_raw
        if isinstance(ms_file, MSData_Base):
            ms_reader = ms_file
        else:
            ms_reader = ms_reader_provider.get_reader(
                ms_file_type
            )
            ms_reader.import_raw(ms_file)

        self._add_need_columns_to_psm_df(
            psm_df, ms_reader
        )

        (
            fragment_mz_df, 
            matched_intensity_df,
            matched_mz_err_df,
        ) = self._prepare_matching_dfs(psm_df)

        tims_data = AlphaTimsWrapper(
            ms_reader, dda=dda
        )

        if 'mobility' in psm_df:
            query_columns = [
                'rt_sec', 'precursor_mz', 
                'mobility',
                'frag_start_idx', 
                'frag_end_idx',
            ]
        else:
            query_columns = [
                'rt_sec', 'precursor_mz', 
                'frag_start_idx', 
                'frag_end_idx',
            ]
        
        for items in psm_df[query_columns].values:
            frag_start_idx = int(items[-2])
            frag_end_idx = int(items[-1])
            
            spec_mzs, spec_intens = self.get_ms2_peaks(
                tims_data,
                *items[:-2],
            )

            self._match_one_psm(
                spec_mzs, spec_intens,
                fragment_mz_df, 
                matched_intensity_df,
                matched_mz_err_df,
                frag_start_idx, frag_end_idx,
                use_ppm, tol,
            )
        return (
            psm_df, fragment_mz_df, 
            matched_intensity_df, matched_mz_err_df
        )
