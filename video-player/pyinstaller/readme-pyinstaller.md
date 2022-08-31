
pyinstaller really wants a Conda environment

run this from 'pie-analysis' folder
```
conda create -y -n video-annotate-env python=3.9
conda activate video-annotate-env

pip install --upgrade pip

pip install -e .

pip install pyinstaller
```

Hidden imports are a problem, might need following

```
--hidden-import six
```

Run from the command-line, this will

 - create a default 'VideoAnnotate.spec' file (overwritten each time).
 - create a 'build/' folder
 - create a 'dist/' folder
 
```
pyinstaller \
    --noconfirm \
    --clean \
    --onedir \
    --windowed \
    --path /Users/cudmore/opt/miniconda3/envs/video-annotate-env/lib/python3.9/site-packages/ \
    --name VideoAnnotate \
    ../videoapp/videoApp.py


#     --hidden-import pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 \
```