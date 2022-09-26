import os
import re


script_data_dir = "scripts"
scene_change_words_dir = 'scene_change_words.txt'
format_data_dir = 'format_scripts/'

# 加载数据
def load_data(data_dir):
    script_data = []
    with open(data_dir, 'r', encoding='UTF-8') as f:
        for line in f:
            # print(line)
            script_data.append(line.strip())
    # 末尾加上空字符，方便后续处理
    script_data.append('')
    return script_data


# 获取路径下所有文件的文件名
def get_file_names(data_dir):
    files = os.listdir(data_dir)
    file_names = [os.path.splitext(x)[0] for x in files]
    return file_names


def format_data_by_sentence(document):
    # 判断是否为一个段落
    is_paragraph = False
    # 是否进入对话段落
    is_talk = False
    # 标点符合的正则表达式
    # pattern = '(?<! )(?=[.,!?:;\"\'])|(?<=[.,!?:;\"\'])(?! )|(?<! )(?=-{2})|(?<=-{2})(?! )'
    format_doc = []
    paragraph = []
    talk_para = []
    scene_change_words = []

    with open(scene_change_words_dir, 'r', encoding='UTF-8') as f_words:
        for word in f_words:
            scene_change_words.append(word.strip('\n'))
        # print(scene_change_words)
    pattern = '|'.join(scene_change_words)

    for line in document:
        if is_paragraph:
            # 段落的下一行为空，代表段落结束，清空段落列表
            if line == '':
                is_paragraph = False
                if len(paragraph) != 0:
                    # 将每个段落单独成一行
                    union = ' '.join(paragraph)

                    # 往所有标点前加个空格
                    # union = re.sub(pattern, r' ', union)
                    # sentences = re.split(r'\.\.\.|\.|\?|!|-{2}', union)
                    format_doc.append(union)
                format_doc.append(line)
                paragraph.clear()
            else:
                paragraph.append(line)

        elif is_talk:
            # 处理人物名后面的带括号的注释
            if line.startswith('('):
                if line.endswith(')'):
                    talk_para.append(line)
                else:
                    paragraph.append(line)
                continue
            if line.endswith(')'):
                paragraph.append(line)
                union = ' '.join(paragraph)
                talk_para.append(union)
                paragraph.clear()
                continue

            if line == '':
                is_talk = False
                if len(talk_para) != 0:
                    union = ' '.join(talk_para)
                    format_doc.append(union)
                format_doc.append(line)
                talk_para.clear()
            else:
                talk_para.append(line)

        else:
            # 进入新的段落
            if line != '':
                # 识别转场过渡词
                if re.search(pattern, line) and len(line.split(' ')) <= 4:
                    format_doc.append(line)
                    continue

                if line.startswith('INT') or line.startswith('EXT'):
                    format_doc.append(line)
                    continue
                '''
                TO DO:
                   判断是否为人物对话
                        英文剧本的人物对话都是先空一行，人物名字单独一行且单词数不大于3，下一行紧接着说话内容
                        根据此特性划分人物对话
                '''
                word_num = len(line.split(' '))
                # print('word_num = {}'.format(word_num))
                if 0 < word_num <= 3:
                    is_talk = True
                    talk_para.append(line.lower().capitalize() + ':')
                    continue

                is_paragraph = True
                paragraph.append(line)
            else:
                format_doc.append(line)

    return format_doc


def de_main(script_path):
    doc = load_data(script_path)
    format_doc = format_data_by_sentence(doc)
    file_name = os.path.basename(script_path)
    file_name = file_name.split('.')[0]
    with open(format_data_dir + f'{file_name}.txt', 'w', encoding='UTF-8') as f:
        for line in format_doc:
            f.write('{}\n'.format(line.strip()))

    return {'msg': '读取成功！', 'data': file_name}


if __name__ == '__main__':
    file_names = get_file_names(script_data_dir)
    print(file_names)
    for file_name in file_names:
        script_path = os.path.join(script_data_dir, '{}.txt'.format(file_name))
        doc = load_data(script_path)
        # print(doc)
        format_doc = format_data_by_sentence(doc)
        # print('-----------------------------------')
        # print(format_doc)
        print('----------------- {} is complied ------------------'.format(file_name))

        with open('format_scripts/{}.txt'.format(file_name), 'w', encoding='UTF-8') as f:
            for line in format_doc:
                f.write('{}\n'.format(line.strip()))

    # doc = load_data('scripts/15-Minutes.txt')
    # format_doc = format_data_by_sentence(doc)
    # with open('format_scripts/15-Minutes.txt', 'w', encoding='UTF-8') as f:
    #     for line in format_doc:
    #         f.write('{}\n'.format(line.strip()))





