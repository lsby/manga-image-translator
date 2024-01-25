import openai
from typing import List

from .common import CommonTranslator

async def 翻译(input_text):
    openai.api_base = "http://localhost:8080/v1"
    openai.api_key = ""

    response = await openai.ChatCompletion.acreate(
        model="sukinishiro",
        messages=[
            { "role": "system", "content": "你是一个轻小说翻译模型,可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文." },

            { "role": "user", "content": "注意: 你需要联系上下文,使用正确使用人称代词,不要擅自添加主语和代词.\n.下面我们开始." },
            { "role": "assistant", "content": "了解,我会尽力遵循你的要求.翻译时我会联系上下文,使用正确使用人称代词,不擅自添加主语和代词." },

            { "role": "user", "content": "ラーメンを食べます" },
            { "role": "assistant", "content": "我吃拉面" },

            { "role": "user", "content": "勉強します" },
            { "role": "assistant", "content": "在学习" },

            { "role": "user", "content": "旅行します" },
            { "role": "assistant", "content": "要去旅行" },

            { "role": "user", "content": input_text }
        ],
        max_tokens=2048,
        temperature=0.1, # 温度, 控制梯度算法的求解随机性, 越大结果越多样, 默认 1
        top_p=0.3, # 选择候选词的范围, 越大结果越多样, 默认 1
        frequency_penalty=0, # 高频词汇惩罚, 越大结果用词越多样, 默认 0
        extra_query={
            'do_sample': False, # 是否使用文本采样, 打开结果会更随机, 默认 True
            'num_beams': 1, # 搜索束宽度, 越大越能生成一致性的结果, 但会牺牲多样性, 默认 1
            'repetition_penalty': 0, # 重复词惩罚, 越大结果用词越多样, 默认 1
        },
    )

    for choice in response.choices:
        if 'text' in choice:
            return choice.text
    return response.choices[0].message.content

def convert_fullwidth_to_halfwidth(input_str):
    result = ''
    for char in input_str:
        if '０' <= char <= '９':
            result += chr(ord(char) - ord('０') + ord('0'))
        else:
            result += char
    return result

class sakuraTranslator(CommonTranslator):

    def supports_languages(self, from_lang: str, to_lang: str, fatal: bool = False) -> bool:
        if to_lang == 'CHS':
            return True
        print("只支持翻译到CHS")
        return False

    async def _translate(self, from_lang: str, to_lang: str, queries: List[str], max_retries: int = 3) -> List[str]:
        translated_results = []
        for query in queries:
            query = convert_fullwidth_to_halfwidth(query)
            print('================')
            print('开始翻译: ' + query)

            for retry_count in range(max_retries):
                try:
                    translation_result = await 翻译(query)
                    print('翻译完成: ' + translation_result)
                    translated_results.append(translation_result)
                    break
                except Exception as e:
                    print(f'翻译出错, 重试中... (重试次数: {retry_count + 1}/{max_retries})')
                    if retry_count == max_retries - 1:
                        print(f'达到最大重试次数, 放弃翻译: {query}')
                        translated_results.append('')
                        break

        return translated_results
