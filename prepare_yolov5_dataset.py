import fiftyone as fo


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

def load_dataset_from_local_path(dataset_local_dir: str, dataset_name: str,
                                 force_reload_dataset_if_exists: bool = False):
    if dataset_name in fo.list_datasets() and force_reload_dataset_if_exists:
        exists_dataset = fo.load_dataset(dataset_name)
        print("dataset: {} already exists, will delete it...".format(dataset_name))
        exists_dataset.delete()
        print("     deleted with result: {}".format(exists_dataset.deleted))
    elif dataset_name in fo.list_datasets() and not force_reload_dataset_if_exists:
        return fo.load_dataset(dataset_name)
    dataset_type = fo.types.KITTIDetectionDataset
    dataset = fo.Dataset.from_dir(
        dataset_dir=dataset_local_dir,
        dataset_type=dataset_type,
        name=dataset_name,
    )
    dataset.persistent = True
    return dataset


def export_dataset_to(src_dataset, export_to_local_dir: str):
    # The splits to export
    splits = ["train", "val"]
    ds_len = len(src_dataset)

    # Perform a random 90-10 test-train split
    src_dataset.take(0.1 * len(src_dataset)).tag_samples("val")
    src_dataset.match_tags("val", bool=False).tag_samples("train")

    classes = src_dataset.distinct("ground_truth.detections.label")
    for split in splits:
        train_data_view = src_dataset.match_tags(split)
        train_data_view.export(
            export_dir=export_to_local_dir,
            dataset_type=fo.types.YOLOv5Dataset,
            label_field="ground_truth",
            split=split,
            classes=classes,
        )


if __name__ == '__main__':
    # the kitti dataset should follow this structure, otherwise the loaded dataset will be empty (and no error were shown) !!!
    # <dataset_dir>/
    # data/
    #     <uuid1>.<ext>
    #     <uuid2>.<ext>
    #     ...
    # labels/
    #     <uuid1>.txt
    #     <uuid2>.txt
    #     ...

    # you may see debug error like rm -rf ~/.fiftyone/
    src_dataset_local_path = "prepare_yolov5_dataset_from_kitti_format"
    dataset_name = "first_time1"
    load_dataset = load_dataset_from_local_path(src_dataset_local_path, dataset_name,True)
    print(load_dataset)

    target_export_dataset_local_path = "{}/fiftyone_convert_split_export".format(src_dataset_local_path)
    export_dataset_to(load_dataset, target_export_dataset_local_path)
