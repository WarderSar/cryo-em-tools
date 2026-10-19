from pathlib import Path
import logging
import itertools

def sets_crop_calc(box1_range, box2_range, crop_range, ps1, ps2, round_to=4):
    """
    Calculate new pixel sizes after Fourier cropping for two datasets.

    Parameters:
    - box1_range: range of box sizes for dataset 1 (in pixels)
    - box2_range: range of box sizes for dataset 2 (in pixels)
    - crop_range: range of crop box sizes (in pixels)
    - ps1: pixel size for dataset 1 (in Angstroms)
    - ps2: pixel size for dataset 2 (in Angstroms)
    - round_to: number of decimal places to round the new pixel sizes to

    Returns:
    A list of tuples containing (boxsize1, boxsize2, crop_size, new_pixel_size) where new_pixel_size is the common pixel size after cropping.
    """
    results = []
    for bs1, bs2, crop in itertools.product(box1_range, box2_range, crop_range):
        if crop >= bs1 or crop >= bs2 or crop <= 0:
            continue
        ps1_new = round(bs1 / crop * ps1, round_to)
        ps2_new = round(bs2 / crop * ps2, round_to)

        if ps1_new == ps2_new:
            results.append((bs1, bs2, crop, ps1_new))
            logging.info(f"boxsize 1 = {bs1}, boxsize 2 = {bs2}, fourier crop to: {crop}, new pixel size = {ps1_new:.4f}")
    
    return results

def download_vols_df(project, df, target_dir):
    '''
    Download volumes from a CryoSPARC project based on a dataframe containing job names.

    - Requires a dataframe with a column named "Job" containing the job names in string format "J<number>".
    - If optional column "Name" is present, it will be used to rename the downloaded files.
    - If "Name" is not present, the downloaded files will be named based on the job names.
    - The downloaded files will be saved in the specified target directory.
    - Output names will be in the format: {Name}_map.mrc or {Job}_map.mrc if "Name" is not provided.
    '''
    if "Job" not in df.columns:
        raise ValueError("Dataframe must contain a column named 'Job' with job names in string format.")
    if df['Job'].isna().any():
        raise ValueError("Dataframe contains missing values in the 'Job' column.")

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for _, row in df.iterrows():
        job_id = str(row["Job"])
        if "Name" in row and str(row["Name"]).lower() != 'nan':
            custom_name = str(row["Name"])
        else:
            custom_name = job_id

        source_file = f"{job_id}_map.mrc"
        output_file = target_dir / f"{custom_name}_map.mrc"

        try:
            job = project.find_job(job_id)
            job.download_file(source_file, target=output_file)
            logging.info(f"Downloaded {source_file} to {output_file}")
        except Exception as e:
            logging.error(f"Failed to download {source_file} for job {job_id}: {e}")