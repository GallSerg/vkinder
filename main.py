import os
import vk_user as vk
from dotenv import load_dotenv
from vkinder_db.model_db import create_tables
from vkinder_db.work_with_db import connect_db, Database


if __name__ == '__main__':
    load_dotenv()
    session, engine = connect_db()
    create_tables(engine)
    test = Database()
    group_token = os.environ['vk_group_token']
    user_token = os.environ['vk_user_token']
    vk_client = vk.VkUser(group_token, user_token, '5.131')
    vk_client.msg_listener()



