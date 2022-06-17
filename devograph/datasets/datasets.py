import dgl
import os
import re
import pandas as pd
import torch as th
import abc
import traceback
import hashlib

from dgl.data import DGLDataset
from dgl.data.utils import download, get_download_dir, makedirs
from dgl.utils import retry_method_with_fix

class CETemporalGraphKNN(DGLDataset):
    '''
    The C. elegans Temporal Graph built on given the csv file using KNN method.
    '''

    def __init__(self, name='CETemporalGraph', url=None, raw_dir='~/.CEData/', save_dir='~/.CEData/', hash_key=(), 
                 force_reload=False, verbose=False, transform=None, 
                 knn_k=4, knn_algorithm='bruteforce-blas', knn_dist='euclidean', 
                 time_start=None, time_end=None):
        self.knn_k = knn_k
        self.knn_algorithm=knn_algorithm
        self.knn_dist=knn_dist
        self.time_start = time_start
        self.time_end = time_end
        self.graphs = []

        super().__init__(name, url, raw_dir, save_dir, hash_key, 
                         force_reload, verbose, transform)
        
        
    def has_cache(self):
        graph_path = os.path.join(self.save_dir,
                                  self.name + '.bin')
        if os.path.exists(graph_path):
            return True

        return False

    def download(self):
        file_name = download(self.url, self.raw_path)
        file_name = re.findall(r"([^\/]*\.csv)", file_name)[0]
        print(f'Finish downloading {file_name}')

    def process(self):
        raw_data:pd.DataFrame = pd.read_csv(self.raw_path)
        time_start = self.time_start if self.time_start is not None else 0
        time_end = self.time_end if self.time_end is not None else raw_data.time.max()

        for time in range(time_start, time_end+1):
            _raw_data = raw_data[raw_data.time == time]
            pos = th.tensor(_raw_data[['x', 'y', 'z']].to_numpy())
            graph = dgl.knn_graph(pos, self.knn_k, self.knn_algorithm, self.knn_dist)
            graph.ndata['pos'] = pos
            graph.ndata['name'] = raw_data.cell
            graph.ndata['size'] = th.tensor(raw_data['size'])
            self.graphs.append(graph)
        
    def save(self):
        dgl.save_graphs(f'{self.save_dir}{self.name}.bin', [self.graphs])

    def load(self):
        self.graphs, _ = dgl.load_graphs(f'{self.save_dir}{self.name}.bin')
    
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
    cet_temp_g_knn = CETemporalGraphKNN(url='https://raw.githubusercontent.com/devoworm/DevoWorm/master/Caenorhabditis%20elegans%20raw%20nuclei%20data/raw-data-part-1a.csv')
    graphs = cet_temp_g_knn.load_graphs()
    print("Done testing")