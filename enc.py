import collections
import os
import shutil
import zipfile

import fiona

_id_label = 'id'
_shape_label = 'type'
_feature_label = 'Feature'
_geometry_label = 'geometry'
_properties_label = 'properties'
_coordinates_label = 'coordinates'
_depth_label = ('depth_min', 'DYBDE_MIN')

_path_temporary = 'data', 'temporary'
_path_extracted_charts = 'data', 'charts'
_path_zipped_charts = 'data', 'external', 'zipped_charts'


def read_shapes(category, feature, region, bounding_box):
    return _read_shape_file_data((*_path_extracted_charts, category, feature, region), bounding_box)


def unpack_chart_files(regions, terrains, bounding_box, ocean_depths):
    for region in regions:
        try:
            print('Extracting selected files from {}'.format(region))
            _remove_file_or_folder(*_path_extracted_charts)
            _unzip_chart_files(region)
            _split_ocean_depth_polygons(region, terrains, bounding_box, ocean_depths)
            _generate_feature_shape_files(region, terrains, bounding_box)
            print()
        finally:
            _remove_file_or_folder(*_path_temporary)


def _unzip_chart_files(region):
    print('Unzipping external charts')
    temp = _path_temporary
    _create_folder_path(*temp)
    region_zip = _check_for_valid_region_zip_file(region)
    _extract_zipped_files((*_path_zipped_charts, region_zip), temp)
    for file in _get_files(*temp):
        _extract_zipped_files((*temp, file), (*temp, file.rstrip('.zip')))


def _split_ocean_depth_polygons(region, terrains, bounding_box, ocean_depths):
    print('Splitting ocean depths:')
    category, features, file_names = terrains[0]
    directory = _feature_exists_in_region(file_names[0])
    if directory:
        source_path = *_path_temporary, directory, file_names[0] + '.shp'
        shapes = list(shape for shape in _read_shape_file_data(source_path, bounding_box))
        print(len(shapes))
        for i, depth in enumerate(ocean_depths):
            print('   Extracting depth {}'.format(depth))
            depth_max = ocean_depths[i + 1] if i < len(ocean_depths) - 1 else 10000
            target_path = *_path_extracted_charts, category, 'depth_' + str(depth), region
            depth_interval = list(p for p, d, _ in shapes if depth <= d < depth_max)
            _write_shapes_to_file(target_path, source_path, depth_interval, depth, 'Polygon')
            print('   Depth {} done'.format(depth))


def _generate_feature_shape_files(region, terrains, bounding_box):
    for category, features, file_names in terrains[1:]:
        for feature, file_name in zip(features, file_names):
            print('Generating {} shape files'.format(feature))
            directory = _feature_exists_in_region(file_name)
            if directory:
                source_path = *_path_temporary, directory, file_name + '.shp'
                target_path = *_path_extracted_charts, category, feature, region
                _filter_feature_records(target_path, source_path, bounding_box)


def _remove_file_or_folder(*path_list):
    if os.path.exists(os.path.join(*path_list)):
        shutil.rmtree(os.path.join(*path_list), ignore_errors=True)


def _feature_exists_in_region(file_name):
    for directory in _get_directories(*_path_temporary):
        if file_name + '.shp' in _get_files(*_path_temporary, directory):
            return directory
    return None


def _check_for_valid_region_zip_file(region):
    zip_file = next((s for s in _get_files(*_path_zipped_charts) if region in s.lower()), None)
    name, template = zip_file.split('_'), ['Basisdata', int, 'name', int, 'Dybdedata', 'Shape.zip']
    assert all([name[i] == template[i] for i in [0, -2, -1]] + [name[j].isdigit() for j in [1, -3]])
    return zip_file


def _get_directories(*path_list):
    return next(os.walk(os.path.join(*path_list)))[1]


def _get_files(*path_list):
    return next(os.walk(os.path.join(*path_list)))[2]


def _extract_zipped_files(source_path, target_path):
    with zipfile.ZipFile(os.path.join(*source_path), 'r') as zip_file:
        zip_file.extractall(os.path.join(*target_path))


def _create_folder_path(*path_list):
    os.makedirs(os.path.join(*path_list), exist_ok=True)


def _shape_file_reader(*path_list):
    return fiona.open(os.path.join(*path_list), 'r')


def _read_shape_file_data(source_path, bounding_box):
    with _shape_file_reader(*source_path) as source:
        for i, record in enumerate(source.filter(bbox=bounding_box)):
            yield _record_coordinates(record), _record_depth(record), i


def _filter_feature_records(target_path, source_path, bounding_box):
    with _shape_file_reader(*source_path) as source:
        with _shape_file_writer(target_path, source_path) as target:
            for record in source.filter(bbox=bounding_box):
                target.write(_record_reduced(record))


def _shape_file_writer(target_path, source_path):
    _create_folder_path(*target_path)
    source = _shape_file_reader(*source_path)
    schema, driver, crs = _create_new_schema(source), source.driver, source.crs
    return fiona.open(os.path.join(*target_path), 'w', schema=schema, driver=driver, crs=crs)


def _write_shapes_to_file(target_path, source_path, shapes, depth, shape_name):
    with _shape_file_writer(target_path, source_path) as target:
        for i, coords in enumerate(shapes):
            target.write(_shape_to_record(coords, depth, i, shape_name))


def _create_new_schema(source):
    columns = [(_id_label, 'int:11')]
    if _depth_label[1] in source.schema[_properties_label] or _depth_label[0] in source.schema[_properties_label]:
        columns.append((_depth_label[0], 'float:31.15'))
    return {_properties_label: collections.OrderedDict(columns), _geometry_label: source.schema[_geometry_label]}


def _record_reduced(record):
    columns = [(_id_label, record[_id_label])]
    if _depth_label[1] in record[_properties_label]:
        columns.append((_depth_label[0], record[_properties_label][_depth_label[1]]))
    return {_shape_label: _feature_label, _id_label: record[_id_label],
            _properties_label: collections.OrderedDict(columns),
            _geometry_label: record[_geometry_label]}


def _record_coordinates(record):
    data = record[_geometry_label][_coordinates_label]
    return data if isinstance(data, tuple) else data[0]


def _record_depth(record):
    for i in range(2):
        if _depth_label[i] in record[_properties_label]:
            return record[_properties_label][_depth_label[i]]
    return 0


def _shape_to_record(coords, depth, number, shape_name):
    columns = [(_id_label, number)] if depth is None else [(_id_label, number), (_depth_label[0], depth)]
    return {_shape_label: _feature_label, _id_label: number, _properties_label: collections.OrderedDict(columns),
            _geometry_label: {_shape_label: shape_name, _coordinates_label: [list(coords)]}}
