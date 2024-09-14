import math
import matplotlib.pyplot as plt
from typing import List, Tuple
from ezdxf.filemanagement import readfile, new
from ezdxf.document import Drawing


def calculate_azimuth(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    azimuth = math.degrees(math.atan2(dy, dx))    
    return azimuth if azimuth >= 0 else azimuth + 360.0

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


def create_dxf_file(points: List[Tuple[int, float, float, float, str]], output_dxf_path: str, skipped_pairs: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    doc = new()
    msp = doc.modelspace()

    current_polyline_points = []  # Lista przechowująca pary (nr, x, y), między którymi jest rysowana polilinia

    for i in range(len(points) - 2):
        nr1, x1, y1, z1, desc1 = points[i]
        nr2, x2, y2, z2, desc2 = points[i + 1]
        nr3, x3, y3, z3, desc3 = points[i + 2]

        # Oblicz odległość między punktami (x1, y1) i (x2, y2)
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        azimuth1 = calculate_azimuth(x1, y1, x2, y2)
        azimuth2 = calculate_azimuth(x2, y2, x3, y3)

        # Sprawdź czy różnica azymutów między dwiema kolejnymi parami punktów nie przekracza 60 stopni
        if abs(azimuth2 - azimuth1) <= 60:
            # Sprawdź czy odległość między punktami nie przekracza 10
            if distance <= 10:
                current_polyline_points.extend([(x1, y1), (x2, y2), (x3, y3)])
        else:
            # Sprawdź, czy punkty (nr2, x2, y2) i (nr3, x3, y3) nie są już w current_polyline_points
            if (x1, y1) not in current_polyline_points or (x2, y2) not in current_polyline_points:
                # Dodaj parę punktów (x2, y2) i (x3, y3) do listy skipped_pairs
                skipped_pairs.append((nr1, nr2))

            if current_polyline_points:
                msp.add_lwpolyline([(x, y) for x, y in current_polyline_points], dxfattribs={'layer': 'Poprzeczka'})
            current_polyline_points = []

    for nr, x, y, z, desc in points:
        # Add point representing height
        msp.add_point(location=(x, y, z), dxfattribs={'layer': 'POINTS'})

        # Add shifted description to point with number and separate text with description
        msp.add_text(f'{nr}', dxfattribs={'insert': (x-0.4, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})
        msp.add_text(desc, dxfattribs={'insert': (x+0.1, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})

    # Save DXF file
    doc.saveas(output_dxf_path)

    return skipped_pairs


def add_profil(doc: Drawing, plot_points: List[Tuple[int, float, float]], offset_x: float, offset_y: float, points: List[Tuple[int, float, float, float, str]], skipped_pairs: List[Tuple[int,int]]) -> None:
    msp = doc.modelspace()

    # Add profile vertices and lines
    for i in range(len(plot_points) - 1):
        point1 = plot_points[i]
        point2 = plot_points[i + 1]
        x1, y1 = point1[1], point1[2]
        x2, y2 = point2[1], point2[2]

        # Calculate distance between points
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Check if distance is greater than 10
        if distance > 10:
            continue
        # Add offset to point coordinates
        x1 += offset_x
        y1 += offset_y
        x2 += offset_x
        y2 += offset_y
        point_offset1 =  x1, y1
        point_offset2 =  x2, y2
        
        # Extract point numbers for checking if the pair is in skipped_pairs
        nr1, nr2 = points[i][0], points[i+1][0]

        # Check if the pair of point numbers is in skipped_pairs and not in plot_points
        if (nr1, nr2) in skipped_pairs and (nr1, nr2) not in [(coord[0], coord[1]) for coord in plot_points]:
            continue
        # Dodaj linię tylko wtedy, gdy para numerów punktów nie znajduje się w skipped_pairs
        msp.add_lwpolyline([point_offset1, point_offset2], dxfattribs={'layer': 'Profil_wysokosciowy'})
        
    # Add profile vertices points
    for nr, cumulative_distance, elevation in plot_points:
        cumulative_distance = offset_x + cumulative_distance
        elevation = offset_y + elevation

        # Add point only if it is not in skipped_pairs and in plot_points
        msp.add_point(location=(cumulative_distance, elevation), dxfattribs={'layer': 'Profile_POiNT'})


    # Add numbering and description to each point
    for i in range(len(points)):
        nr, _, _, _, desc = points[i]
        x, y = plot_points[i][1], plot_points[i][2]  # Use plot_points to determine text insertion point
        x += offset_x
        y += offset_y
        msp.add_text(f'{nr}', dxfattribs={'insert': (x-0.4, y+0.1, 0), 'style': 'Standard', 'height': 0.1})
        msp.add_text(desc, dxfattribs={'insert': (x+0.1, y+0.1, 0), 'style': 'Standard', 'height': 0.1})


def plot_elevation_profile(points: List[Tuple[int, float, float, float, str]], skipped_pairs: List[Tuple[int,int]]) -> List[Tuple[int, float, float]]:
    # Ustal wysokość punktu pierwszego jako referencyjną dla każdej pary punktów w skipped_pairs
    reference_elevation = points[0][3]
    
    # Inicjalizuj listę punktów referencyjnych, dodając punkt pierwszy na początku
    reference_points = [points[0][0]]
    reference_points.extend([pair[1] for pair in skipped_pairs])
    # Oblicz różnice wysokości względem punktu referencyjnego
    elevations = [point[3] - reference_elevation for point in points]

    # Inicjalizuj listę odległości
    distance_points = []

    # Iteruj przez punkty, dodając 25 do distance_points dla każdej pary punktów z skipped_points
    for i in range(1, len(points)):
        if (points[i - 1][0], points[i][0]) in skipped_pairs:
            distance_points.append(25)
        else:
            distance = math.sqrt((points[i][1] - points[i-1][1])**2 + (points[i][2] - points[i-1][2])**2)
            distance_points.append(distance)

    # Zsumuj odległości, aby uzyskać całkowite odległości
    cumulative_distances = [0] + [sum(distance_points[:i]) for i in range(1, len(distance_points) + 1)]

    # Zwróć punkty zawierające odległości, różnice wysokości i numery punktów
    return list(zip([point[0] for point in points], cumulative_distances, elevations))


if __name__ == "__main__":

    input_file_path = 'D:/ROBOTA/python/autocad/programy/test1.txt'
    output_dxf_path = 'D:/ROBOTA/python/autocad/programy/test4.dxf'

    # Read coordinates
    points = read_coordinates(input_file_path)
    # Calculate offset based on the highest point on the left
    # Find point with the highest y coordinate and the smallest x coordinate
    highest_point = min(points, key=lambda p: p[1])
    leftmost_point = max(points, key=lambda p: p[2])  # Fix: Changed from p[0] to p[2] to get the leftmost point

    # Calculate offset based on the point with the highest y coordinate and the smallest x coordinate
    offset_x, offset_y = leftmost_point[1] + 100, highest_point[2] + 50

    # Create DXF file with descriptions and get skipped_pairs
    skipped_pairs = create_dxf_file(points, output_dxf_path, skipped_pairs=[])

    # Generate plot and get points
    plot_points = plot_elevation_profile(points, skipped_pairs)


    # Read DXF file
    doc = readfile(output_dxf_path)

    # Add elevation profiles to DXF file
    add_profil(doc, plot_points, offset_x, offset_y, points, skipped_pairs)


    # Save modified DXF file
    doc.saveas(output_dxf_path)

