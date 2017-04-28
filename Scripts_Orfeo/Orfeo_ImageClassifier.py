import os
import glob
import time

# Set the OTB_APPLICATION_PATH environment variable to point to where our OTB applications
# are installed so Python can invoke them
os.environ["OTB_APPLICATION_PATH"] = "/home/linkalis/OrfeoToolbox/OTB-5.10.0-Linux64/lib/otb/applications"

# Import Orfeo Toolbox via Python bindings
import otbApplication


def argument_parser():
    '''
    Parse arguments and return
    '''
    import argparse
    parser = argparse.ArgumentParser(description= "Use Orfeo Toolbox to classify raster .TIF files based on a trained model; output classified raster .TIF file to specified directory")
    parser.add_argument("--indir", required=True, help="The directory that contains the .TIF files you want to compute statistics on", dest="indir")
    parser.add_argument("--outdir", required=True, help="The directory where you want to save the .XML file containing the computed statistics", dest="outdir")
    return parser


def classifyRaster(input_raster, indir, outdir, start_time):
    '''
    A helper function to perform classification for a single raster image
    '''
    # Extract just the filename of the image, minus the OS filepath and .tif
    # indicators so we can concatenate this later
    filename_to_save = os.path.basename(input_raster)[:-4] + "_classified.tif"

    # Check if raster has already been classified; if it has, we don't want to
    # waste time reclassifying, so print an error message and move on
    if os.path.exists(outdir + filename_to_save):
        print "Looks like this raster has already been classified. Found existing file at: " + outdir + filename_to_save
    elif os.path.exists(outdir):
        print "Classifying raster: " + outdir + filename_to_save

        # If raster hasn't yet been classified, and output directory is valid,
        # create an ImageClassifier OTB application and pass parameters
        ImageClassifier = otbApplication.Registry.CreateApplication("ImageClassifier")

        # Set application parameters
        ImageClassifier.SetParameterString("in", input_raster) # Raster file to classify

        # Add some checking to make sure these files exist in indir?
        ImageClassifier.SetParameterString("imstat", indir + "image_stats.xml") # Image statistics file
        ImageClassifier.SetParameterString("model", indir + "model.txt") # Model file trained in step above

        ImageClassifier.SetParameterString("out", outdir + filename_to_save) # Save classified image as a new raster

        # Execute the application
        ImageClassifier.ExecuteAndWriteOutput()

        end_time = time.time() # Stop the clock
        elapsed_time = end_time - start_time

        print "Finished classifying raster: " + outdir + filename_to_save
        print "Elapsed time: " + str(elapsed_time)
    else:
        print "Sorry! Couldn't find target save directory. Please check your --outdir argument and try again."



def main(indir, outdir):
    # If user forgot to put trailing slashes at the end of their indir and outdir,
    # add those or we may accidentally try to read from or save to an invalid directory!
    if indir[-1:] != "/":
        indir = indir + "/"

    if outdir[-1:] != "/":
        outdir = outdir + "/"

    # Get the list of all files in the input directory that end in .tif - these are the
    # rasters we want to classify
    rasters_to_classify = glob.glob(indir + "*.tif")

    for raster in rasters_to_classify:
        classifyRaster(raster, indir, outdir, time.time())



if __name__ == '__main__':
    args = argument_parser().parse_args()

    main(args.indir, args.outdir)
