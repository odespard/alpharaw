conda create -n alpharaw_pip_test python=3.8 -y
conda activate alpharaw_pip_test
pip install "alpharaw[stable]"
python -c "import alpharaw"
conda deactivate
