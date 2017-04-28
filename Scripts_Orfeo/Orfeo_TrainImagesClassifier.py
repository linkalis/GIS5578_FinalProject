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
    parser = argparse.ArgumentParser(description= "Use Orfeo Toolbox to take a directory containing an image stats file, input .TIF files, and associated .SHP files labeled with target classes; train a model to identify these classes, and output result to a .TXT file")
    parser.add_argument("--indir", required=True, help="The directory that contains the .TIF files and associated .SHP files you want to use for training", dest="indir")
    parser.add_argument("--outdir", required=True, help="The directory where you want to save the .TXT file containing the trained model", dest="outdir")
    return parser


def main(indir, outdir):
    # If user forgot to put trailing slashes at the end of their indir and outdir,
    # add those or we may accidentally try to read from or save to an invalid directory!
    if indir[-1:] != "/":
        indir = indir + "/"

    if outdir[-1:] != "/":
        outdir = outdir + "/"

    # Check if target save directory exists; if not, warn the user and exit
    if os.path.exists(outdir):
        start_time = time.time() # Start the clock

        try:
            # Create an instance of the TrainImagesClassifier application
            TrainImagesClassifier = otbApplication.Registry.CreateApplication("TrainImagesClassifier")

            # Get the list of all files in the input directory that end in .shp
            roi_vector_files = glob.glob(indir + "*.shp")

            # Get the list of all files in the input directory that end in .tif
            training_image_files = glob.glob(indir + "*.tif")

            # Set application parameters
            TrainImagesClassifier.SetParameterStringList("io.vd", roi_vector_files) # Input vector file(s) with regions of interest classified by hand
            TrainImagesClassifier.SetParameterStringList("io.il", training_image_files) # Input rasters
            TrainImagesClassifier.SetParameterString("io.imstat", indir + "/image_stats.xml") # Image statistics file
            #TrainImagesClassifier.SetParameterString("sample.vfn", "Class") # Name of the field in vector file(s) that contains the classification data

            # BOOST CLASSIFIER
            # Note: According to Orfeo docs, real AdaBoost is supposed to work well with categorical data
            TrainImagesClassifier.SetParameterString("classifier.boost.t", "real")
            TrainImagesClassifier.SetParameterString("classifier.ann.f", "sig")
            TrainImagesClassifier.SetParameterString("classifier.ann.term", "all")

            # SVM CLASSIFIER
            #TrainImagesClassifier.SetParameterString("classifier", "libsvm")
            #TrainImagesClassifier.SetParameterString("classifier.libsvm.opt", "false")
            #TrainImagesClassifier.SetParameterString("classifier.libsvm.k", "linear")
            #TrainImagesClassifier.SetParameterString("classifier.libsvm.c", "1")

            #TrainImagesClassifier.SetParameterInt("sample.mv", 100)
            #TrainImagesClassifier.SetParameterInt("sample.mt", 100)
            #TrainImagesClassifier.SetParameterFloat("sample.vtr", 0.5)

            TrainImagesClassifier.SetParameterString("io.confmatout", outdir + "/confusion_matrix.csv") # Save a confusion matrix to .csv
            TrainImagesClassifier.SetParameterString("io.out", outdir + "/model.txt") # Save the model itself to .txt

            # The following line execute the application
            TrainImagesClassifier.ExecuteAndWriteOutput()
            end_time = time.time() # Stop the clock
            elapsed_time = end_time - start_time

            print "Finished training classification model. File saved as 'model.txt' to: " + outdir
            print "Elapsed time: " + str(elapsed_time)
        except Exception as e:
            print "Something went wrong!"
            print e

    else:
        print "Sorry! Couldn't find target save directory. Please check your --outdir argument and try again."
        return


if __name__ == '__main__':
    args = argument_parser().parse_args()

    main(args.indir, args.outdir)
