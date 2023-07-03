import os
import vk_user as vk
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()
    group_token = os.environ['vk_group_token']
    user_token = os.environ['vk_user_token']
    vk_client = vk.VkUser(group_token, user_token, '5.131')
    vk_client.msg_listener()



