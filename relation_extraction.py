import opennre
from relate_analysis import *
import numpy as np
import json

anaylsis_dir = 'analysis_data'

def load_model(type='tacred_bertentity_softmax', is_cuda=True):
    model = opennre.get_model(type)
    if is_cuda:
        model = model.cuda()
    return model


'''
TO DO:
   创建人物关系字典
   字典结构为:
     relation_dict{
        name1:{
            name2: {relation1: [rate], relation2: [rate]}
            name3: {relation1: [rate], relation2: [rate]}
            ...
        }
        ...
     }
'''
def create_relation_dict(name2id):
    relation_dict = {}

    for name1_tup in name2id.keys():
        name1_id = str(name2id[name1_tup])
        name1_related = {}
        for name2_tup in name2id.keys():
            if name2_tup == name1_tup:
                continue
            name2_id = str(name2id[name2_tup])
            name1_related[name2_id] = {}
        relation_dict[name1_id] = name1_related

    return relation_dict


# 提取句中人物实体间的关系，适用于句子中包含多个人物
def sents_rel_extract(model, sent, ents, n_dict: nameDict, relation_dict):
    for ent1 in ents:
        ent1_id = str(n_dict.find_id_by_name(ent1.text))
        ent1_start = ent1.start_char
        ent1_end = ent1.end_char
        ent1_rel = relation_dict[ent1_id]
        for ent2 in ents:
            ent2_id = str(n_dict.find_id_by_name(ent2.text))
            if ent1_id == ent2_id:
                continue
            ent2_start = ent2.start_char
            ent2_end = ent2.end_char
            result = model.infer({'text': sent,
                                  'h': {'pos': (ent2_start, ent2_end)},
                                  't': {'pos': (ent1_start, ent1_end)}
                                  })
            relate = result[0]
            rate = result[1]
            if relate in ent1_rel[ent2_id].keys():
                ent1_rel[ent2_id][relate].append(rate)
            else:
                ent1_rel[ent2_id][relate] = [rate]


def relation_extract(model, label_doc, n_dict):
    # 创建关系字典
    relation_dict = create_relation_dict(n_dict.name2id)
    for doc_list in label_doc.values():

        for para_doc in doc_list:
            if para_doc.text == '':
                continue
            for sent in para_doc.sentences:
                ents = [ent for ent in sent.ents if ent.type == 'PERSON' and ent.text in n_dict.all_names]
                # 句中只有一个人物实体时，无需提取关系
                if len(ents) == 1:
                    continue
                sents_rel_extract(model, sent.text, ents, n_dict, relation_dict)
    for n1_id in relation_dict:
        n1 = n_dict.find_name_by_id(n1_id)
        n1_rel = relation_dict[n1_id]
        for n2_id in n1_rel:
            n2 = n_dict.find_name_by_id(n2_id)
            print(f'{n1} 和 {n2}的可能关系是:')
            print_dict(n1_rel[n2_id])
    c =0
    for n1_id in relation_dict:
        n1_rel = relation_dict[n1_id]
        for n2_id in n1_rel:
            relates = n1_rel[n2_id]
            if not relates:
                n1_rel[n2_id] = ('unknown', 0)
                continue
            for r in relates:
                m_rate = np.mean(relates[r])
                relates[r] = m_rate
            lt = [x for x in zip(relates.keys(), relates.values())]
            sort_lt = sorted(lt, key=lambda x: x[-1], reverse=True)
            n1_rel[n2_id] = sort_lt[0]

    return relation_dict


def main():
    script_dir = "format_scripts/Joker.txt"
    script_doc = load_data(script_dir)
    persons, label_doc = role_ner(script_doc)
    name_set = role_name_combined(persons)
    n_dict = nameDict(script_doc, name_set)

    model = load_model('wiki80_bertentity_softmax')
    relation_dict = relation_extract(model, label_doc, n_dict)
    #
    # result = model.infer({'text': "Jack is Tom's father.",
    #              'h': {'pos': (0, 4)}, 't': {'pos': (8, 11)}})
    # print(result)

    for n1_id in relation_dict:
        n1 = n_dict.find_name_by_id(n1_id)
        n1_rel = relation_dict[n1_id]
        for n2_id in n1_rel:
            n2 = n_dict.find_name_by_id(n2_id)
            print(f'{n1} 和 {n2}的可能关系是: {n1_rel[n2_id][0]}')


def re_main(n_dict, label_doc, file_name):
    model = load_model('wiki80_bertentity_softmax')
    relation_dict = relation_extract(model, label_doc, n_dict)
    #
    # result = model.infer({'text': "Jack is Tom's father.",
    #              'h': {'pos': (0, 4)}, 't': {'pos': (8, 11)}})
    # print(result)
    json_data = json.dumps(relation_dict, indent=4)
    save_path = os.path.join(anaylsis_dir, file_name, 'relation_dict.json')
    with open(save_path, 'w') as f_re:
        f_re.write(json_data)
    return relation_dict


if __name__ == '__main__':
    main()



