from ezdxf.filemanagement import new
from ezdxf.document import Drawing
from typing import List, Tuple


def read_coordinates(file_path: str) -> List[Tuple[int, float, float, float, str]]:
    measurements = []
    with open(file_path) as stream:
        content = stream.read()
        cleaned_lines = ["\t".join(line.split()) for line in content.split('\n')]
        measurements.extend(cleaned_lines)
    return [(int(''.join(filter(str.isdigit, line.split('\t')[0]))), 
             float(line.split('\t')[2]), 
             float(line.split('\t')[1]),
             float(line.split('\t')[3]), 
             str(line.split('\t')[4])) for line in measurements if len(line) > 3]


# def read_coordinates(file_path: str) -> List[Tuple[int, float, float, float, str]]:
#     measurements = []
#     with open(file_path, 'r') as stream:
#         content = stream.readlines()
#         for line in content:
#             cleaned_line = line.strip().split()
#             if len(cleaned_line) >= 5:
#                 try:
#                     nr = int(cleaned_line[0])
#                     y = float(cleaned_line[1])
#                     x = float(cleaned_line[2])
#                     z = float(cleaned_line[3])
#                     desc = cleaned_line[4]
#                     measurements.append((nr, x, y, z, desc))
#                 except ValueError:
#                     print(f"Niepoprawny format linii: {line}")
#     return measurements


def create_points(points: List[Tuple[int, float, float, float, str]], doc: Drawing) -> None:
    msp = doc.modelspace()
    sorted_points = sorted(points, key=lambda x: x[0])
    for i in range(len(sorted_points)):
        nr, x, y, z, desc = sorted_points[i]
        msp.add_point(location=(x, y, z), dxfattribs={'layer': 'POINTS'})
        msp.add_text(f'{nr}', dxfattribs={'insert': (x-0.4, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})
        msp.add_text(desc, dxfattribs={'insert': (x+0.1, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})


if __name__ == "__main__":
    input_file_path = 'D:/ROBOTA/GEOPARTNER/dom/GRAN TG.txt'
    output_dxf_path = 'D:/ROBOTA/GEOPARTNER/dom/gran_tg2.dxf'

    # Read coordinates
    points = read_coordinates(input_file_path)

    # Create a new DXF file
    doc = new()

    # Connect points with polyline
    create_points(points, doc)

    # Save modified DXF file
    print(f"Saving DXF file to: {output_dxf_path}")  # Debugging statement
    doc.saveas(output_dxf_path)

