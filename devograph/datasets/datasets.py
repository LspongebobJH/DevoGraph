import dgl
import os
import re
import pandas as pd
import torch as th
import abc
import traceback
import hashlib

from dgl.data import DGLDataset
from dgl.data.utils import download, save_info, save_graphs, load_graphs, load_info
from dgl.utils import retry_method_with_fix

class CETemporalGraphKNN(DGLDataset):
    '''
    The C. elegans Temporal Graph built on given the csv file using KNN method.
    '''
    home_dir = os.environ['HOME']+'/'
    def __init__(self, name='CETemporalGraph', url=None, raw_dir=f'{home_dir}.CEData/', save_dir=f'{home_dir}.CEData/', 
                 hash_key=(), force_reload=False, verbose=False, transform=None, 
                 knn_k=4, knn_algorithm='bruteforce-blas', knn_dist='euclidean', 
                 time_start=None, time_end=None):
        self.knn_k = knn_k
        self.knn_algorithm=knn_algorithm
        self.knn_dist=knn_dist
        self.time_start = time_start
        self.time_end = time_end
        self.graphs = []
        self.info = {'cell':[]}

        super().__init__(name, url, raw_dir, save_dir, hash_key, 
                         force_reload, verbose, transform)
        
        
    def has_cache(self):
        graph_path = os.path.join(self.save_dir,
                                  self.name + '.bin')
        if os.path.exists(graph_path):
            return True

        return False

    def download(self):
        if os.path.exists(self.raw_path):
            return
        file_name = download(self.url, self.raw_path)
        file_name = re.findall(r"([^\/]*\.csv)", file_name)[0]
        print(f'Finish downloading {file_name}')

    def process(self):
        raw_data:pd.DataFrame = pd.read_csv(self.raw_path, usecols=['cell', 'time', 'x', 'y', 'z', 'size'])
        time_start = self.time_start if self.time_start is not None else raw_data.time.min()
        time_end = self.time_end if self.time_end is not None else raw_data.time.max()
        self.info['time_start'] = time_start
        self.info['time_end'] = time_end

        for time in range(time_start, time_end+1):
            _raw_data = raw_data[raw_data.time == time]
            if len(_raw_data) == 0:
                continue
            # TODO: need to average positions of the same node (type)?
            # Why are there multiple cells with the same name?
            pos = th.tensor(_raw_data[['x', 'y', 'z']].to_numpy())
            graph = dgl.knn_graph(pos, self.knn_k, self.knn_algorithm, self.knn_dist)
            graph.ndata['pos'] = pos
            graph.ndata['size'] = th.tensor(_raw_data['size'].to_numpy())
            self.info['cell'].append(_raw_data['cell'].to_list())
            self.graphs.append(graph)
        
    def save(self):
        save_info(f'{self.save_dir}{self.name}_info.pkl', self.info)
        save_graphs(f'{self.save_dir}{self.name}.bin', self.graphs)

    def load(self):
        self.graphs, _ = load_graphs(f'{self.save_dir}{self.name}.bin')
        self.info = load_info(f'{self.save_dir}{self.name}_info.pkl')
    
    def __getitem__(self, idx):
        return self.graphs[idx]

    def __len__(self):
        return len(self.graphs)
        
    @property
    def raw_path(self):
        return f'{self.raw_dir}CE_raw_data.csv'

    @property
    def raw_name(self):
        return 'CE_raw_data.csv'

# class CEDirectedGraph:
    
if __name__ == '__main__':
    datasets = CETemporalGraphKNN(
        time_start=0, time_end=5,
        url='https://raw.githubusercontent.com/LspongebobJH/DevoGraph/main/data/CE_raw_data.csv?token=GHSAT0AAAAAABMX6RJRRFC2U5QOCZXHNBVYYVL5Y2A')
    print("Done testing")