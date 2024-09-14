from create_profiles import  read_coordinates
from ezdxf.filemanagement import new
from ezdxf.document import Drawing
from typing import List, Tuple

def connect_points_with_lwpolyline(points: List[Tuple[int, float, float, float, str]], doc: Drawing) -> None:
    msp = doc.modelspace()

    # Sort points by their number
    sorted_points = sorted(points, key=lambda x: x[0])

    # Initialize a list to store polyline vertices
    polyline = []

    # Iterate through sorted points
    for i in range(len(sorted_points)):
        nr, x, y, z, desc = sorted_points[i]

        # If it's not the first point and the previous point has the same description and sequential number
        if i > 0 and sorted_points[i - 1][0] == nr - 1 and sorted_points[i - 1][4] == desc:
            # Add the point to the polyline
            polyline.append((x, y))
        else:
            # If the polyline has points, add it to the drawing
            if polyline:
                msp.add_lwpolyline(polyline, dxfattribs={'layer': 'connect_points'})
                polyline = []  # Reset the polyline

            # Start a new polyline with the current point
            polyline.append((x, y))

        # Add point representing height
        msp.add_point(location=(x, y, z), dxfattribs={'layer': 'POINTS'})

        # Add shifted description to point with number and separate text with description
        msp.add_text(f'{nr}', dxfattribs={'insert': (x-0.4, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})
        msp.add_text(desc, dxfattribs={'insert': (x+0.1, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})

    # If there are remaining points in the polyline, add it to the drawing
    if polyline:
        msp.add_lwpolyline(polyline, dxfattribs={'layer': 'connect_points'})

if __name__ == "__main__":
    input_file_path = 'D:/ROBOTA/GEOPARTNER/dom/GRAN TG.txt'
    output_dxf_path = 'D:/ROBOTA/GEOPARTNER/dom/gran_tg.dxf'

    # Read coordinates
    points = read_coordinates(input_file_path)

    # Create a new DXF file
    doc = new()

    # Connect points with polyline
    connect_points_with_lwpolyline(points, doc)

    # Save modified DXF file
    print(f"Saving DXF file to: {output_dxf_path}")  # Debugging statement
    doc.saveas(output_dxf_path)

