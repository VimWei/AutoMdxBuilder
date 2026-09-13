#!/usr/bin/env python
# @Date    : 2023-11-16 00:00:48
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.6

import os
import re
import shutil

from colorama import Fore
from tomlkit import dumps


class TextDictDtmpl:
    """ 文本词典（模板D） """
    def __init__(self, amb):
        self.settings = amb.settings
        self.func = amb.func

    def make_source_file(self):
        """ 制作预备 txt 源文本 """
        # 清空临时目录下所有文件
        for fname in os.listdir(self.settings.dir_output_tmp):
            fpath = os.path.join(self.settings.dir_output_tmp, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
        # 初始化, 检查原材料: index_all, syns, info, data
        check_result = self._check_raw_files()
        # 开始制作
        if check_result:
            print('\n材料检查通过, 开始制作词典……\n')
            # 预定义输出文件名
            file_final_txt = os.path.join(self.settings.dir_output_tmp, self.settings.fname_final_txt)
            file_dict_info = os.path.join(self.settings.dir_output_tmp, self.settings.fname_dict_info)
            # 1.分步生成各部分源文本
            file_1 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_entries_with_navi_text)  # 文本(有导航栏)词条
            file_2 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_syn)  # 同义词重定向
            file_3 = os.path.join(self.settings.dir_output_tmp, self.settings.fname_relinks_st)  # 繁简重定向
            # (1) 生成文本(主)词条, 带层级导航
            headwords = self._make_entries_with_navi(check_result[0], file_1)
            if headwords:
                # (2) 生成近义词重定向
                if check_result[1]:
                    headwords += self.func.make_relinks_syn(check_result[1], file_2)
                # (3) 生成繁简通搜重定向
                if self.settings.simp_trad_flg:
                    self.func.make_relinks_st(headwords, file_3)
                # 2.合并成最终 txt 源文本
                entry_total = self.func.merge_and_count([file_1, file_2, file_3], file_final_txt)
                print(f'\n源文本 "{self.settings.fname_final_txt}"（共 {entry_total} 词条）生成完毕！')
                # 3.生成 info.html
                if self.settings.multi_volume:
                    self.func.generate_info_html(check_result[2], file_dict_info, self.settings.name, 'D', self.settings.volume_num)
                else:
                    self.func.generate_info_html(check_result[2], file_dict_info, self.settings.name, 'D')
                # 返回制作结果
                return [file_final_txt, check_result[3], file_dict_info]
            else:
                return None
        else:
            print(Fore.RED + "\n材料检查不通过, 请确保材料准备无误再执行程序" + Fore.RESET)
            return None

    def extract_final_txt(self, file_final_txt, out_dir, dict_name, multi_vols_flg=False, volume_num=1):
        """ 从模板D词典的源 txt 文本中提取 index, syns 信息 """
        dcts = []
        syns = []
        # (一) 分析提取源 txt 文本
        with open(file_final_txt, 'r', encoding='utf-8') as fr:
            text = fr.read()
            # 1.提取 index_all
            pat_index = re.compile(r'^<div class="index-all" style="display:none;">(\d+)\|(.+?)\|\d+</div>.+?(<div class="(entry-body|toc-list)">[^\r\n]+</div>)$', flags=re.MULTILINE+re.DOTALL)
            for t in pat_index.findall(text):
                if t[2].startswith('<div class="entry-body">'):
                    body = re.search(r'<div class="entry-body">(.+?)</div>$', t[2], flags=re.MULTILINE).group(1)
                else:
                    body = ''
                dct = {
                    "id": t[0],
                    "name": t[1],
                    "body": body
                }
                dcts.append(dct)
            # 2.识别 name_abbr
            mth = re.search(r'^<link rel="stylesheet" type="text/css" href="([^>/\"\.]+?)\.css"/>$', text, flags=re.MULTILINE)
            if mth:
                name_abbr = mth.group(1).upper()
            else:
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "未识别到词典缩略字母, 已设置默认值")
                name_abbr = 'XXXXCD'
            # 3.提取 syns
            for t in self.settings.pat_relink.findall(text):
                if not t[1].startswith(name_abbr):
                    syns.append((t[0], t[1]))
        # (二) 整理输出提取结果
        # 1.index_all.txt
        dcts.sort(key=lambda dct: dct["id"], reverse=False)
        with open(os.path.join(out_dir, 'index_all.txt'), 'w', encoding='utf-8') as fw:
            for dct in dcts:
                if dct["body"] == '':
                    fw.write(f'{dct["name"]}\t\n')
                else:
                    fw.write(f'{dct["name"]}\t{dct["body"]}\n')
        # 2.syns.txt
        if syns:
            with open(os.path.join(out_dir, 'syns.txt'), 'w', encoding='utf-8') as fw:
                fw.writelines(f'{s[0]}\t{s[1]}\n' for s in syns)
        # 3. build.toml 文件
        self.settings.load_build_toml(os.path.join(self.settings.dir_lib, self.settings.build_tmpl), False)
        self.settings.build["global"]["templ_choice"] = "D"
        self.settings.build["global"]["name"] = dict_name
        self.settings.build["global"]["name_abbr"] = name_abbr
        # 判断 add_headwords
        if not re.search(r'^<div class="entry-headword">[^<]+</div>$', text, flags=re.MULTILINE):
            self.settings.build["template"]["d"]["add_headwords"] = False
        with open(os.path.join(out_dir, 'build.toml'), 'w', encoding='utf-8') as fw:
            fw.write(dumps(self.settings.build))

    def _make_entries_with_navi(self, file_index_all, file_out):
        headwords = []
        """ (一) 生成文本(主)词条, 带层级导航 """
        # 1.读取全索引文件
        dcts = self.func.read_index_all_file(file_index_all, False)
        # 2.生成主体词条
        if dcts:
            with open(file_out, 'w', encoding='utf-8') as fw:
                tops = []
                headwords_stem = []
                len_dcts = len(dcts)
                for i, dct in enumerate(dcts):
                    part_css = f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                    # 词头, 索引备份
                    if dct["level"] == -1:
                        part_title = f'{dct["title"]}\n'
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|{dct["title"]}|{dct["vol_n"]!s}</div>\n'
                    else:
                        part_title = f'{self.settings.name_abbr}_{dct["title"]}\n'
                        part_index = f'<div class="index-all" style="display:none;">{str(dct["id"]).zfill(10)}|【L{dct["level"]!s}】{dct["title"]}|{dct["vol_n"]!s}</div>\n'
                    # top-navi-level 部分
                    part_top = '<div class="top-navi-level">'
                    part_top += f'<span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span>'
                    for x in range(len(dct["navi_bar"])):
                        cname = 'navi-item'
                        link_name = f'{self.settings.name_abbr}_{dct["navi_bar"][x]}'
                        if x == len(dct["navi_bar"])-1 and dct["level"] == -1:
                            cname = 'navi-item-entry'
                            link_name = dct["navi_bar"][x]
                        aname = dct["navi_bar"][x]
                        part_top += f'<span class="sep-navi">»</span><span class="{cname}"><a href="entry://{link_name}">{aname}</a></span>'
                    part_top += '</div>\n'
                    # item-list 部分
                    part_list = self.func.get_item_list(dct)
                    # 词条部分
                    if dct["level"] != -1 and dct["body"] == '':
                        part_headword = ''
                        part_body = ''
                    elif dct["level"] != -1 and dct["body"] != '' or not self.settings.add_headwords:
                        part_headword = ''
                        part_body = f'<div class="entry-body">{dct["body"]}</div>\n'
                    elif re.match(r'<(p|div|html|body|title|head)', dct["body"], flags=re.IGNORECASE):
                        part_headword = f'<div class="entry-headword">{dct["title"]}</div>\n'
                        part_body = f'<div class="entry-body">{dct["body"]}</div>\n'
                    else:
                        part_headword = f'<div class="entry-headword">{dct["title"]}</div>\n'
                        part_body = f'<div class="entry-body"><p>{dct["body"]}</p></div>\n'
                    # bottom-navi 部分
                    part_left = ''
                    part_right = ''
                    if i == 0:
                        # 只有右
                        if dcts[i+1]["level"] != -1:
                            part_right = f'<span class="navi-item-right"><a href="entry://{self.settings.name_abbr}_{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                        else:
                            part_right = f'<span class="navi-item-right"><a href="entry://{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                    elif i == len_dcts-1:
                        # 只有左
                        if dcts[i-1]["level"] != -1:
                            part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{self.settings.name_abbr}_{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                        else:
                            part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                    else:
                        if dcts[i-1]["level"] != -1:
                            part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{self.settings.name_abbr}_{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                        else:
                            part_left = f'<span class="navi-item-left">☚&#8197;<a href="entry://{dcts[i-1]["title"]}">{dcts[i-1]["title"]}</a></span>'
                        if dcts[i+1]["level"] != -1:
                            part_right = f'<span class="navi-item-right"><a href="entry://{self.settings.name_abbr}_{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                        else:
                            part_right = f'<span class="navi-item-right"><a href="entry://{dcts[i+1]["title"]}">{dcts[i+1]["title"]}</a>&#8197;☛</span>'
                    part_bottom = '<div class="bottom-navi">' + part_left + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + part_right + '</div>\n'
                    # 合并写入
                    fw.write(part_title+part_css+part_index+part_top+part_list+part_headword+part_body+part_bottom+'</>\n')
                    headwords.append(dct["title"])
                    # 收集顶级章节
                    if dct["level"] != -1:
                        if dct["level"] == 0:
                            tops.append(dct["title"])
                        elif dct["level"] == 1 and self.settings.multi_volume:
                            pass
                        else:
                            headwords_stem.append(dct["title"])
                # 3.写入总目词条
                toc_entry = f'TOC_{self.settings.name_abbr}\n'
                toc_entry += f'<link rel="stylesheet" type="text/css" href="{self.settings.name_abbr.lower()}.css"/>\n'
                toc_entry += f'<div class="top-navi-level"><span class="navi-item"><a href="entry://TOC_{self.settings.name_abbr}">🕮</a></span></div>\n'
                toc_entry += '<div class="toc-list"><ul>'
                for top in tops:
                    toc_entry += f'<li><a href="entry://{self.settings.name_abbr}_{top}">{top}</a></li>'
                toc_entry += '</ul><div class="bottom-navi">' + '<span class="navi-item-middle">&#8197;&#12288;&#8197;</span>' + '</div>\n'
                toc_entry += '</div>\n</>\n'
                fw.write(toc_entry)
                # 4.章节重定向
                fw.writelines(f'{word}\n@@@LINK={self.settings.name_abbr}_{word}\n</>\n' for word in headwords_stem)
            print("文本词条(有导航栏)已生成")
        else:
            pass
        return headwords

    def _check_index_alls(self, dir_input, dir_out):
        """ 检查 index_all 文本 """
        pass_flg = True
        file_index_all = os.path.join(dir_input, self.settings.fname_index_all)
        # 1.扫描识别总 index_all 文件
        final_index_all = os.path.join(dir_out, self.settings.fname_index_all)
        index_check_num = self.func.text_file_check(file_index_all)
        if index_check_num == 2:
            shutil.copy(file_index_all, final_index_all)
            # 读取检查总 index_all 文件
            with open(final_index_all, 'r', encoding='utf-8') as fr:
                for i, line in enumerate(fr, start=1):
                    mth_stem = self.settings.pat_stem_text.match(line)
                    if mth_stem:
                        # 章节
                        pass
                    elif self.settings.pat_tab.match(line):
                        # 词条
                        pass
                    else:
                        print(Fore.RED + "ERROR: " + Fore.RESET + f"index_all.txt 第 {i} 行未匹配, 请检查")
                        pass_flg = False
                        break
        elif index_check_num == 1:
            pass_flg = False
        elif self.settings.multi_volume:
            # 2.扫描识别分 index_all
            lst_file_index_all = []
            pat1 = re.compile(r'index_all_(\d+)', flags=re.IGNORECASE)
            lst_n = []
            for fname in os.listdir(dir_input):
                if fname.endswith('.txt') and pat1.match(fname):
                    vol_n = int(pat1.match(fname).group(1))
                    fp = os.path.join(dir_input, fname)
                    if vol_n not in lst_n:
                        index_check_num = self.func.text_file_check(fp)
                        if index_check_num == 1:
                            pass_flg = False
                            break
                        elif index_check_num == 2:
                            lst_file_index_all.append({"vol_n": vol_n, "path": fp})
                            lst_n.append(vol_n)
            if pass_flg and not lst_file_index_all:
                print(Fore.RED + "ERROR: " + Fore.RESET + "未读取到 index_all 文件")
                pass_flg = False
            elif pass_flg:
                self.settings.volume_num = len(lst_file_index_all)
                # 3.合并各 index_all 文本, 顺便检查格式
                lst_file_index_all.sort(key=lambda dct: dct["vol_n"], reverse=False)
                pat_vname = re.compile(r'index_all_\d+_(.+?)\.txt', flags=re.IGNORECASE)
                with open(final_index_all, 'w', encoding='utf-8') as fw:
                    break_flg = False
                    for x in range(len(lst_file_index_all)):
                        fname = os.path.split(lst_file_index_all[x]["path"])[1]
                        with open(lst_file_index_all[x]["path"], 'r', encoding='utf-8') as fr:
                            # 获取卷名, 写入卷标
                            try:
                                vname = self.settings.vol_names[x]
                            except IndexError:
                                vname = None
                            if not vname:
                                if pat_vname.match(fname):
                                    vname = pat_vname.match(fname).group(1)
                                else:
                                    vname = '第'+str(lst_file_index_all[x]["vol_n"]).zfill(2)+'卷'
                            fw.write('【L0】'+vname+'\t\n')
                            # 整合开始
                            for i, line in enumerate(fr, start=1):
                                mth_stem = self.settings.pat_stem_text.match(line)
                                if mth_stem:
                                    # 章节
                                    if mth_stem.group(3) == '':
                                        fw.write(f'【L{int(mth_stem.group(1))+1!s}】{mth_stem.group(2)}\t\n')
                                    else:
                                        fw.write(f'【L{int(mth_stem.group(1))+1!s}】{mth_stem.group(2)}\t{mth_stem.group(3)}\n')
                                elif self.settings.pat_tab.match(line):
                                    # 词条
                                    mth = self.settings.pat_tab.match(line)
                                    fw.write(f'{mth.group(1)}\t{mth.group(2)}\n')
                                else:
                                    print(Fore.RED + "ERROR: " + Fore.RESET + f"{fname} 第 {i} 行未匹配, 请检查")
                                    pass_flg = False
                                    break_flg = True
                                    break
                        if break_flg:
                            break
        if pass_flg:
            return final_index_all
        else:
            return None

    def _check_raw_files(self):
        """ 检查原材料
        * 必要文本存在(文本编码均要是 utf-8 无 bom)
        * 检查 info.html 的编码
        """
        check_result = []
        # 预定义输入文件路径
        dir_input = self.settings.dir_input
        file_index_all = os.path.join(dir_input, self.settings.fname_index_all)
        file_syns = os.path.join(dir_input, self.settings.fname_syns)
        file_dict_info = os.path.join(dir_input, self.settings.fname_dict_info)
        dir_data = os.path.join(dir_input, self.settings.dname_data)
        # 准备临时文件夹
        dir_index_all = self.settings.dir_index_all
        if os.path.exists(dir_index_all):
            shutil.rmtree(dir_index_all)
            os.makedirs(dir_index_all)
        else:
            os.makedirs(dir_index_all)
        file_index_all = self._check_index_alls(dir_input, dir_index_all)
        # 1.检查索引文件: 必须存在且合格
        if file_index_all:
            check_result.append(file_index_all)
            # 2.检查同义词文件: 若存在就要合格
            syns_check_num = self.func.text_file_check(file_syns)
            if syns_check_num == 0:
                check_result.append(None)
            elif syns_check_num == 2:
                check_result.append(file_syns)
            # 3.检查 info.html: 若存在就要合格
            info_check_num = self.func.text_file_check(file_dict_info)
            if info_check_num == 0:
                check_result.append(None)
            elif info_check_num == 2:
                check_result.append(file_dict_info)
            # 4.检查 data 文件夹
            if os.path.isdir(dir_data) and len(os.listdir(dir_data)) != 0:
                check_result.append(dir_data)
            elif os.path.isdir(dir_data):
                print(Fore.MAGENTA + "WARN: " + Fore.RESET + "data 文件夹为空, 已忽略将不打包")
                check_result.append(None)
            else:
                check_result.append(None)
        # 返回最终检查结果
        if len(check_result) == 4:
            return check_result
        else:
            return None
