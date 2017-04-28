## Step 3: Train and apply a classification model using Orfeo Toolbox

> Modules used: os, glob, time, otbApplication (Orfeo Toolbox's Python bindings module to access Orfeo tools from within Python)

Now that the "human supervised" part of the training process is finished, and regions of interest are labeled, it's time to turn the heavy lifting over to the computer.  This is also where Orfeo Toolbox comes in, offering a robust suite of applications for training a classification model and applying this model to classify other raster images in the dataset.  Out of the box, Orfeo Toolbox already offers some nice command line and very simple GUI tools.  The main difficulty, then, is simply figuring out how to leverage these tools in an efficient way.

I noticed early on, for example, that most of the steps involved in training a classification model and classifying images involve batch processing across multiple raster files.  I found the "otbcli" and "otbgui" applications to be somewhat cumbersome for this kind of batch processing, requiring the user to input long strings of input lists or click through lots of menu options when processing multiple images.  I focused on designing Python scripts, then, that add some flow control and act ask a kind of wrapper around Orfeo tools to allow better batch processing for passing files into the various Orfeo applications and saving the results.  

I tried to design these Python wrapper scripts in a consistent manner so that they can take a user-defined input directory (usually containing raster images), process the entire directory in some way, and then output the result to a user-defined output directory.  I found this to be a lot more straightforward approach to flow control than what the raw OTB tools themselves offer.  I also experienced a number of frustrating moments during testing where I would inadvertently specify an invalid output directory, only to discover at the end of a task that the output path was invalid or unwriteable.  It appears that Orfeo, by default, _doesn't_ check the validity of the output directory/filepath at the outset of a processing task, and is happy to kick off a long and processing-intensive request, only throwing an error message _after_ the task is complete.  To mitigate this, I also added some path checking to make sure that the user doesn't inadvertently try to write to an invalid directory and doesn't inadvertently kick off a duplicate of a processessing-intensive task if a particular file has already been processed.  And finally, because some of the Orfeo tools take a long time to run, I also added in some performance checking using the Python time module to each of these scripts.

I won't discuss the details of each command line tool (which are available in the `Scripts_Orfeo` folder of this write-up), but will give a high-level overview of each step of the process, to explain what each tool is helping accomplish.  And since this portion of the project is the most time- and processing-intensive segment, I will also include estimated execution times for each step, to help the user plan in a snack, a laundry break, or a walk around the block as you're working on training your model and classifying new raster images.


## Step 1: Calculate image statistics to normalize images within each dataset

**Script name:** Orfeo_ComputeImageStatistics.py

**Input:** _--indir_, a directory path pointing to all of the files in the dataset of interest

**Output:** _--outdir_, a directory path pointing to the directory where you want to save the computed statistics file (in .XML format)

**Execution time:** ~ 270s (Ubuntu running in Parallels, 2 processors, 4GB memory)

The first step is to compute some basic image statistics for the files in each dataset.  For this step, you will input _all_ images in the respective datasets--not just the ones which have been used for region of interest labeling in QGIS.  The goal is to compute a global mean and standard deviation across all of the images to use for "centering" the images' pixel band values before training the classification model.  This same image statistics file will also need to be used when applying the classification model to ascribe classes to rasters in the dataset.

It is also important, when working across multiple years of NAIP imagery, to make sure you compute _separate_ image statistics for each year's dataset, and train _separate_ models for each year.  This is because the photos for the different years may be taken during different seasons, and at different times of day (while photos in the same year are generally taken on the same day within a relatively short time span for a region of this size).  This means, for example, that photos taken in 2013 should share the same image statistics and classification model, and photos taken in 2015 should share the same statistics and classification model, and you should avoid mixing photos and models across NAIP capture years.

To call this command line tool to compute image statistics across a dataset, execute the following Python command from the Terminal:

```sh
python Orfeo_ComputeImageStatistics.py --indir <path to NAIP rasters> --outdir <path to save statistics output file>
```

The result will be a file named `image_stats.xml` saved to the designated output directory.  I'm including a file in the `Scripts_Orfeo` folder of this project write-up called `image_stats_example.xml` so you can preview what the output should look like.


## Step 2: Train separate models for each year of the training sets

**Script name:** Orfeo_TrainImagesClassifier.py

**Input:** _--indir_, a directory path pointing to a folder containing three things: 1) the rasters that were used for labeling regions of interest, 2) their associated shapefiles that were created in QGIS and labeled with class values, and 3) the image statistics file generated in the step above

**Output:** _--outdir_, a directory path pointing to the directory where you want to save the classification model file (in .TXT format)

**Execution time:** ~ 120 seconds (MacBook Pro, no Parallels running)

In this step, we finally get to let the computer _learn_!  The Orfeo tool we use in this step takes the rasters and vector files that were used for labeling land uses in QGIS, and has the computer train a model based on these human-labeled inputs.  Because Orfeo Toolbox is a pretty sophisticated library, it does a lot of "magic" behind the scenes.  For example, the modeling process doesn't train using each and every pixel in every labeled feature; instead, it will pick a subset of pixels from within each of the labeled features and analyze their values across all four bands of the image (R, G, B and infrared).  It will then compute vector weights that can be used to classify pixels when applying the model to other images.  And finally, the tool will also perform cross-validation using the remaining pixels within the labeled feature classes to give the user a sense of which classes in the dataset are commonly getting confused with each other.  This results in a "confusion matrix" that can be saved to a .CSV file.  We'll look at this a little more in the conclusion, but this turns out to be a useful metric to understand the quality and limitations of the model.

This step was also the only step I did not get to work successfully as a Python script running in Ubuntu.  I am including my attempt to create a script for reference, but after a number of troubleshooting attempts, I ultimately had to turn to the GUI tool provided by Orfeo to get the models to compute.  To find this tool, you have to open up the folder where you originally installed Orfeo Toolbox on the computer.  Then, look under the `bin/` folder for a tool called `otbgui_TrainImagesClassifier` and click on it to open up a GUI where you can input the training raster files, training vector files, and define an output path for the model and confusion matrix:

![Orfeo Train Images Classifier GUI screenshot with three rasters and three associated ROI vectors loaded in](/img/train_images_classifier.png)

The result will be a file names `model.txt` saved to the designated output directory.  I'm also including a file in the `Scripts_Orfeo` folder of this project write-up called `model_example.txt` so you can preview what the output should look like.


## Step 3: Classify images

**Script name:** Orfeo_ImageClassifier.py

**Input:** _--indir_, a directory path pointing to a folder containing three things: 1) the new NAIP images you want the model to classify (all of which should be from the same year the model was trained for), 2) the image statistics file generated in Step 1 above, and 3) the model file generated in Step 2 above

**Output:** _--outdir_, a directory path pointing to the directory where you want to save the classified raster files

**Execution time:** ~11,700 seconds per image (Ubuntu running in Parallels, 3 processors, 4GB memory)

The final step is to use the model generated in the previous step to have the computer classify other raster images in the dataset to identify the most likely land usages that are present.  The model will then proceed, pixel by pixel, to examine the four bands of the image and assign the likeliest land usage classification based on these values.  Sound like a lot of work?  It sure is--and it takes _a long time_!  

As the classifier is running, you may want to use the Unix `top` tool to keep an eye on your CPU processing speed just to make sure your computer is running at full blast as it's working on this task.  For example, for this demo, I assigned three processors to my Ubuntu installation running in Parallels.  When executing the `top` command from the Terminal, I should see a CPU activity percentage close to 300% (i.e. 100% for each dedicated processor):

![top command in Ubuntu terminal showing 294% CPU activity](/img/top_console_output.png)

What does this mean?  Well, it looks like, behind the scenes, Orfeo Toolbox's C++ library is parceling out the work of classification across all three available processors and is doing its best to make this classification task run as quickly as possible.  It will still take several hours (!) to classify each image, but there is at least a nice amount of efficiency support built into Orfeo Toolbox by default.
