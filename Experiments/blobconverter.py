import blobconverter

blob_path = blobconverter.from_openvino(
    xml="/home/andy/Documents/intel/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.xml",
    bin="/home/andy/Documents/intel/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.bin",
    data_type="FP16",
    shaves=6,
)