import matplotlib
matplotlib.use('Agg')
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import sys
sys.path.append('../')
from utils import load_data, load_as_dict, get_result_path, \
    create_dir_if_not_exists, get_norm_str
from results import load_result
from exp import get_text_label
from vis import sorted_dict, info_dict_preprocess, draw_extra, list_safe_get, calc_subplot_size


TRUE_MODEL = 'astar'


def draw_graph(g, info_dict, weight, weight_max, weight_min):
    if g is None:
        return
    pos = sorted_dict(graphviz_layout(g))
    weight_array = []
    for i in range(len(weight)):
        weight_array.append(weight[i][0])
    for i in range(len(weight_array)):
        if weight_array[i] > 0.85:
            weight_array[i] = 0.85
        if weight_array[i] < 0.7:
            weight_array[i] = 0.7
        weight_array[i] = (weight_array[i] - weight_min) / (weight_max - weight_min)
    # print(weight_array)
    # print(g.graph['gid'])
    # weight_array = normalize(weight, norm='l1', axis=0)
    if info_dict['node_label_name'] is not None:
        node_labels = sorted_dict(nx.get_node_attributes(g, info_dict['node_label_name']))
        # print(weight_array)
        # from light to dark
        # color_values = sorted(range(len(weight_array)), key=lambda k: weight_array[k])
        color_values = []
        # print(color_values)
        for i in range(len(pos.keys())):
            if len(str(hex(int(255 - 255 * weight_array[i])))) <= 3:
                if len(str(hex(int(80 + 255 - 255 * weight_array[i])))) < 3:
                    color_values.append("#0" + str(hex(int(80 + 255 - 255 * weight_array[i])))[2:] + "0" +
                                    str(hex(int(255 - 255 * weight_array[i])))[2:] + "ff")
                else:
                    color_values.append("#" + str(hex(int(80 + 255 - 255 * weight_array[i])))[2:] + "0" +
                                        str(hex(int(255 - 255 * weight_array[i])))[2:] + "ff")
            else:
                if len(str(hex(int(80 + 255 - 255 * weight_array[i])))) < 3:
                    color_values.append("#0" + str(hex(int(80 + 255 - 255 * weight_array[i])))[2:] +
                                        str(hex(int(255 - 255 * weight_array[i])))[2:] + "ff")
                else:
                    color_values.append("#" + str(hex(int(255 - 255 * weight_array[i])))[2:] +
                                    str(hex(int(255 - 255 * weight_array[i])))[2:] + "ff")
        print(color_values)
    else:
        node_labels = {}
        for i in range(len(pos.keys())):
            node_labels[str(i)] = ''
        node_labels = sorted_dict(node_labels)
        color_values = []
        for i in range(len(pos.keys())):
            if len(str(hex(int(255 - 255 * weight_array[i])))) <= 3:
                color_values.append("#0" + str(hex(int(80 + 255 - 255 * weight_array[i])))[2:] + "0" +
                                    str(hex(int(255 - 255 * weight_array[i])))[2:] + "ff")
            else:
                color_values.append("#" + str(hex(int(80 + 255 - 255 * weight_array[i])))[2:] +
                                    str(hex(int(255 - 255 * weight_array[i])))[2:] * 2 + "ff")
    for key, value in node_labels.items():
        if len(value) > 6:
            value = value[0:6]  # shorten the label
        node_labels[key] = value
    if info_dict['node_label_name'] is not None:
        # cmap=plt.cm.Blues or cmap=plt.cm.PuBu or cmap=plt.Reds it depends on you
        nx.draw_networkx(g, pos, nodelist=pos.keys(),
                        node_color=color_values, with_labels=True,
                        node_size=info_dict['draw_node_size'], labels=node_labels,
                        font_size=info_dict['draw_node_label_font_size'])
    else:
        nx.draw_networkx(g, pos, nodelist=pos.keys(), node_color=color_values,
                         with_labels=True, node_size=info_dict['draw_node_size'],
                         labels=node_labels)

    if info_dict['draw_edge_label_enable'] == True:
        edge_labels = nx.get_edge_attributes(g, info_dict['edge_label_name'])
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,
                                     font_size=info_dict[
                                         'draw_edge_label_font_size'])


def vis(q=None, gs=None, info_dict=None, weight=None, weight_max=0, weight_min=0):
    plt.figure()
    info_dict_preprocess(info_dict)

    # get num
    graph_num = 1 + len(gs)
    plot_m, plot_n = calc_subplot_size(graph_num)

    # draw query graph
    ax = plt.subplot(plot_m, plot_n, 1)
    draw_graph(q, info_dict, weight[0], weight_max, weight_min)
    draw_extra(0, ax, info_dict,
               list_safe_get(info_dict['each_graph_text_list'], 0, ""))

    # draw graph candidates
    for i in range(len(gs)):
        ax = plt.subplot(plot_m, plot_n, i + 2)
        draw_graph(gs[i], info_dict, weight[i + 1], weight_max, weight_min)
        draw_extra(i, ax, info_dict,
                   list_safe_get(info_dict['each_graph_text_list'], i + 1, ""))

    # plot setting
    # plt.tight_layout()
    left = 0.01  # the left side of the subplots of the figure
    right = 0.99  # the right side of the subplots of the figure
    top = 1 - info_dict['top_space']  # the top of the subplots of the figure
    bottom = \
        info_dict['bottom_space']  # the bottom of the subplots of the figure
    wspace = \
        info_dict['wbetween_space']  # the amount of width reserved for blank space between subplots
    hspace = \
        info_dict['hbetween_space']  # the amount of height reserved for white space between subplots

    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top,
                        wspace=wspace, hspace=hspace)

    # save / display
    save_path = info_dict['plot_save_path']
    if save_path is None or save_path == "":
        plt.show()
    else:
        sp = info_dict['plot_save_path']
        print('Saving query vis plot to {}'.format(sp))
        plt.savefig(sp, dpi=info_dict['plot_dpi'])


if __name__ == '__main__':
    dataset = 'aids700nef'
    model = 'astar'
    concise = True
    ext = 'png'
    norms = [True, False]
    dir = get_result_path() + '/{}/att_vis/{}'.format(dataset, model)
    create_dir_if_not_exists(dir)
    info_dict = {
        # draw node config
        'draw_node_size': 150 if dataset != 'linux' else 10,
        'draw_node_label_enable': True,
        'node_label_name': None if dataset == 'linux' else 'type',
        'draw_node_label_font_size': 6,
        'draw_node_color_map': {'C': '#ff6666',
                                'O': 'lightskyblue',
                                'N': 'yellowgreen',
                                'movie': '#ff6666',
                                'tvSeries': '#ff6666',
                                'actor': 'lightskyblue',
                                'actress': '#ffb3e6',
                                'director': 'yellowgreen',
                                'composer': '#c2c2f0',
                                'producer': '#ffcc99',
                                'cinematographer': 'gold'},
        # draw edge config
        'draw_edge_label_enable': False,
        'edge_label_name': 'valence',
        'draw_edge_label_font_size': 6,
        # graph text info config
        'each_graph_text_list': [],
        'each_graph_text_font_size': 8,
        'each_graph_text_pos': [0.5, 1.05],
        # graph padding: value range: [0, 1]
        'top_space': 0.20 if concise else 0.26,  # out of whole graph
        'bottom_space': 0.05,
        'hbetween_space': 0.6 if concise else 1,  # out of the subgraph
        'wbetween_space': 0,
        # plot config
        'plot_dpi': 200,
        'plot_save_path': ''
    }
    weight_data = load_as_dict("/home/songbian/Documents/fork/GraphEmbedding/model/Siamese/logs"
                               "/siamese_classification_aids700nef_2018-07-28T10:09:33"
                               "/test_info.pickle")
    weight = weight_data['atts']
    weight_max_array = []
    weight_min_array = []
    for i in range(len(weight)):
        weight_min_array.append(min(weight[i]))
        weight_max_array.append(max(weight[i]))
    weight_max = max(weight_max_array)
    weight_min = min(weight_min_array)
    print("max:", weight_max)
    print("min:", weight_min)
    weight_max = 0.85
    weight_min = 0.7
    train_data = load_data(dataset, train=True)
    test_data = load_data(dataset, train=False)
    row_graphs = test_data.graphs
    col_graphs = train_data.graphs
    r = load_result(dataset, model, row_graphs=row_graphs, col_graphs=col_graphs)
    tr = load_result(dataset, TRUE_MODEL, row_graphs=row_graphs, col_graphs=col_graphs)
    for norm in norms:
        ids = r.sort_id_mat(norm)
        m, n = r.m_n()
        num_vis = 10
        for i in range(len(row_graphs)):
            q = test_data.graphs[i]
            gids = ids[i][:5]
            # gids = np.concatenate([ids[i][:3], [ids[i][int(n / 2)]], ids[i][-3:]])
            gs = [train_data.graphs[j] for j in gids]
            weight_query = []
            # hard code 560 determine the size of training code
            weight_query.append(weight[len(col_graphs) + i])
            for j in gids:
                weight_query.append(weight[j])
            info_dict['each_graph_text_list'] = \
                [get_text_label(dataset, r, tr, i, i, q, model, norm, True, concise)] + \
                [get_text_label(dataset, r, tr, i, j,
                                train_data.graphs[j], model, norm, False, concise) \
                 for j in gids]
            info_dict['plot_save_path'] = '{}/query_vis_{}_{}_{}{}.{}'.format(
                dir, dataset, model, i, get_norm_str(norm), ext)
            vis(q, gs, info_dict, weight_query, weight_max, weight_min)


