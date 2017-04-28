## Step 1: Access NAIP images via AWS

> Modules used: pandas, boto3, os

NAIP data is highly structured in a convenient "quad" tile format.  The key, however, is to learn how to decipher to filenames in order to pinpoint which quads you'll need for a specific project.  Here, we'll walk through a workflow for picking out specific quads and downloading them from AWS.

### Understand NAIP filenames

The filename structure for NAIP images is as follows: **S_DDdddQQ_qq_ZZ_R_YYYYMMDD_yyyymmdd**

* S = Sensor Type
* DDddd = SE Reference point of 1 Degree Block (Latitude = DD, Longitude = ddd)
* QQ = Quad location (range 1 -64)
* qq = Quadrant indicator (NE, NW, SE, SW)
* ZZ = UTM Zone
* R = Resolution in meters
* YYYYMMDD = Acquisition date (year, month, day)
* yyyymmdd = Date NAIP JPG2000 data was created (year, month, day)

For more information on understanding NAIP coverage areas and file naming conventions, see the [USGS's NAIP data dictionary](https://lta.cr.usgs.gov/naip_full_res.html).


### Pick quads using QGIS

To pick quads specifically for the Twin Cities metro region, we'll leverage a manual step in QGIS:

1. Head to the USDA's ["NAIP Quarter Quad and Photocenter Shapefiles"](https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-qq-and-photocenter-shapefiles/index) download site, and download the shapefiles for Minnesota for 2013 and 2015.  These shapefiles act as lookup indexes that you can open up in QGIS and see which NAIP filenames are associated with which regions of interest.

2. In QGIS, open up one of the shapefiles and use the QGIS GUI select interface to manually select which quads you want to target for download.  

3. With the quads selected, right-click the layer name in the layers panel and choose "Save As...".  For the file "Format", choose "Comma Separated Value [CSV]", and make sure to check the option to "Save only selected features". When you're done, you'll have a .CSV file listing the filenames of the NAIP images you're wanting to download.


### Download quads from AWS

Finally, we're ready to grad some NAIP images!  The code for this can be broken into a few relatively simple chunks.  First, you'll need to import the .CSV you just exported from QGIS into Python as a pandas dataframe.  You can use this dataframe as a convenient way to iterate over the metadata for each of the desired images, extract the associated filepaths from the respective columns of the .CSV, and then kick off the downloads for the desired quad images from AWS.  So first, let's load in the dataframe with the following code:

```python
import pandas as pd

selected_quads = pd.read_csv(LOCAL_SAVE_DIR + "/twin_cities_selected_quads_2015.csv")
```

Next, we can define a function that takes the year, latitude, longitude, and filename of an image and kicks off a download from the appropriate folder within the AWS bucket:

```python
import boto3
import os

def download_naip_image(year, lat, lon, filename, save_directory):
    '''
    Given a year indicator, latitude, longitude, and NAIP filename, this function makes a call to the AWS S3 public
    bucket that hosts the NAIP imagery and download the selected image to a specified save directory on the
    user's computer.
    '''
    # AWS doesn't include the version date in the filename, so splice that off before appending to path_to_download
    filename_shortened = filename[0:26] + ".tif"

    # Define the folder to search on AWS
    path_to_download = 'mn/' + str(year) + '/1m/rgbir/' + str(lat) + '0' + str(lon) + '/' + filename_shortened

    # Initialize boto3 S3 client
    s3_client = boto3.client('s3')

    # Define the path where we want to save the file
    # Note: We'll make sure images are stored in separate directories by year
    save_path = save_directory + '/' + str(year) + '/' + filename

    # Check if this file already exists at the save path; if not, download it
    if not os.path.exists(save_path):
        save_path = save_directory + '/' + str(year) + '/' + filename
        print("Downloading image: " + path_to_download)
        s3_client.download_file('aws-naip', path_to_download, save_path, {'RequestPayer':'requester'})
    else:
        print("Looks like you've already downloaded this file.")

    print("Finished downloading image: " + filename_shortened)
```

Finally, we can set up a simple for loop that calls the function we just defined above, using it to download each desired image from AWS.  And because the NAIP files are relatively large, and the downloads can take a while, we can also add some simple print functions after each successful download that can act as a rudimentary progress indicator.  The result is a nice batch process that iterates over each row in the .CSV file, kicks off the download function, and then offers a progress update once each download is complete:

```python
# Get the total number of images we want to download
num_of_images = selected_quads_df.shape[0]

# Kick off the download of the selected images, printing a progress message after each successful download
for index, row in selected_quads_df.iterrows():
    # Note: The .CSV holding information about our selected quads has different column names for 2013 & 2015,
    # so we need to account for that when we're feeding the data into the download_naip_image() function.
    # Uncomment the line below that corresponds to the column names for either the 2013 or 2015 dataset,
    # depending on which year's images you're trying to download.

    # Column names for 2013 dataset:
    #download_naip_image(str(row['naip_3_136'])[0:4], row['quads375_D'], row['quads375_5'], row['naip_3_138'], LOCAL_SAVE_DIR)

    # Column names for 2015 dataset:
    download_naip_image(str(row['SrcImgDate'])[0:4], row['DY'], row['DX'], row['FileName'], LOCAL_SAVE_DIR)

    print("Progress: " + str(index + 1) + " of " + str(num_of_images) + " files downloaded.")
```
