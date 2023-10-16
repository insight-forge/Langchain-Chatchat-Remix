import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from datetime import datetime
from server.chat.search_engine_chat import SEARCH_ENGINES
import os
from configs import LLM_MODEL, TEMPERATURE
from server.utils import get_model_worker_config
from typing import List, Dict
import openai

config = get_model_worker_config("gpt-3.5-turbo")
openai.api_type = config.get("OPENAI_API_TYPE", "")
openai.api_key = config.get("OPENAI_API_KEY", "")
openai.api_version = config.get("OPENAI_API_VERSION", "")
openai.api_base = config.get("OPENAI_API_BASE", "")
DEPLOYMENT_ID = config.get("DEPLOYMENT_ID", "")

# config = get_model_worker_config(LLM_MODEL)

PRODUCT_QA_SYSTEM = """你是一名带货主播，正在为店家“{store_name}”直播带货，需要根据带货内容回答买家的问题。请注意，你的回答口吻要符合一名主播的人设，称呼买家为小伙伴。回答内容尽量简洁，如果根据已知信息无法回答问题，请告知买家去咨询商家，不要胡编乱造。带货套餐为：{product_name}，{price}，套餐内容如下：
{product_content}

购买须知如下：
{purchase_notes}"""

# LIVE_OPEN_SYSTEM = """你是“{store_name}”的一名带货主播，正为直播带货做准备。

# 商品列表：
# {products_list}

# 现在你需要为该场直播写一份口播文案的开场白，为接下来的直播带货吸引流量，活跃直播间气氛。
# 开场白的内容包括：首先，介绍主播名字(如果未提供，请为主播取一个名字)，并且亲切的对直播间的观众表示欢迎和问好，可以称呼观众们为家人们，亲们等；然后，抛砖引玉，“预告”带货内容或福利，可以从商品列表中精选出不超过2个商品.
# 文案要尽可能吸引人群，激发观众的好奇心和购买欲望，对商品的描述要生动、详细、丰富。提示观众如果有任何问题，可以现在打在评论区里；
# 直接给出开场白内容，不要做其他修饰。"""
LIVE_OPEN_SYSTEM = """你是“{store_name}”的一名带货主播，正为直播带货做准备。

现在你需要为该场直播写一份口播文案的开场白。
文案目标：为接下来的直播带货吸引流量，活跃直播间气氛，尽可能吸引人群，激发观众的好奇心和购买欲望。
开场白的内容包括：首先，介绍主播名字(如果未提供，请为主播取一个名字)，并且对直播间的观众表示欢迎和问好，可以称呼观众们为家人们，亲们等；然后，幽默接地气的方式简单介绍下店铺的特色特点；最后，提示观众如果在直播期间有任何问题，可以随时打在评论区里。

直接给出开场白内容，不要做其他修饰。"""

PRODUCT_CONTENT_SYSTEM = '''你是“{store_name}”的一名带货主播，以下是你正在直播带货的商品详细信息：
商品：{product_name}
团购详情：
总体价格：{price}

{product_content}

你要详细介绍以上商品，吸引观众下单购买。
现在请按照如下要求进行团品介绍：详细描述团购套餐里包含的内容或项目，数量，原始单价。可以通过情景带入的方式来吸引顾客下单；

请直接给出口播内容，不要做其他修饰。'''
PRODUCT_NOTES_SYSTEM = '''{purchase_notes}

承接上述团品详情介绍，接下来，根据以上购买须知，按照如下要求进行直播：
1、简单介绍购买套餐的注意事项。
2、如果“购买须知”中提供额外的套餐内包含的项目，可以详细讲一下，同样也可以通过情景带入的方式吸引顾客下单；
3、再次强调团品的优惠，需要的请抓紧下单；
4、提示观众如果有任何问题，可以现在打在评论区里。

请直接给出口播内容，不要做其他修饰。'''

LIVE_END_SYSTEM = """你是“{store_name}”的一名带货主播，现在直接已经到达尾声，现在你需要给出你的结束语，表达对观众的支持，并希望下次能与观众再次见面。

请直接给出口播内容，不要做其他修饰。"""

STORE_NAME_DEFAULT = "雾灵山宜山居木屋度假村"
# PRODUCTS_LIST = """1、【4选1】云梦大床房+含早餐＋虹鳟鱼＋亲近小动物, 原价4131.10元，1.4折后现价只要598元。
# 2、【周末不加价】大床房/标间＋虹鳟鱼＋免费垂钓，原价736.50元，5.4折后现价只要398元。
# 3、豪华套房四室一居+虹鳟鱼＋垂钓＋赠送早餐，原价4138元，7.0折后现价只要2880元。"""

PRODUCT_NAME_DEFAULT = "【4选1】云梦大床房+含早餐＋虹鳟鱼＋亲近小动物"
PRICE_DEFAULT = "原价4131.10元，1.4折后现价只要598元"
PRODUCT_CONTENT_DEFAULT = """套餐内容    数量/规格    单价

住 (2选1)
A区田园风光（两室一厅）    1    1698.00
C区观景雅居（两室两露台）    1    1698.00

餐 (2选2)
虹鳟鱼    1    138.00
4 份早餐    1    10

享 (8选8)
阳台休闲桌椅    1    10
影音电视    1    10
一次性拖鞋    1    10
洗浴用品    1    10
全屋畅享高速WIFI    1    10
畅玩沙坑/捞鱼    1    10
篮球场    1    10
足球场    1    10"""
PURCHASE_NOTES_DEFAULT = """1.预约有效期
2023.06.12 至 2023.10.31
2.可入住日期
2023.06.12 至 2023.10.31
3.可用时间
商家营业时间可用
4.预约规则
预约后不可取消和修改
5.购买限制
每单限购1份
6.退款规则
1）下单后若未预约酒店可随时全额退款
2）过期未预约自动全额退款
3）已入住或超时后未入住情况不支持变更或取消订单，预付款将全额扣收。如有特殊情况，请与酒店联系咨询确认
7.其他规则
1）最早入住时间：14:00
2）最晚退房时间：12:00
3）仅接待内宾
4）不与店内优惠同享
5）发票问题请询问商家
6）不可带宠物
7）虹鳟鱼只适用于平日，周末和节假日不适用。
8）下单后若未预约酒店可随时全额退款。
9）过期未预约自动全额退款。
10）预约完成后不可取消/变更。
11）已入住或超时后未入住情况不支持变更或取消订单，预付款将全额扣收。
12）如有特殊情况，请与酒店联系咨询确认。"""

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


def live_stream_page(api: ApiRequest):
    chat_box.init_session()

    with st.sidebar:
        # TODO: 对话模型与会话绑定
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"

            chat_box.reset_history()

            # if mode == "知识库问答":
            #     cur_kb = st.session_state.get("selected_kb")
            #     if cur_kb:
            #         text = f"{text} 当前知识库： `{cur_kb}`。"
            st.toast(text)
            # sac.alert(text, description="descp", type="success", closable=True, banner=True)

        dialogue_mode = st.selectbox("请选择模式：",
                                     ["直播文案",
                                      "商品问答",
                                      ],
                                     index=0,
                                     on_change=on_mode_change,
                                     key="dialogue_mode",
                                     )

        with st.expander("店铺信息", True):
            store_name = st.text_input('店铺名称：', value=STORE_NAME_DEFAULT)
            # if dialogue_mode == "直播文案":
            #     products_list = st.text_area('商品列表：', value=PRODUCTS_LIST, height=1)

        with st.expander("带货商品信息", True):
            product_name = st.text_input('商品名称：', value=PRODUCT_NAME_DEFAULT)
            price = st.text_input('价格：', value=PRICE_DEFAULT)
            product_content = st.text_area('商品内容：', value=PRODUCT_CONTENT_DEFAULT, height=1)
            purchase_notes = st.text_area('购买须知：', value=PURCHASE_NOTES_DEFAULT)

        now = datetime.now()
        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空历史",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.experimental_rerun()

        export_btn.download_button(
            "导出记录",
            # "".join(chat_box.export2md()),
            "".join(chat_box.export2md()),
            file_name=f"{now:%Y-%m-%d %H.%M}_{dialogue_mode}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        temperature = st.slider("Temperature：", 0.0, 1.0, TEMPERATURE, 0.01)

    # Display chat messages from history on app rerun

    if dialogue_mode == "直播文案":
        chat_box.output_messages()

        # chat_input_placeholder = "任意输入，提交后生成文案"
        # if copy_type := st.selectbox("请选文案类型",
        #                              ["",
        #                               "直播开场",
        #                               "商品介绍",
        #                               "直播结束"
        #                               ],
        #                              index=0,
        #                              on_change=on_mode_change,
        #                              key="live_stream_sess",
        #                              ):

        # if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        if st.button('生成文案'):
            chat_box.reset_history()
            chat_box.output_messages()
            # 开场白
            # if copy_type == "直播开场":
            # live_open_prompt = LIVE_OPEN_SYSTEM.format(store_name=store_name, products_list=products_list)
            live_open_prompt = LIVE_OPEN_SYSTEM.format(store_name=store_name)
            messages = [
                {"role": "system", "content": "系统时间：17:00"},
                {'role': 'user', 'content': live_open_prompt}
            ]
            # chat_box.user_say("请生成直播文案")
            # chat_box.user_say(live_open_prompt)
            chat_box.ai_say("正在生成...")
            text = ""
            for chunk in openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_ID,
                    messages=messages,
                    temperature=temperature,
                    stream=True, ):

                if len(chunk["choices"]) > 0 and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0][
                    "delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    text += content
                    chat_box.update_msg(text)
            # chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标

            # 团品内容
            # if copy_type == "商品介绍":
            product_content_prompt = PRODUCT_CONTENT_SYSTEM.format(store_name=store_name,
                                                                   product_name=product_name,
                                                                   price=price,
                                                                   product_content=product_content,
                                                                   )
            messages = [
                {"role": "system", "content": "系统时间：17:00"},
                {'role': 'user', 'content': product_content_prompt}
            ]
            # chat_box.user_say("请生成商品介绍直播文案")
            # chat_box.ai_say("正在生成...")
            # text = ""
            text += "\n\n"
            new_text = ''
            for chunk in openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_ID,
                    messages=messages,
                    temperature=temperature,
                    stream=True, ):

                if len(chunk["choices"]) > 0 and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0][
                    "delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    text += content
                    new_text += content
                    chat_box.update_msg(text)

            messages.append({"role": "assistant", "content": new_text})
            text += "\n\n"
            chat_box.update_msg(text)
            product_notes_prompt = PRODUCT_NOTES_SYSTEM.format(purchase_notes=purchase_notes)
            messages.append({'role': 'user', 'content': product_notes_prompt})
            new_text = ''
            for chunk in openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_ID,
                    messages=messages,
                    temperature=temperature,
                    stream=True, ):

                if len(chunk["choices"]) > 0 and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0][
                    "delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    text += content
                    new_text += content
                    chat_box.update_msg(text)
            messages.append({"role": "assistant", "content": new_text})

            # chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标

            # 结束
            # if copy_type == "直播结束":
            live_end_prompt = LIVE_END_SYSTEM.format(store_name=store_name)
            messages = [
                {'role': 'user', 'content': live_end_prompt}
            ]
            # chat_box.user_say("请生成直播结束文案")
            # chat_box.ai_say("正在生成...")
            # text = ""
            text += "\n\n"
            for chunk in openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_ID,
                    messages=messages,
                    temperature=temperature,
                    stream=True, ):

                if len(chunk["choices"]) > 0 and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0][
                    "delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    text += content
                    chat_box.update_msg(text)

            chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标
            chat_box.reset_history()


    elif dialogue_mode == "商品问答":
        chat_box.output_messages()
        chat_input_placeholder = "请输入关于商品的问题，换行请使用Shift+Enter "
        if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
            #             replace_dict = {
            #                 '{store_name}':store_name,
            #                 '{product_name}':product_name,
            #                 '{store_num}':str(store_num),
            #                 '{price}':price,
            #                 '{product_content}':product_content,
            #                 '{purchase_notes}': purchase_notes}

            #             system_prompt = PRODUCT_QA_SYSTEM.translate(str.maketrans(replace_dict))
            system_prompt = PRODUCT_QA_SYSTEM.replace('{store_name}', store_name).replace('{product_name}',
                                                                                          product_name).replace(
                '{price}', price). \
                replace('{product_content}', product_content).replace('{purchase_notes}', purchase_notes)
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            chat_box.user_say(prompt)
            chat_box.ai_say("正在思考...")
            text = ""
            for chunk in openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_ID,
                    messages=messages,
                    temperature=temperature,
                    stream=True, ):

                if len(chunk["choices"]) > 0 and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0][
                    "delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    text += content
                    chat_box.update_msg(text)

            chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标

#     with st.sidebar:

#         cols = st.columns(2)
#         export_btn = cols[0]
#         if cols[1].button(
#                 "清空对话",
#                 use_container_width=True,
#         ):
#             chat_box.reset_history()
#             st.experimental_rerun()

#         export_btn.download_button(
#             "导出记录",
#             "".join(chat_box.export2md()),
#             file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
#             mime="text/markdown",
#             use_container_width=True,
#         )
#         temperature = st.slider("Temperature：", 0.0, 1.0, TEMPERATURE, 0.01)
