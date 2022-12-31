# Lossless 3D Streaming
This is a Python code for progressive compression for lossless transmission of triangular meshes. It is based on the paper by Alliez and Desbrun titled "Progressive Compression for Lossless Transmission of Triangle Meshes" which was presented at the 28th annual conference on Computer Graphics and Interactive Techniques in 2001.

## Setup
To use this code, you will need to modify the OBJ_PATH and NB_ITERATIONS variables in the script. OBJ_PATH should be the file path of the OBJ file that you want to transmit, and NB_ITERATIONS is the number of iterations that you want the compression algorithm to run.

Once you have modified these variables, you can run the script by using the command `python main.py`.

## Output
The script will output the compressed version of the OBJ file, which can then be transmitted and decompressed at the receiving end for lossless reconstruction of the original triangular mesh.
