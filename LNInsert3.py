import deepdrr
from deepdrr import Volume
from deepdrr import geo
from deepdrr import utils
from deepdrr.utils import image_utils
import numpy as np
from scipy.spatial.transform import Rotation as R
import random
import matplotlib.pyplot as plt
import os


def main() :

    random.seed()

    #path to segs
    c_dir = 'nnunet_mask/nnU_OUTPUT_Task17_0430compressed'

    NodPath = "nodules"
    segPath = "lung_segs"
    CTPath = "data"

    outPathImages = "drrs2/images"
    outPathMasks = "drrs2/masks"
    outPathImagesN = "drrs2/imagesN"

    #saveDirIm = "downstream/testImage.png"
    #saveDirMsk = "downstream/testMask.png"

    ct_paths = []
    segmentation_paths = []
    nod_paths = []
    imageSave_paths = []
    maskSave_paths = []

    #temporary lung masks for imaging
    lungs = []

    imageNSave_paths = []
    names = []

    #carm = deepdrr.MobileCArm()

    #get ct path, seg path if case in masks dir and data dir
    print("Getting case paths...")
    for filename in os.listdir(segPath) :
        names.append(filename)
        print(filename)
        if filename in os.listdir(CTPath) :
            ct_path = os.path.join(CTPath, filename)
            seg_path = os.path.join(c_dir, filename)
            lung_path = os.path.join(segPath, filename)
            image_path = os.path.join(outPathImages, filename + ".png")
            mask_path = os.path.join(outPathMasks, filename + ".png")
            imageN_path = os.path.join(outPathImagesN, filename + ".png")


            ct_paths.append(ct_path)
            segmentation_paths.append(seg_path)
            imageSave_paths.append(image_path)
            maskSave_paths.append(mask_path)
            imageNSave_paths.append(imageN_path)

            lungs.append(lung_path)


    print("Total cases:", len(ct_paths))

    print("Getting nodule paths...")
    #load nodule paths to randomly sample
    for filename in os.listdir(NodPath) :
        nod_paths.append(os.path.join(NodPath, filename))

    print("Looping through cases...")
    #loop to simulate images 
    for c in range(len(ct_paths)) :
        print("Case:", c + 1)
        #get CT and masks
        print("Loading volumes...")
        ct = getVol(ct_paths[c])
        ct_segmented = getSegVol(ct_paths[c], segmentation_paths[c])

        lung = Volume.from_nifti(lungs[c])
        #print(ct_segmented.materials)

        ##figure out how to get strictly lung mask (seg)
        #print("Getting lung mask...")

        #lung = ct_segmented.materials['lung']

        #lung = np.zeros(ct_segmented.shape)
        #lung[ct_segmented.materials == 'lung'] = 1
        #lung[ct_segmented.materials != 'lung'] = 0

        #lung = Volume(lung)

        ct.faceup()
        ct_segmented.faceup()
        lung.faceup()

        #initialize carm 
        #carm = deepdrr.MobileCArm(isocenter= ct.center_in_world, source_to_isocenter_horizontal_offset = -5, source_to_isocenter_vertical_distance = 1500, alpha=0, beta=10, degrees=True, horizontal_movement=1200, vertical_travel=2000)

        #get randomly 0-6 nodules from nodlib
        numNods = random.randint(1, 3)
       

        #print(nod_paths)
    
        #print(numNods)
        print("Getting", numNods, "nodules and transforming/inserting each")
        nods = random.choices(population = nod_paths, k = numNods)
        #transform each and append to list
        nodules = []
        for path in nods :
            nodule = getVol(path)
            nodule = rotNodule(nodule)
            nodule = scaleNodule(nodule)

            point = insertNodule(lung)

        
        
            
            
            ###use when works

            #point = insertNodule2(ct_segmented, "Liver")
            #point = ct.world_from_ijk @ point
            #print("Transformed:", point)

            nodule = translate_center_to(nodule, point)
            nodules.append(nodule)

        #start up the projectors
        #prepend ct to nods list
        #volargT = nodules.insert(0, ct)
        #volargS = nodules.insert(0, ct_segmented)
        
        print("Initializing projectors and imaging...")

        carm = deepdrr.MobileCArm(isocenter= lung.center_in_world, source_to_isocenter_horizontal_offset = -5, source_to_isocenter_vertical_distance = 1500, alpha=0, beta=10, degrees=True, horizontal_movement=1200, vertical_travel=2000)

        if numNods == 0 :
            threshold_projector = deepdrr.Projector(ct, carm=carm)
            segmentation_projector = deepdrr.Projector(ct_segmented, carm=carm)
            
            #how to define empty proj?
            gt_projector = deepdrr.Projector(ct, carm=carm)
        elif numNods == 1 :
            threshold_projector = deepdrr.Projector([nodules[0], ct], carm=carm)
            segmentation_projector = deepdrr.Projector([nodules[0], ct_segmented], carm=carm)
            gt_projector = deepdrr.Projector(nodules[0], carm=carm)
        elif numNods == 2 :
            threshold_projector = deepdrr.Projector([nodules[0], nodules[1], ct], carm=carm)
            segmentation_projector = deepdrr.Projector([nodules[0], nodules[1], ct_segmented], carm=carm)
            gt_projector = deepdrr.Projector([nodules[0], nodules[1]], carm=carm)
        elif numNods == 3 :
            threshold_projector = deepdrr.Projector([nodules[0],nodules[1], nodules[2], ct], carm=carm)
            segmentation_projector = deepdrr.Projector([nodules[0],nodules[1], nodules[2], ct_segmented], carm=carm)
            gt_projector = deepdrr.Projector([nodules[0], nodules[1], nodules[2]], carm=carm)
        
        #what is **self.seg_projector_config #add ct before nodule when not in collab #should I even include lung seg?
        #here, should create projector for all organ segmentations

        
        #ground truth projector


        threshold_projector.initialize()
        segmentation_projector.initialize()
        gt_projector.initialize()

        image = threshold_projector()
        imageN = segmentation_projector()

        #get ground truth and mask
        nodule_heatmap = gt_projector()
        #nodule_mask = np.where(nodule_heatmap > 0, 1, 0).astype(np.float32)
        print("Saving images...")
        #save
        image_utils.save(imageSave_paths[c], image)
        image_utils.save(imageNSave_paths[c], imageN)
        image_utils.save(maskSave_paths[c], nodule_heatmap)
        print("Images saved!")
        

        #also save to imageNSave_paths and maskN

    print("Simulation complete!!! :)")

#helper functions

def getVol(path) -> Volume :
    vol = Volume.from_nifti(path, segmentation_method = 'thresholding', use_cached= False)
    return vol

def getSegVol(path, cache) -> Volume :
    organ = Volume.from_nifti(path=path, segmentation_method = 'nnunet', use_cached=True, cache_dir= cache)
    return organ

def scaleNodule(x) -> Volume :
    scaleFactor = random.uniform(0.25, 1.1)
    scaleMatrix = np.array([[scaleFactor, 0.0, 0.0, 0.0], [0.0, scaleFactor, 0.0, 0.0], [0.0, 0.0, scaleFactor, 0.0], [0.0, 0.0, 0.0, 1.0]])
    scaling = geo.FrameTransform(scaleMatrix)
    x.world_from_anatomical = scaling @ x.world_from_anatomical
    return x


def rotNodule(x) -> Volume :
    rotation = R.random()
    x = x.rotate(rotation)
    return x

#modified np.all
def contains(org: Volume, x: geo.Point3D) -> bool:
    """Determine whether the point x is inside the volume.
    Args:
        x (geo.Point3D)world': [-1346.4464, -65.99151, 8.187973], 'fractured': False,
                          'cortical_breach': 'TODO'}: world-space point.
    """
    x_ijk = np.array(org.ijk_from_world @ geo.point(x))
    if not np.all(0 <= x_ijk) and np.all(x_ijk < np.array(org.shape)):
        return False
    
    i, j, k = np.round(x_ijk).astype(int)
    return org.data[i, j, k] > 0

def translate_center_to(nod : Volume, x: geo.Point3D) -> None:
        """Translate the volume so that its center is located at world-space point x.
        Only changes the translation elements of the world_from_anatomical transform. Preserves the current rotation of the
        Args:
            x (geo.Point3D): the world-space point.
        """
        x = geo.point(x)
        print(nod.center_in_world)
        nod.translate(x - nod.center_in_world)
        return nod

def insertNodule(vol : Volume) :
    boundingBox = vol.get_bounding_box_in_world()
    
    #print(lung_obj)
    #lung_obj = Volume(lung_obj, {'soft tissue' : lung_obj}, vol.anatomical_from_ijk)
    #boundingBox = lung_obj.get_bounding_box_in_world()
    pointInOrgan = False
    while not pointInOrgan:
        point = geo.point(np.random.uniform(boundingBox[0], boundingBox[1], size=3))
        pointInOrgan = contains(vol, point)
    
    x = point
    #print(x)
    return x

def insertNodule2(vol : Volume, organ : str) :
    org_obj = vol.materials[organ]
    #print(lung_obj)
    #lung_obj = Volume(lung_obj, {'soft tissue' : lung_obj}, vol.anatomical_from_ijk)
    #boundingBox = lung_obj.get_bounding_box_in_world()
    pointInOrgan = False
    i = 0
    while not pointInOrgan:
        #print(i)
        poi_i = np.random.choice(range(org_obj.shape[0]))
        poi_j = np.random.choice(range(org_obj.shape[1]))
        poi_k = np.random.choice(range(org_obj.shape[2]))
        #print(poi_i, poi_j, poi_k)
        if org_obj.data[poi_i, poi_j, poi_k]== 1. :
            pointInOrgan = True
        i+=1

        #too many tries 
        if i > 200000 :
            print("Organ Not Found, inserting somewhere in body")
            break

    #point = vol.world_from_ijk(geo.point([poi_i, poi_j, poi_k]))
    #point = trans @ geo.point([poi_i, poi_j, poi_k])
    point = geo.point([poi_i, poi_j, poi_k])
    print(point)
    return point


    #x = randomly sample point in bounding box, if bounding box is circuscribed about segmentation, check if point is within organ still, if not sample anothe point (while)
    #output volume object
    #when passed to the projector
    
    #x = x.translate_center_to(point), will do outside
    x = point
    #print(x)
    return x

def isLung(vol: Volume, point : geo.Point3D) -> bool:
    lung_obj = vol.materials['lung']
    x_ijk = vol.ijk_from_world @ geo.point(point)
    x_ijk = np.around(x_ijk)
    x_ijk = x_ijk.astype(int)

    if lung_obj.data[x_ijk[0]][x_ijk[1]][x_ijk[2]] == 1 :
        return True
    else :
        return False


def findFile(name, directory) :
    result = False
    for root, dir, files in os.walk(directory) :
        if name in files:
            result = True
    return result


if __name__ == "__main()__" :
    main()
main()
