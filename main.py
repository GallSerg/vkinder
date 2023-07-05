import vk_user as vk
from vkinder_db.model_db import create_tables
from vkinder_db.work_with_db import connect_db, Database


if __name__ == '__main__':

    session, engine = connect_db()
    create_tables(engine)
    test = Database(session)
    vk_client = vk.VkUser('5.131')
    vk_client.msg_listener()
