import openai
from typing import List

from .common import CommonTranslator

async def 翻译(input_text):
    openai.api_base = "http://localhost:8080/v1"
    openai.api_key = ""

    response = await openai.ChatCompletion.acreate(
        model="sukinishiro",
        messages=[
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
            },
            {
                "role": "user",
                "content": "将下面的日文文本翻译成中文：" + input_text
            }
        ],
        temperature=0.1,
        top_p=0.3,
        max_tokens=512,
        frequency_penalty=0.0,
        seed=-1,
        extra_query={
            'do_sample': False,
            'num_beams': 1,
            'repetition_penalty': 1.0,
        },
    )

    for choice in response.choices:
        if 'text' in choice:
            return choice.text
    return response.choices[0].message.content

def convert_fullwidth_to_halfwidth(input_str):
    result = ''
    for char in input_str:
        # 如果字符是全角数字，进行替换
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
        max_retries = 10

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
                    break  # 如果成功翻译，退出重试循环
                except Exception as e:
                    print(f'翻译出错，重试中... (重试次数: {retry_count + 1}/{max_retries})')
                    if retry_count == max_retries - 1:
                        print(f'达到最大重试次数，放弃翻译: {query}')
                        translated_results.append('')
                        break  # 如果达到最大重试次数，放弃翻译，退出重试循环

        return translated_results
