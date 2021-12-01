# Compile Method

## Hint & Preparation(NO NEED FOLLOW)

1.  run "python buildfile.py" in current dir to get the newest built pbrain-xiaocilao.exe GOMOKU files.
2. uncomment some line in mainfile.py to write result in a xlsx file "results.xlsx" (in dist dir) and note that rebuilding can be rather difficult for some computers(including Xu's but not Liu's).
3. uncomment some line in mainfile.py, MCT_Values.py, MCT_Agent.py to enhance randomness.

4. Our codes are based on some packages which are not so popular. So you may use Anaconda or pip install some packs manually.

## Compile steps

- Change the loaction to your mainfile.py (**you don't need to change this, the purpose of this step is to save the MC simulation results in a excel table for training. Since we have done this, please just simply jump to the next step**)

- Open cmd/powershell/terminal under the root folder ("codes")

- ```python
  python .\buildfiles.py 
  ```

- The exe file now is in the dist folder(already cover the former one)

