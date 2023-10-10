import networkx as nx
import matplotlib.pyplot as plt


def draw_conflict_figure():
    # 创建有向图对象
    G = nx.DiGraph()

    # 添加节点
    nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    G.add_nodes_from(nodes)

    # 添加边
    double_edges = [(1, 2), (1, 8), (1, 6), (1, 10), (2, 3), (2, 6), (2, 7), (2, 8), (2, 1), (3, 2), (3, 4), (3, 5),
                    (3, 8), (4, 3), (4, 5), (4, 6), (4, 7), (4, 9), (4, 10), (5, 4), (5, 3), (5, 8), (5, 10), (6, 4),
                    (6, 2), (6, 1), (6, 10), (7, 2), (7, 4), (7, 8), (7, 9), (8, 1), (8, 2), (8, 3), (8, 7), (8, 9),
                    (8, 5), (9, 4), (9, 7), (9, 8), (9, 10), (10, 1), (10, 5), (10, 6), (10, 4), (10, 9)]
    single_edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 8), (0, 10), (5, 9), (3, 7)]
    G.add_edges_from(double_edges)
    G.add_edges_from(single_edges)

    # 指定每个节点的颜色
    node_colors = ['#7f7f7f', '#789440', '#9c4a09', '#c4d6a0', '#92cddc', '#bf9000', '#7f6000', '#c4d6a0',
                   '#31859b', '#bf9000', '#ea700d']

    # 判断边的方向，并设置不同的颜色值
    edge_colors = []
    for edge in G.edges():
        if (edge[1], edge[0]) in G.edges():
            edge_colors.append('blue')  # 双向边为蓝色
        else:
            edge_colors.append('red')  # 单向边为红色

    plt.figure()
    # 绘制有向图
    nx.draw(G, with_labels=True, arrows=True, node_color=node_colors, edge_color=edge_colors, node_size=800)
    # plt.show()
    plt.savefig(f'./../figures/冲突有向图.eps')

def draw_coexist_figure():
    # 创建无向图
    G = nx.Graph()

    # 添加节点
    nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    G.add_nodes_from(nodes)

    # 添加边
    edges = [(1, 3), (1, 4), (1, 7), (1, 5), (1, 9), (2, 5), (2, 9), (2, 4), (2, 10), (3, 10), (3, 6),
             (7, 10), (7, 6), (4, 8), (5, 6), (9, 6), (8, 10)]
    G.add_edges_from(edges)

    # 指定每个节点的颜色
    node_colors = ['#789440', '#9c4a09', '#c4d6a0', '#92cddc', '#bf9000', '#7f6000', '#c4d6a0',
                   '#31859b', '#bf9000', '#ea700d']
    plt.figure()
    # 绘制有向图
    nx.draw(G, with_labels=True, arrows=True, node_color=node_colors, node_size=1000)
    # plt.show()
    plt.savefig(f'./../figures/共存无向图.svg')


if __name__ == '__main__':
    # draw_conflict_figure()
    draw_coexist_figure()