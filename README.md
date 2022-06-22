# DevoGraph
## Introduction
* DevoGraph is a [GSoC 2022 project](https://neurostars.org/t/gsoc-2022-project-idea-gnns-as-developmental-networks/21368) under the administration of [INCF](https://www.incf.org/) and [DevoWorm](https://devoworm.weebly.com/). Our main goal is to provide examples and components that utlize (Temporal/Directed/...) Graph Neural Networks to model the developmental process of *[C. elegans](https://en.wikipedia.org/wiki/Caenorhabditis_elegans)*. 

## Developers
* GSoC 2022 participants: [Jiahang Li](https://github.com/LspongebobJH), [Wataru Kawakami](https://github.com/watarungurunnn)
* Mentors: [Bradly Alicea](https://bradly-alicea.weebly.com/), [Jesse Parent](https://jesparent.github.io/)

## Overall Design
### Stage 1: convert input data into processed data
* The input data should be a video of embryogenesis of *C. elegans*. In the stage, the DevoGraph extracts 3-d positions of nuclei of *C. elegans* along the time series of the video, which will be organized into a csv file. The csv file follows the following format:

|cell| time | x | y | z |
| ---- | ---- | ---- | ---- | ---- |
| AB | 1 | 454.0 | 286.0 | 14.0 |
| ... | ... | ... | ... | ... |

* `cell` is the name of the cell, `time` is the timestamp when the information of the cell was observed, `x, y, z` is 3-d position of the cell that was observed at `time`. Though the csv file may contains other columns, these five columns are necessary.

> The columns in the csv file can be in any order. The same below.

### Stage 2: convert processed data into temporal (directed) graph(s)
* With the csv file specified in stage 1 as the input file, stage 2 converts it into temporal graphs based on [DGL](https://www.dgl.ai/), which is a common-used graph deep learning library. Each graph of the generated temporal graphs corresponds to a certain frame of the input video of stage 1. Given cell lineage tree csv file specified as the following format, DevoGraph provides API to connect mother cells and daughter cells across successive graphs, and thus obtain a temporal and directed graph. Please refer to `/stage_2/stage_2.ipynb` to check details of this stage.

|dauguter| mother |
| ---- | ---- |
| AB | P0 |
| ... | ... |

