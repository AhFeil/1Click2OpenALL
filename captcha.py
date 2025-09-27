import httpx


async def verify_captcha(instance_url, site_key, key_secret, captcha_token) -> bool:
    url = f"{instance_url}/{site_key}/siteverify"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "secret": key_secret,
        "response": captcha_token
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json().get("success")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
