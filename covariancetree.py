import numpy as np
from .thing import TriangleThing
from ciscode import Frame, closest


class CovTreeNode:

	minCount = 25 #the minimum number of triangles each tree MUST have in self.things

	def __init__(self, ts, atl):
		self.things = ts #array of triangles where each triangle holds 3 vectors
		self.num_things = len(ts)
		self.atlas = atl
		self.points = None
		self.F= None
		self.U = None
		self.left = None
		self.right = None
		self.haveSubTrees = False
		self.cc = None
		self.pos_cent = None
		self.neg_cent = None
		self.median = 0
		self.compute_cov_frame(self.things) #get our transformation
		self.construct_subtrees() #make left and right subtrees or finish 

	
	def compute_cov_frame(self,ts):
		self.points = self.extract_points(ts)

		#compute centroid
		summed = []
		for triangle in self.things:
			summed.append((triangle.corners[0] + triangle.corners[2] + triangle.corners[1])/3.0)
		cent = np.mean(np.array(summed),axis=0) 

		self.U = self.points - cent
	
		#use svd to compute rotation
		A = np.cov(self.U.transpose())
		lamda, Q = np.linalg.eig(A) 
		index = lamda.tolist().index(max(lamda))
		new_Q = Q

		#need to ennsure that we have either a rotation or reflection matrix
		if index==0:
			new_Q = Q
			
		if index==1:
			new_Q = np.array([Q[:,1], Q[:,0], Q[:,2]])	
			
		if index==2:
			new_Q = np.array([Q[:,2], Q[:,1], Q[:,0]])

		self.F = Frame(new_Q, cent)

	
	def extract_points(self, ts):
		extracted = []
		for triangle in ts:
			vertices = triangle.corners
			p = vertices[0]
			r = vertices[2]
			q = vertices[1]
			extracted.append(p)
			extracted.append(r)
			extracted.append(q)
		extracted = np.array(extracted)
		extracted = np.unique(extracted, axis=0)
		return extracted
		

	def construct_subtrees(self):
		if self.num_things < self.minCount:
			self.haveSubTrees = False 
			return

		centers = []
		left_list = []
		right_list = []
		pos_centers = []
		neg_centers = []
		new_points = []
		for i in range(len(self.things)):
			centers.append(np.dot(np.linalg.inv(self.F.r),((self.things[i].corners[0] + self.things[i].corners[2] + self.things[i].corners[1])/3.0) - self.F.p)) #maybe change to np.add
		for i in range(len(self.points)):
			new_points.append(np.dot(np.linalg.inv(self.F.r),((self.points[i]) - self.F.p)))
		self.median = 0
		
		for i in range(len(centers)):
			#get our triangle vertices in terms of the current node's coordinate system
			transformed_p = np.dot(np.linalg.inv(self.F.r),(self.things[i].corners[0] - self.F.p))
			transformed_q = np.dot(np.linalg.inv(self.F.r),(self.things[i].corners[1] - self.F.p))
			transformed_r = np.dot(np.linalg.inv(self.F.r),(self.things[i].corners[2] - self.F.p))

			#rotation matrix
			if np.linalg.det(self.F.r) > 0:
				if transformed_p[0] <= self.median or transformed_q[0] <= self.median or transformed_r[0] <= self.median:
					left_list.append(self.things[i]) 
					neg_centers.append(centers[i])
				if transformed_p[0] > self.median or transformed_q[0] > self.median or transformed_r[0] > self.median:
					right_list.append(self.things[i]) 
					pos_centers.append(centers[i])
			#reflection matrix
			else:
				if transformed_p[0] > self.median  or transformed_q[0] > self.median or transformed_r[0] > self.median: 
					left_list.append(self.things[i]) 
					neg_centers.append(centers[i])
				if transformed_p[0] <= self.median or transformed_q[0] <= self.median or transformed_r[0] <= self.median:
					right_list.append(self.things[i]) 
					pos_centers.append(centers[i])


		self.haveSubTrees = True 
		self.pos_cent = pos_centers
		self.neg_cent = neg_centers

		self.left = CovTreeNode(left_list,len(left_list)) 
		self.right = CovTreeNode(right_list, len(right_list)) 


	def findClosestPoint(self, a, c, dist): 
		"""Finds closest point in mesh to given coordinates."""
		b = self.F.inv().__matmul__(a)		
		if self.haveSubTrees:
			
			if np.linalg.det(self.F.r) > 0:
				if b[0] > 0:
					return self.right.findClosestPoint(a,c,dist)
				elif b[0] <= 0:
					return self.left.findClosestPoint(a,c,dist)
			#if matrix is a refelection matrix
			else:

				if b[0] <= 0:
					return self.right.findClosestPoint(a,c,dist)
				elif b[0] > 0:
					return self.left.findClosestPoint(a,c,dist)
		else:
			for i in range(len(self.things)):
				cp = self.searchTri(self.things[i], a)
				dst = closest.distance(cp,a)
				if dst < dist:
					dist = dst
					c = cp
			return c, self.things[i] 

	def searchTri(self, triangle: TriangleThing, a: np.ndarray) :

		vertices = triangle.corners
		p = vertices[0]
		q = vertices[1]
		r = vertices[2]
		A = np.array([q - p, r - p]).T
		B = (a - p).T
			
		x, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
		x = x.T
			
		c = p + x[0] * (q - p) + x[1] * (r - p)

        # Check bound
		if x[0] < 0:
			c = self.triangle_bound(c, r, p)
		elif x[1] < 0:
			c = self.triangle_bound(c, p, q)
		elif (x[0] + x[1]) > 1:
			c = self.triangle_bound(c, q, r)

		return c

	def triangle_bound(self, c: np.ndarray, p: np.ndarray, q: np.ndarray):
		"""Computes point projected on triangle edge."""
		l = np.dot((c - p), (q - p)) / np.dot((q - p), (q - p))
		l_s = max(0, min(l, 1))
		return (np.cross((p + l_s), (q - p)))


	


