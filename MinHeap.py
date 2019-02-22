# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 12:36:15 2019

@author: wsz
"""

class MinHeap():
    def __init__(self):
        self.size = 6
        self.contains = [None]*self.size
        self.num = 0
    
    def _percolate_down(self, i):
        #左孩子索引：2*i+1  右孩子索引：2*i+2
        cur_index = i
        while cur_index*2+1<self.num:
            if 2*cur_index+2<self.num:  #有右孩子
                min_index = 2*cur_index+1
                if self.contains[cur_index*2+1][0] > self.contains[cur_index*2+2][0]:
                    min_index += 1
                if self.contains[cur_index][0] > self.contains[min_index][0]:
                    self.contains[cur_index], self.contains[min_index] = self.contains[min_index],self.contains[cur_index]
                    cur_index = min_index
                else:
                    break
            else:   #无右孩子
                if self.contains[cur_index][0] > self.contains[cur_index*2+1][0]:
                    self.contains[cur_index], self.contains[cur_index*2+1] = self.contains[cur_index*2+1], self.contains[cur_index]
                    cur_index = cur_index*2+1
                else:
                    break
                
    
    def _percolate_up(self, i):
        cur_index = i
        while cur_index > 0:
            father_index = (cur_index-1)//2
            if self.contains[father_index][0] > self.contains[cur_index][0]:
                self.contains[father_index], self.contains[cur_index] = self.contains[cur_index], self.contains[father_index]
                cur_index = father_index
            else:
                break
    
    def full(self):
        if self.size <= self.num:
            return True
        else:
            return False
    
    def empty(self):
        return self.num == 0
    
    def add(self,x):
        if self.full():
            if x[0] > self.contains[0][0]:
                self.contains[0] = x
                self._percolate_down(0)
        else:
            self.contains[self.num] = x
            self._percolate_up(self.num)
            self.num+=1
            
    def pop(self):
        if self.empty():
            return None
        else:
            toReturn = self.contains[0]
            self.num -= 1
            self.contains[0] = self.contains[self.num]
            self._percolate_down(0)
            return toReturn
    
if __name__ == '__main__':
    h = MinHeap()
    h.add((1.3242, 160))
    h.add((31.1, 567))
    h.add((12.1, 567))
    h.add((3.1, 567))
    h.add((3.1, 567))
    h.add((3, 567))
    h.add((31, 567))
    h.add((70.1, 567))
    h.add((-31.1, 567))
    h.add((0, 567))
    h.add((1.1, 567))
    h.add((90,313))