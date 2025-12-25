import aiohttp


async def get_random_joke() -> str:
    try:
        url = "https://official-joke-api.appspot.com/random_joke"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    setup = data.get("setup", "")
                    punchline = data.get("punchline", "")
                    
                    if setup and punchline:
                        result = "😄 Случайная шутка:\n\n"
                        result += f"❓ {setup}\n"
                        result += f"😆 {punchline}"
                        return result
                    else:
                        return "❌ Не удалось получить шутку"
                else:
                    url2 = "https://v2.jokeapi.dev/joke/Any?lang=ru&type=single"
                    async with session.get(url2, timeout=aiohttp.ClientTimeout(total=10)) as response2:
                        if response2.status == 200:
                            data2 = await response2.json()
                            joke_text = data2.get("joke", "")
                            if joke_text:
                                result = "😄 Случайная шутка:\n\n"
                                result += f"😆 {joke_text}"
                                return result
                    
                    return "❌ Ошибка при получении шутки"
    except Exception as e:
        fallback_jokes = [
            "Почему программисты не любят природу? В ней слишком много багов! 🐛",
            "Как называется программист, который не пьет кофе? Не программист! ☕",
            "Почему Python не может быть быстрым? Потому что он ползет! 🐍",
            "Что говорит один байт другому? Мы встретимся на мегабайте! 💾"
        ]
        import random
        return f"😄 Случайная шутка:\n\n😆 {random.choice(fallback_jokes)}"

