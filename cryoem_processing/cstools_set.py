from pathlib import Path
import itertools
import logging
import os

"""
This is a module of code I gathered for 3 years in Cryo-EM as notebooks.

The code was refined and processed as functions.
"""

def sets_crop_calc(box1_range, box2_range, crop_range, ps1, ps2, round_to=4):
    """
    Calculate matching pixel sizes after Fourier cropping two datasets.

    Returns tuples of (boxsize1, boxsize2, crop_size, new_pixel_size).
    """
    results = []
    for bs1, bs2, crop in itertools.product(box1_range, box2_range, crop_range):
        if crop >= bs1 or crop >= bs2 or crop <= 0:
            continue

        ps1_new = round(bs1 / crop * ps1, round_to)
        ps2_new = round(bs2 / crop * ps2, round_to)
        if ps1_new == ps2_new:
            results.append((bs1, bs2, crop, ps1_new))
            logging.info(
                "boxsize 1 = %s, boxsize 2 = %s, fourier crop to: %s, "
                "new pixel size = %.4f",
                bs1,
                bs2,
                crop,
                ps1_new,
            )

    return results


def create_connected_job(
    project,
    workspace,
    job_type,
    inputs=None,
    params=None,
    title=None,
    hostname="localhost",
    queue=True,
):
    """
    Create a CryoSPARC job, connect its inputs, set parameters, and optionally queue it.

    `inputs` maps each target input to a (source_job_uid, source_output) tuple.
    """
    for target_input, source in (inputs or {}).items():
        if not isinstance(source, (tuple, list)) or len(source) != 2:
            raise ValueError(
                f"Input '{target_input}' must map to a "
                "(source_job_uid, source_output) tuple."
            )

    job_options = {"title": title} if title is not None else {}
    job = project.create_job(workspace, job_type, **job_options)

    for target_input, source in (inputs or {}).items():
        source_job_uid, source_output = source
        job.connect(
            target_input=target_input,
            source_job_uid=source_job_uid,
            source_output=source_output,
        )

    for name, value in (params or {}).items():
        job.set_param(name, value)

    if queue:
        job.queue(hostname=hostname)

    logging.info("Created %s job %s", job_type, job.uid)
    return job


def create_class_local_refinements(
    project,
    parent_job_uid,
    workspace,
    n_classes,
    symmetry=None,
    volume_output="volume_consensus",
    particles_output="particles_class_{index}",
    mask_output="mask_focus",
    params=None,
    hostname="localhost",
    queue=True,
):
    """
    Create one Local Refinement job for each class in a parent job.

    Output slot names can be customized to match the parent job's result slots.
    """
    jobs = []
    job_params = dict(params or {})
    if symmetry is not None:
        job_params["refine_symmetry"] = symmetry

    for index in range(n_classes):
        jobs.append(
            create_connected_job(
                project=project,
                workspace=workspace,
                job_type="new_local_refine",
                inputs={
                    "volume": (parent_job_uid, volume_output),
                    "particles": (
                        parent_job_uid,
                        particles_output.format(index=index),
                    ),
                    "mask": (parent_job_uid, mask_output),
                },
                params=job_params,
                title=f"Class {index} local refinement",
                hostname=hostname,
                queue=queue,
            )
        )

    return jobs


def create_class3d_sweep(
    project,
    parent_job_uid,
    mask_job_uid,
    workspace,
    modes,
    epochs,
    class_counts,
    target_res,
    symmetry="C1",
    hostname="localhost",
    queue=True,
):
    """
    Create Class 3D jobs for every combination of mode, epoch, and class count.
    """
    jobs = []
    for mode, epoch, n_classes in itertools.product(modes, epochs, class_counts):
        jobs.append(
            create_connected_job(
                project=project,
                workspace=workspace,
                job_type="class_3D",
                inputs={
                    "particles": (parent_job_uid, "particles"),
                    "mask": (mask_job_uid, "mask"),
                },
                params={
                    "class3D_symmetry": symmetry,
                    "class3D_oem_epochs": epoch,
                    "class3D_N_K": n_classes,
                    "class3D_init_mode": mode,
                    "class3D_target_res": target_res,
                },
                title=(
                    f"mode: {mode} classes: {n_classes} "
                    f"target resolution: {target_res} epochs: {epoch}"
                ),
                hostname=hostname,
                queue=queue,
            )
        )

    return jobs


def create_extract_reconstruct(
    project,
    workspace,
    extraction_batches,
    bin_size_pix,
    symmetry="C1",
    hostname="localhost",
    queue=True,
):
    """
    Create extraction jobs for particle/micrograph pairs and combine their particles
    in one Homogeneous Reconstruction job.

    Each batch is a mapping with `particles_job_uid`, `micrographs_job_uid`, and
    `box_size_pix` keys.
    """
    extraction_batches = list(extraction_batches)
    if not extraction_batches:
        raise ValueError("At least one extraction batch is required.")

    extracts = []
    for batch in extraction_batches:
        extracts.append(
            create_connected_job(
                project=project,
                workspace=workspace,
                job_type="extract_micrographs_multi",
                inputs={
                    "particles": (batch["particles_job_uid"], "particles"),
                    "micrographs": (batch["micrographs_job_uid"], "micrographs"),
                },
                params={
                    "box_size_pix": batch["box_size_pix"],
                    "bin_size_pix": bin_size_pix,
                },
                hostname=hostname,
                queue=queue,
            )
        )

    reconstruction = project.create_job(workspace, "homo_reconstruct")
    for extract in extracts:
        reconstruction.connect(
            target_input="particles",
            source_job_uid=extract.uid,
            source_output="particles",
        )
    reconstruction.set_param("refine_symmetry", symmetry)
    if queue:
        reconstruction.queue(hostname=hostname)
    logging.info(
        "Created Homogeneous Reconstruction job %s from %s extraction jobs",
        reconstruction.uid,
        len(extracts),
    )
    return extracts, reconstruction


def create_volume_flip_job(
    project,
    workspace,
    parent_job_uid,
    source_result,
    flip=True,
    hostname="localhost",
    queue=True,
):
    """
    Create a Volume Tools job from a named volume result and set its flip parameter.

    `source_result` may be, for example, "map_locres" or "map_half_A".
    """
    job = project.create_job(workspace, "volume_tools")
    job.connect_result(
        target_input="volume",
        connection_idx=0,
        slot="map",
        source_job_uid=parent_job_uid,
        source_output="volume",
        source_result=source_result,
    )
    job.set_param("vol_flip", flip)
    if queue:
        job.queue(hostname=hostname)

    logging.info("Created Volume Tools job %s from %s", job.uid, source_result)
    return job


def download_vols_df(project, df, target_dir):
    """
    Download maps for jobs listed in a dataframe with a "Job" column.

    An optional "Name" column is used as the output filename prefix. Returns the
    job IDs whose downloads failed; failures are logged and do not stop other rows.
    """
    if "Job" not in df.columns:
        raise ValueError("Dataframe must contain a column named 'Job'.")
    if df["Job"].isna().any():
        raise ValueError("Dataframe contains missing values in the 'Job' column.")

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    failed_jobs = []

    for _, row in df.iterrows():
        job_id = str(row["Job"])
        name = row["Name"] if "Name" in df.columns else None
        if name is None or str(name).lower() == "nan":
            name = job_id

        source_file = f"{job_id}_map.mrc"
        output_file = target_dir / f"{name}_map.mrc"
        try:
            job = project.find_job(job_id)
            job.download_file(source_file, target=output_file)
            logging.info("Downloaded %s to %s", source_file, output_file)
        except Exception as error:
            logging.error(
                "Failed to download %s for job %s: %s",
                source_file,
                job_id,
                error,
            )
            failed_jobs.append(job_id)

    return failed_jobs


def download_job_files(project, job_uid, file_names, target_dir):
    """
    Download explicitly named files from a CryoSPARC job to a local directory.
    """
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    job = project.find_job(job_uid)
    downloaded_files = []

    for file_name in file_names:
        target = target_dir / Path(file_name).name
        job.download_file(file_name, target=target)
        downloaded_files.append(target)
        logging.info("Downloaded %s to %s", file_name, target)

    return downloaded_files


def download_halfmaps(project, job_uid, target_dir):
    """
    Download every MRC half-map file listed for a CryoSPARC job.
    """
    job = project.find_job(job_uid)
    halfmap_files = [
        name
        for name in job.list_files()
        if "half" in name.lower() and name.lower().endswith(".mrc")
    ]
    if not halfmap_files:
        raise FileNotFoundError(f"No MRC half-map files found for job {job_uid}.")

    return download_job_files(project, job_uid, halfmap_files, target_dir)
