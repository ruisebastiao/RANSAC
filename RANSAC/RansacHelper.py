import Point as pt
import statistics 
import LineModel as lm
import random
import numpy as np
import math

from sklearn.linear_model import LinearRegression

class RansacHelper(object):
    """Encapsulates RANSAC logic"""
    def __init__ (self):
        pass
        self._complete_list_of_points:list=list()
        self.max_iterations:float=0
        self.min_points_for_model:float=0
        # 'threshold_error' is the threshold distance from a line for a point to be classified as an inlier
        self.threshold_error:float=0
        self.threshold_inlier_count:float=0

    #
    #Should be called once to set the full list of data points
    #
    def add_points(self,points:list):
        self._complete_list_of_points.extend(points)
        pass
    #
    #Get the collection of points
    #
    def get_points(self):
        return self._complete_list_of_points

    #
    #Main algorithm
    #
    def run(self) -> lm.LineModel:
        iter=0
        best_error=9999
        best_model=None
        count_of_better_models=0
        while (iter < self.max_iterations):
            print("-------------------------------------")
            iter+=1
            print("Iteration=%d" % iter)
            random_points=self.select_random_points(self.min_points_for_model)
            print("Found %d random points" % len(random_points))
            temp_model=self.create_model(random_points)
            print("Built model %s using %d random points" % (temp_model,len(random_points)))
            inliers=self.get_inliers_from_model(temp_model,random_points)
            print("Found %d inliers" % (len(inliers)))
            if (len(inliers) < self.threshold_inlier_count):
                print("   Skipping because of poor inlier count (less than %d)" % (self.threshold_inlier_count))
                continue
            print("   Taking mini-model because of good inlier count (gt %d)" % (self.threshold_inlier_count))
            lst_new=list()
            lst_new.extend(random_points)
            lst_new.extend(inliers)
            better_model=self.create_model(lst_new)
            print("Built better model %s using %d random points" % (better_model, len(lst_new)) )
            average_distance=self.compute_average_distance(better_model,lst_new)
            if (average_distance < best_error):
                best_model=temp_model
                best_error=average_distance
                count_of_better_models+=1
                print("    Taking better model. Error=%f    Count of models=%d Polar=%s" % (average_distance,count_of_better_models,best_model.display_polar()))
            else:
                print("    Skipping better model. Error=%f    Count of models=%d" % (average_distance,count_of_better_models))

        return best_model
        pass

    def compute_average_distance(self,model:lm.LineModel,points:list) -> float:
        lst_distances=list()
        for pt in points:
            distance=model.compute_distance(pt)
            lst_distances.append(distance)
        mean=statistics.mean(lst_distances)
        return mean
    #
    #Get all points from master list (not used for model building) within error threshold
    #
    def get_inliers_from_model(self,model:lm.LineModel,points_old_inliers:list) -> list:
        lst_inliers=list()
        for pt in self._complete_list_of_points:
            if ((pt in points_old_inliers) == True):
                continue
            distance_from_model:float=model.compute_distance(pt)
            if (distance_from_model > self.threshold_error):
                continue
            lst_inliers.append(pt)
        return lst_inliers
    #
    #Returns the specified count of random selection of points from the full data set
    #
    def select_random_points(self,count:int):
        #Temporary implementation only
        count_original=len(self._complete_list_of_points)
        if (count >= count_original):
            message="The count of random points:%d canot exceed length of original list:%d" % (count,count_original)
            raise Exception(message)
        lst=random.choices(population=self._complete_list_of_points,k=count)
        return lst
    #
    #Find the best line which fits the specified points
    #
    def create_model(self,points:list):
        #temporary implementation
        model=lm.LineModel(10,20,30)

        #https://www.varsitytutors.com/hotmath/hotmath_help/topics/line-of-best-fit

        mean_x=0
        mean_y=0
        for p in points:
            mean_x+=p.X
            mean_y+=p.Y
        mean_x=mean_x/len(points)
        mean_y=mean_y/len(points)

        slope_numerator=0
        slope_denominator=0
        slope=0
        #use the formula for least squares
        for p in points:
            slope_numerator+=(p.X-mean_x)*(p.Y-mean_y)
            slope_denominator+=(p.X-mean_x)*(p.X-mean_x)

        if (math.fabs(slope_denominator) < 0.001):
            raise Exception("Vertical lines are not yet handled")
        
        slope=slope_numerator/slope_denominator
        y_intercept=mean_y - (slope * mean_x)

        line_a=slope
        line_b=-1
        line_c=y_intercept
        #  standard form of line equation
        #  ------------------------------
        #   y=mx+c
        #   mx  -   y   +   c=0
        #   ax  +   by  +   c=0
        #   slope= -a/b
        #   yint= -c/b
        #        
        model=lm.LineModel(line_a,line_b,line_c)
        return model
