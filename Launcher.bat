set root=C:\Users\charl\anaconda3
call %root%\Scripts\activate.bat %root%
call conda env create -f environment.yml
call conda activate env_elec
call jupyter notebook notebook_elections.ipynb
pause