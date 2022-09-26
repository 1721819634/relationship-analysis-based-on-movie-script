import numpy as np
import stanza
import os
import re
import pandas as pd
import json

word_change_dir = 'scene_change_words.txt'


class nameDict:
    def __init__(self, script_doc, name_set):
        self.name_id = 0
        self.name2id = {}
        self.total_roles = {}
        self.all_names = []
        self.script_doc = script_doc
        # 姓名出现次数的淘汰阈值
        self.threshold = 7

        self.role_total_count(name_set)
        self.role_num = len(self.total_roles)

    # 对剧本所有角色计数，并淘汰掉出现在阈值以下的角色
    def role_total_count(self, name_set):
        total_list = []
        for scene_id in self.script_doc.keys():
            scene_text = self.script_doc[scene_id]
            total_list.extend(scene_text)
        total_text = '\n'.join(total_list)

        for names in name_set:
            name1 = names[0]
            name2 = name1.upper()
            count = total_text.count(name1) + total_text.count(name2)
            if count > self.threshold:
                self.name2id[names] = self.name_id
                self.total_roles[self.name_id] = count
                self.all_names.extend(names)
                self.name_id += 1

    def find_id_by_name(self, role_name):
        for names in self.name2id.keys():
            if role_name in names:
                return self.name2id[names]

    def find_name_by_id(self, name_id):
        for names, id in zip(self.name2id.keys(), self.name2id.values()):
            if name_id == id:
                return names[0]

    def save_name2id(self, file_name):
        save_path = os.path.join('analysis_data', file_name, 'name2id.json')
        json_data = json.dumps(self.name2id, indent=4)
        with open(save_path, 'w') as f_n:
            f_n.write(json_data)


def print_dict(dict):
    for key, value in zip(dict.keys(), dict.values()):
        print(f'{key}: {value}')


def load_data(script_dir):
    script_doc = {}
    scene_id = 1
    ch_list = []
    scene_doc = []

    # 读入场景过渡转换词
    with open(word_change_dir, 'r', encoding='utf-8') as f_w:
        for line in f_w:
            ch_list.append(line.strip())
    pattern = '|'.join(ch_list)

    with open(script_dir, 'r', encoding='utf-8') as f_script:
        for para in f_script:
            # 检测到过渡词证明情节发生了变化
            if re.search(pattern, para) and len(line.split()) <= 3:
                script_doc[scene_id] = scene_doc.copy()
                scene_id += 1
                scene_doc.clear()
            scene_doc.append(para)
        scene_doc.append(para)
        script_doc[scene_id] = scene_doc.copy()
    return script_doc


def role_ner(script_doc):
    roles = []
    label_doc = {}

    script_nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')
    for scene_id, scene_text in zip(script_doc.keys(), script_doc.values()):
        in_docs = [stanza.Document([], text=d) for d in scene_text]  # 用stanza.Document对象包装每一句文本
        out_docs = script_nlp(in_docs)
        label_doc[scene_id] = out_docs
        for ner_doc in out_docs:
            doc = ner_doc.text
            if doc == "" or doc == "\n":
                continue
            for ent in ner_doc.ents:
                if ent.type == 'PERSON':
                    text = ent.text.strip('.,!?:()')
                    # 该模型有时会把单独的所有格识别为一个人物
                    text = (re.split("'s|'S", text))[0]
                    if text not in roles:
                        roles.append(text)

    return roles, label_doc


def role_name_combined(uncombined_names):
    name_set = []
    combined_names = []

    # 将单个单词的名字单独一类，多单词名字按小名部分分类
    for name_i in uncombined_names:
        same_names = []
        part_name_i = name_i.split()
        if len(part_name_i) != 1 or name_i in combined_names:
            continue
        if name_i.isupper():
            same_names.append(name_i.lower().capitalize())
            combined_names.append((name_i.lower().capitalize()))
        same_names.append(name_i)
        combined_names.append(name_i)
        for name_j in uncombined_names:
            if name_j in combined_names:
                continue
            part_name_j = name_j.split()

            if len(part_name_j) == 1:
                if name_j != name_i and name_j.lower() == same_names[0].lower():
                    same_names.append(name_j)
                    combined_names.append(name_j)
                if name_j in same_names[0]:
                    combined_names.append(name_j)
            elif len(part_name_j) >= 2:
                # 英文名的小名多为第一个单词，根据该性质合并同类人名
                if part_name_j[0].lower() == name_i.lower():
                    same_names.append(name_j)
                    combined_names.append(name_j)
                if '.' in part_name_j[0]:
                    if part_name_j[1].lower() == name_i.lower():
                        same_names.append(name_j)
                        combined_names.append(name_j)
        name_set.append(tuple(same_names))
    # 处理剩余的多单词名字
    for name in uncombined_names:
        if name in combined_names:
            continue
        n_tup = (name,)
        name_set.append(n_tup)

    return name_set


def find_para_role(doc, name2id, co_word_matrix=None):
    entities_id = []
    for key in name2id:
        name1 = key[0]
        name2 = name1.upper()
        count1 = doc.count(name1)
        count2 = doc.count(name2)
        if count1 or count2:
            n_id = name2id[key]
            entities_id.append(n_id)
            if co_word_matrix is not None:
                co_word_matrix[n_id][n_id] += (count1 + count2)
    return entities_id


def matrix_bath_increase(co_word_matrix, poses):
    for i in poses:
        for j in poses:
            if i == j:
                continue
            co_word_matrix[i][j] += 1


def co_word_analysis(n_dict: nameDict, script_doc):
    co_word_matrix_dict = {}
    talk_doc = []
    is_talk = False

    for scene_id, scene_docs in zip(script_doc.keys(), script_doc.values()):
        co_word_matrix = np.zeros((n_dict.role_num, n_dict.role_num))
        # doc为stanza库的Document对象，为源文本中的一个段落
        for doc in scene_docs:
            if doc == '' or doc == '\n':
                continue
            if ':' in doc:
                doc_sp = doc.split(':')
                d0 = doc_sp[0].split()
                d1 = doc_sp[1]
                if d1 != '\n' and d1 != '' and len(d0) <= 3:
                    is_talk = True
                    talk_doc.append(doc)
                    continue
            if is_talk:
                is_talk = False
                talk_text = '\n'.join(talk_doc)
                entities_id = find_para_role(talk_text, n_dict.name2id, co_word_matrix)
                if len(entities_id) >= 2:
                    matrix_bath_increase(co_word_matrix, entities_id)
                talk_doc.clear()
            entities_id = find_para_role(doc, n_dict.name2id, co_word_matrix)
            if len(entities_id) >= 2:
                matrix_bath_increase(co_word_matrix, entities_id)
        co_word_matrix_dict[scene_id] = co_word_matrix

    # 整个剧本的共现矩阵
    total_co_word_matrix = sum(co_word_matrix_dict.values())
    return co_word_matrix_dict, total_co_word_matrix


def create_similar_matrix(co_word_matrix, dim):
    similar_matrix = np.zeros((dim, dim))
    for i in range(dim):
        co_i = co_word_matrix[i][i]
        if co_i == 0:
            continue
        for j in range(dim):
            co_j = co_word_matrix[j][j]
            if co_j == 0:
                continue
            # ochiia系数
            ochiia = co_word_matrix[i][j] / (np.sqrt(co_i) * np.sqrt(co_j))
            similar_matrix[i][j] = round(ochiia, 4)
    return similar_matrix


def create_similar_dict(co_word_matrix_dict, dim):
    similar_matrix_dict = {}

    for scene_id, co_word_matrix in zip(co_word_matrix_dict.keys(), co_word_matrix_dict.values()):
        similar_matrix = create_similar_matrix(co_word_matrix, dim)
        similar_matrix_dict[scene_id] = similar_matrix

    return similar_matrix_dict


def save_matrix(matrix, n_dict: nameDict, s_path, file_name):
    save_dir = os.path.join(s_path, file_name + '.csv')
    names = [x[0] for x in n_dict.name2id.keys()]
    df = pd.DataFrame(matrix, index=names, columns=names)
    df.to_csv(save_dir)


def main():
    script_dir = "format_scripts/Joker.txt"
    script_doc = load_data(script_dir)
    # print_dict(script_doc)
    persons, label_doc = role_ner(script_doc)
    name_set = role_name_combined(persons)
    n_dict = nameDict(script_doc, name_set)
    print_dict(n_dict.name2id)


if __name__ == '__main__':
    main()
