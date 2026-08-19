from app.lidar.pdal_processing import classification_limits

def test_default_roof_classes_include_unclassified_and_building():
    assert classification_limits() == "Classification[1:1],Classification[6:6]"
