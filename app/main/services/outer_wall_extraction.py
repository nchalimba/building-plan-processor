import shapely.geometry as geom
from app.main.constants import DISTANCE_TO_NEIGHBOURS
from app.main.models.adjacent_polygon import Adjacent_Polygon
from app.main.models.polygon import Polygon
from app.main.models.wall import Wall
from app.main.services.extraction_helper import ExtractionHelper
from app.main.services.orientation_extraction import OrientationExtraction
from loguru import logger
from numpy import poly

'''
Description: This class contains logic to identify outer walls. 
The functionality to identify outer walls is mostly integrated from prototype b.
'''
main_logger = logger.bind()

class OuterWallExtraction:
    def get_outer_walls(self, polygons: list[Polygon], polygon: Polygon, yaxis: float, outline_polygon: Polygon, calculate_orientation: bool) -> Polygon:
        '''
        Description: This method coordinates the calculation of outer walls and orientation.
        Params: polygons: list[Polygon], polygon: Polygon, yaxis: float, outline_polygon: Polygon, calculate_orientation: bool
        Return: polygon: Polygon
        '''
        walls = polygon.walls
        walls, list_of_neighbours = self.check_walls_for_outer_walls(
            walls, outline_polygon, polygons, polygon, calculate_orientation, yaxis)

        polygon.walls = walls
        polygon.outer_wall_percentage = self.calculate_outer_wall_percentage(
            polygon)
        polygon.walls , sky_directions= self.get_sky_direction(polygon.walls, outline_polygon, polygons, polygon, calculate_orientation, yaxis)
        return polygon


    def check_walls_for_outer_walls(self, walls: list, outline_polygon: Polygon, file_polygons: list, wall_polygon: Polygon, calculate_orientation: bool, yaxis):
        '''
        Description: This method checks if a wall out of a given list walls is an outer wall. Therefore, the method "is_outer_wall_get_neighbour" is called and
        the response_code 4 is needed to identify a wall as such. The "return" of the method is a print-line which includes the number of
        outer walls found by reading out the outer_wall_counter.
        Params: walls: list, outline_polygon: Polygon, file_polygons: list, wall_polygon: Polygon, calculate_orientation: bool, yaxis
        Return: walls, list_of_neighbors
        '''

        list_of_neighbors = []
        outer_wall_counter = 0
        counter = 0
        for wall in walls:
            counter = counter + 1
            check_left = self.is_outer_wall_get_neighbour(
                "left", outline_polygon, file_polygons, wall, wall_polygon)

            check_right = self.is_outer_wall_get_neighbour(
                "right", outline_polygon, file_polygons, wall, wall_polygon)

            if check_left[0] == 4 or check_right[0] == 4:
                outer_wall_counter = outer_wall_counter + 1
                wall.is_outer_wall = True

                if calculate_orientation:
                    try:
                        if check_left[0] == 4:
                            wall.orientation = OrientationExtraction.calculate_orientation(
                                "left", yaxis, wall)
                        elif check_right[0] == 4:
                            wall.orientation = OrientationExtraction.calculate_orientation(
                                "right", yaxis, wall)
                    except ValueError:
                        main_logger.warning('Value errror')
                        pass
            else:
                wall.is_outer_wall = False

                if len(check_left) > 1 >= len(check_right):
                    list_of_neighbors.append(Adjacent_Polygon(
                        adjacent_polygon_id=check_left[1].id))

                elif len(check_right) > 1 >= len(check_left):
                    list_of_neighbors.append(Adjacent_Polygon(
                        adjacent_polygon_id=check_right[1].id))

                elif check_left[0] == 5 or check_right[0] == 5:
                    continue

                else:
                    wall.is_pillar = True

        return walls, list_of_neighbors

    def is_outer_wall_get_neighbour(self, direction: str, outline_polygon: Polygon, file_polygons: list[Polygon], wall: Wall, wall_polygon: Polygon) -> list:
        """
        Description: Method to check if a given wall is an outer wall by drawing a perpendicular line and checking if this line
        intersects the outer red line. Additionally it is checked if another polygon is intersected (this is the case
        for pillars or elevators).Direction left or right (direction of the perpendicular line) needs to be handed over.
        Params: direction:String, outline_polygon: Polygon, file_polygons: list[Polygon], wall: Wall, wall_polygon: Polygon
        
        Return: return_list:List [return code: int, neighbor:Polygon]
        Returns a list with a return code on Position 0 followed by the neighbor on position 1 if there is one
        Possible return codes: 1: perpendicular line ends in own polygon, 2: perpendicular line intersects own polygon,
        3: wall has a neighbor, 4: This is an outer wall in this direction,
        5: no neighbor, no outer wall in this direction

        """
        return_list = []
        # create a shapely linestring for intersects check
        outline_linestring = ExtractionHelper.transform_polygon_to_line_string(
            outline_polygon)
        # Step 1: get the wall as shapely LineString and calculate the middle
        this_wall_line = ExtractionHelper.transform_wall_to_line_string(wall)
        this_wall_line_middle = geom.Point((wall.start_point.x_coordinate + wall.end_point.x_coordinate) / 2,
                                           (wall.start_point.y_coordinate + wall.end_point.y_coordinate) / 2)

        # Step 2: draw a parallel line in the specified direction of the wall_line and calculate middle,
        # first value controls how long perpendicular_line will be
        # increase value to increase length of perpendicular line
        # 2.5(m) offset and perpendicular line for improved detection of outer walls
        parallel_line = this_wall_line.parallel_offset(2.5, direction)
        try:
            parallel_line_middle = geom.Point(
                (parallel_line.coords[0][0] + parallel_line.coords[1][0]) / 2,
                (parallel_line.coords[0][1] + parallel_line.coords[1][1]) / 2)
            # this exception occurs, if the walls are not long enough to divide by 2. although the amount of those wall
            # is reduced as far as possible, this exception might occur in pillars due to the arc approximation
        except IndexError:
            return_list.append(1)
            return return_list

        # if the endpoint of the perpendicular line (middle of parallel line) is within own polygon, we can leave method
        if parallel_line_middle.within(ExtractionHelper.transform_polygon_to_shapely_polygon(wall_polygon)):
            # print("Perpendicular line goes into its own polygon. No action in this direction")
            return_list.append(1)
            return return_list

        # Step 3: create perpendicular line by connecting middle points, this line will be used for next checks
        perpendicular_line = geom.LineString(
            [this_wall_line_middle, parallel_line_middle])

        if perpendicular_line.intersects(outline_linestring):
            return_list.append(4)
            return return_list
        else:
            return_list.append(5)
            return return_list

    def calculate_outer_wall_percentage(self, polygon: Polygon) -> float:
        '''
        Description: This method calculates the percentage of outer walls in a polygon
        Params: polygon: Polygon
        Return: outer_wall_percentage: float
        '''
        outer_wall_length = 0
        for wall in polygon.walls:
            if wall.is_outer_wall:
                outer_wall_length = outer_wall_length + ExtractionHelper.transform_wall_to_line_string(wall).length
        if outer_wall_length != 0 and polygon.perimeter != 0:
            outer_wall_percentage = (
                outer_wall_length / polygon.perimeter) * 100
            return outer_wall_percentage
        return None


    def get_sky_direction(self, walls: list, outline_polygon: Polygon, file_polygons: list, wall_polygon: Polygon, calculate_orientation: bool, yaxis) -> tuple[list, list]:
        '''
        Description: This method determines the sky direction of outer walls. It utilizes the is_outer_wall_get_neighbour() method on one hand for 
        checking if a wall is an outer wall and on the other hand for determination of the wall direction. The direction of an outer wall
        is then used for calculating the orientation angle with calculate_orientation(). This angle is used to determine the sky direction
        with the sky_direction() method. The method returns a list of walls and sky directions.
        Params: walls: list, outline_polygon: Polygon, file_polygons: list, wall_polygon: Polygon, calculate_orientation: bool, yaxis
        Return: walls: list, sky_directions_list
        '''

        sky_directions = []

        for wall in walls:

            wall_left = self.is_outer_wall_get_neighbour(
                "left", outline_polygon, file_polygons, wall, wall_polygon)

            wall_right = self.is_outer_wall_get_neighbour(
                "right", outline_polygon, file_polygons, wall, wall_polygon)

            # return code 4 for outer wall
            if wall_left[0] == 4:
                # left oriented outer wall
                angle_left = True

                # angle calculation
                if angle_left and calculate_orientation:
                    angle = OrientationExtraction.calculate_orientation(
                        "left", yaxis, wall)

                    # determination of sky direction
                    sky_direction = OrientationExtraction.sky_direction(angle)

                    wall.sky_direction = sky_direction
                    sky_directions.append(sky_direction)

            # return code 4 for outer wall
            elif wall_right[0] == 4:
                # right oriented outer wall
                angle_right = True

                # angle calculation
                if angle_right and calculate_orientation:
                    angle = OrientationExtraction.calculate_orientation(
                        "right", yaxis, wall)

                    # determination of sky direction
                    sky_direction = OrientationExtraction.sky_direction(angle)
                    
                    wall.sky_direction = sky_direction
                    sky_directions.append(sky_direction)
 
        return walls, sky_directions

