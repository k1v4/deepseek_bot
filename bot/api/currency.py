import aiohttp
from settings import config


async def get_currency_rates() -> str:
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    rates = data.get("rates", {})
                    
                    usd_to_rub = rates.get("RUB", None)
                    eur_to_usd = rates.get("EUR", None)
                    gbp_to_usd = rates.get("GBP", None)
                    
                    if not usd_to_rub:
                        return "❌ Не удалось получить курс валют"
                    
                    result = "💱 Курс валют к рублю:\n\n"
                    
                    if usd_to_rub:
                        result += f"🇺🇸 USD: {usd_to_rub:.2f} ₽\n"
                    
                    if eur_to_usd and usd_to_rub:
                        eur_to_rub = usd_to_rub / eur_to_usd
                        result += f"🇪🇺 EUR: {eur_to_rub:.2f} ₽\n"
                    
                    if gbp_to_usd and usd_to_rub:
                        gbp_to_rub = usd_to_rub / gbp_to_usd
                        result += f"🇬🇧 GBP: {gbp_to_rub:.2f} ₽\n"
                    
                    if result == "💱 Курс валют к рублю:\n\n":
                        return "❌ Не удалось получить данные о курсах валют"
                    
                    return result
                else:
                    return f"❌ Ошибка при получении курса валют (код {response.status})"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

