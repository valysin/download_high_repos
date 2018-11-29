import os
import uuid
from DownloadTools import MysqlOperation
from DownloadTools import FormatConvert
from config import config

DOWNLOAD_LIST_PATH = './download_list.txt'

REPO_PATH = config.DEFAULT_PATH
DB_CONFIG = config.REPOSITORY_JAVA_DB

PREFIX_LEN = len('https://github.com')
SEP = '|++*X_-_X*++|'

uuid_list = []
commit_id_list = []
name_list = []
author_list = []
commit_time_list = []
local_addr_list = []

with open(DOWNLOAD_LIST_PATH) as f:

    for line in f.readlines():

        flag = 0

        if os.path.exists(REPO_PATH + line[PREFIX_LEN:-1]):

            if not os.path.exists(REPO_PATH + line[PREFIX_LEN:-1] + '/releases_added'):
                flag = 1

            # if release_updated(): 后续更新
            #    flag = 2

            if flag > 0:
                os.chdir(REPO_PATH + line[PREFIX_LEN:-1])
                tag_name_list = os.popen('git tag -l').readlines()

                for tag_name in tag_name_list:

                    tag_msg_output = os.popen('git show %s ' % tag_name[:-1] + '-q --pretty=format:"%H' + SEP + '%an' + SEP + '%ad"')

                    split = tag_msg_output.readlines()[-1].split('|++*X_-_X*++|')

                    uuid_list.append(uuid.uuid1().__str__())
                    commit_id_list.append(split[0])
                    name_list.append(tag_name)
                    author_list.append(split[1])
                    commit_time = FormatConvert.local_to_utc(split[2])
                    commit_time_list.append(commit_time)
                    local_addr_list.append(line[PREFIX_LEN:-1])


                if flag == 1:
                    with open(REPO_PATH + line[PREFIX_LEN:-1] + '/releases_added', 'w'):
                        pass
                    # os.mknod('./releases_added')

                elif flag == 2:
                    os.system('rm -f ./releases_updated')

    MysqlOperation.insert_into_mysql(
        db_config = DB_CONFIG,
        tablename = 'C/C++_releases',
        params = {
            'uuid': uuid_list,
            'commit_id': commit_id_list,
            'name': name_list,
            'author': author_list,
            'commit_time': commit_time_list,
            'local_addr': local_addr_list
        },
        mode = 'multiple'
    )