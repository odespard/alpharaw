conda create -n alpharaw_pip_test python=3.8 -y
conda activate alpharaw_pip_test
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "alpharaw[stable]"
alpharaw
conda deactivate
