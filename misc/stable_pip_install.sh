conda create -n alpharaw python=3.9 -y
conda activate alpharaw
pip install -e '../.[stable,development-stable]'
python -c "import alpharaw"
conda deactivate
