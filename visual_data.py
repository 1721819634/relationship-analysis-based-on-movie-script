import networkx as nx
from relate_analysis import *

import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Graph, Bar, Grid, Line
from pyecharts.components import Table
import os


anaylsis_dir = 'analysis_data'
format_data_dir = 'format_scripts'

# 生产人物社交关系网络
def create_social_net(matrix, n_dict):
    G = nx.Graph()
    node_lists = [(x, {'name': n_dict.find_name_by_id(x)}) for x in range(n_dict.role_num)]
    G.add_nodes_from(node_lists)
    # 添加边
    for i in range(n_dict.role_num):
        for j in range(i + 1, n_dict.role_num):
            weight = matrix[i][j]
            if weight != 0:
                G.add_edge(i, j, weight=weight)
    # 去掉孤立节点
    for node in list(G.nodes):
        if G.degree(node) == 0:
            G.remove_node(node)
    return G
    # print(G.graph)
    # print(G.nodes.data())
    # print(G.edges.data())


def create_epoch_social_net(matrix_dict, n_dict):
    G_dict = {}
    for scene_id, matrix in zip(matrix_dict.keys(), matrix_dict.values()):
        G = create_social_net(matrix, n_dict)
        G_dict[scene_id] = G
    return G_dict


# 网络中心性分析
def centrality_analysis(G):
    # 度中心性
    degree_c = nx.degree_centrality(G)
    # 中介中心性
    bet_c = nx.betweenness_centrality(G)
    # 接近中心性
    close_c = nx.closeness_centrality(G)
    # 合成中心性
    sum_c = {}
    for node in G.nodes:
        sum_c[node] = (degree_c[node] + bet_c[node] + close_c[node])/3
    # print(sum_c)
    return degree_c, bet_c, close_c, sum_c


# 计算网络密度
def cal_density(G):
    return nx.density(G)


# 计算网络平均聚类系数
def cal_ave_cluster(G):
    return nx.average_clustering(G)


# 计算平均路径长度
def cal_ave_length(G):
    return nx.average_shortest_path_length(G)


def net_plot(G, n_dict, matrix, net_path, scene_id=0):
    save_dir = os.path.join(net_path, str(scene_id) + '_net.html')
    total_roles = n_dict.total_roles
    p_nodes = []
    for node in list(G.nodes):
        p_nodes.append({"name": G.nodes[node]['name'], "symbolSize": G.degree(node)+1, "value": total_roles[node]})
    p_links = []
    for edge in list(G.edges):
        p_links.append({"source": n_dict.find_name_by_id(edge[0]), "target": n_dict.find_name_by_id(edge[1]),
                        "value": matrix[edge[0]][edge[1]]})
    p = f"情节{scene_id}-" if scene_id else ""
    c = (
        Graph(init_opts=opts.InitOpts(width='720px', height='720px'))
            .add("", p_nodes, p_links, repulsion=2500)
            .set_global_opts(title_opts=opts.TitleOpts(title=p + "人物社会关系网络", pos_left='center'))
            .render(save_dir)
    )


# 绘制人物中心度数据
def centrality_plot(G, n_dict, net_path, scene_id=0):
    degree_c, bet_c, close_c, sum_c= centrality_analysis(G)
    save_dir = os.path.join(net_path, str(scene_id) + '_centrality.html')
    table = Table()

    headers = ['角色名称', '度中心性', '中介中心性', '接近中心性', '综合中心性']
    rows = []
    for node in G.nodes:
        name = n_dict.find_name_by_id(node)
        rows.append([name, round(degree_c[node], 4), round(bet_c[node], 4), round(close_c[node], 4), round(sum_c[node], 4)])
        sort_rows = sorted(rows, key=lambda x: x[-1], reverse=True)
    table.add(headers, sort_rows)

    p = f"情节{scene_id}-" if scene_id else ""

    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(title=p + "人物中心性")
    )
    table.render(save_dir)


# 绘制情节演化数据
def scene_analysis(n_dict, matrix_dict, net_path):
    save_dir = os.path.join(net_path, "scene_analysis.html")
    desitys = []
    clusters = []
    # lengths = []
    edges_n = []
    nodes_n = []
    x_data = []

    for scene_id, scene_matrix in zip(matrix_dict.keys(), matrix_dict.values()):
        scene_g = create_social_net(scene_matrix, n_dict)
        if len(scene_g.nodes) == 0:
            continue
        # 绘画社交网络
        net_plot(scene_g, n_dict, scene_matrix, net_path, scene_id)
        centrality_plot(scene_g, n_dict, net_path, scene_id)
        x_data.append(str(scene_id))

        # 存储数据
        desitys.append(cal_density(scene_g))
        clusters.append(cal_ave_cluster(scene_g))
        # lengths.append(cal_ave_length(scene_g))
        edges_n.append(len(scene_g.edges))
        nodes_n.append(len(scene_g.nodes))

    bar = (
        Bar()
            .add_xaxis(x_data)
            .add_yaxis(
            "节点数",
            nodes_n,
            color="#d14a61",
            yaxis_index=0,
        )
            .add_yaxis(
            "边数",
            edges_n,
            color="#5793f3",
            yaxis_index=1,
        )
            .extend_axis(
            yaxis=opts.AxisOpts(
                name="边数",
                type_="value",
                min_=0,
                max_=max(edges_n) * 2,
                position="right",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            )
        )

            .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="节点数",
                min_=0,
                max_=30,
                position="left",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
            title_opts=opts.TitleOpts(title="社会关系演化分析"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )

    line = (
        Line()
            .add_xaxis(x_data)
            .add_yaxis(
            "图密度",
            desitys,
            xaxis_index=1,
            yaxis_index=2,
            color="#675bba",
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            "平均聚类系数",
            clusters,
            xaxis_index=1,
            yaxis_index=3,
            color="#FFC0CB",
            label_opts=opts.LabelOpts(is_show=False),
        )
        #     .add_yaxis(
        #     "平均路径长度",
        #     lengths,
        #     xaxis_index=1,
        #     yaxis_index=3,
        #     color="#96CE54",
        #     label_opts=opts.LabelOpts(is_show=False),
        # )
            .extend_axis(
            yaxis=opts.AxisOpts(
                name="平均聚类系数",
                min_=0,
                max_=1,
                position="right",
                grid_index=1,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#96CE54")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
        )
            .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                name="密度",
                min_=0,
                max_=1,
                position="left",
                grid_index=1,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#675bba")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
            legend_opts=opts.LegendOpts(pos_top="55%"),
        )
    )

    grid = Grid()
    grid.add(bar, opts.GridOpts(pos_bottom="58%"), is_control_axis_index=True)
    grid.add(line, opts.GridOpts(pos_top="58%"), is_control_axis_index=True)
    grid.render(save_dir)


# 绘制角色对的亲密度演化数据
def roles_related_plot(matrix_dict, n_dict: nameDict, re_path):

    matrix_list = list(matrix_dict.values())
    num = n_dict.role_num
    x_data = [str(x) for x in matrix_dict.keys()]

    for i in range(num):
        name_i = n_dict.find_name_by_id(i)
        for j in range(i+1, num):
            name_j = n_dict.find_name_by_id(j)
            y_data = [m[i][j] for m in matrix_list]

            save_dir = os.path.join(re_path, f"{name_i}-{name_j}.html")
            L = Line(init_opts=opts.InitOpts(width='720px', height='380px'))
            L.add_xaxis(x_data)
            L.add_yaxis('关系亲密度', y_data)
            L.set_global_opts(title_opts=opts.TitleOpts(title=f"{name_i}-{name_j}关系演化"),
                              yaxis_opts=opts.AxisOpts(
                                  name='关系亲密度',
                                  min_=0,
                                  max_=1,
                                  position="left",
                              ),
                              xaxis_opts=opts.AxisOpts(name='情节'))
            L.render(save_dir)


def v_main(file_name):
    script_dir = os.path.join(format_data_dir, file_name+'.txt')
    # 创建数据文件夹
    s_path = os.path.join(anaylsis_dir, file_name)
    if not os.path.exists(s_path):
        os.mkdir(s_path)
    net_path = os.path.join(s_path, 'social_network')
    if not os.path.exists(net_path):
        os.mkdir(net_path)
    re_path = os.path.join(s_path, 'role_related_data')
    if not os.path.exists(re_path):
        os.mkdir(re_path)

    script_doc = load_data(script_dir)
    # print_dict(script_doc)
    persons, label_doc = role_ner(script_doc)
    name_set = role_name_combined(persons)
    n_dict = nameDict(script_doc, name_set)

    # print_dict(n_dict.total_roles)
    # print_dict(n_dict.name2id)
    co_word_matrix_dict, total_co_word_matrix = co_word_analysis(n_dict, script_doc)
    similar_matrix_dict = create_similar_dict(co_word_matrix_dict, n_dict.role_num)
    total_similar_matrix = create_similar_matrix(total_co_word_matrix, n_dict.role_num)
    # save_matrix(total_co_word_matrix, n_dict, s_path, '共现矩阵')
    # save_matrix(total_similar_matrix, n_dict, s_path, '相似矩阵')

    roles_related_plot(similar_matrix_dict, n_dict, re_path)
    G = create_social_net(total_similar_matrix, n_dict)
    net_plot(G, n_dict, total_similar_matrix, net_path)
    centrality_plot(G, n_dict, net_path)
    scene_analysis(n_dict, similar_matrix_dict, net_path)

    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True)
    # plt.show()
    scene_ids = script_doc.keys()
    d = {'n_dict': n_dict, 'label_doc': label_doc, 'scene_ids': scene_ids}
    return {'msg': '网络生成成功！', 'data': d}


if __name__ == '__main__':
    v_main("Joker")
