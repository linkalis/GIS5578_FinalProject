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
