import httpx
import asyncio
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

API_KEY = "c389ece7b9msh983e6c7bc0dddddp1483d9jsn843ea15d4313"  # Ensure this is correctly configured

@router.get("/youtube/popular-videos")
async def youtube_popular(query: str) -> List[Dict[str, Any]]:
    try:
        return await get_popular_videos(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_with_backoff(url: str, headers: dict, params: dict = None, max_retries: int = 5):
    retries = 0
    while retries < max_retries:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 429:  # Rate limit exceeded
                sleep_time = (2 ** retries)  # Exponential backoff
                await asyncio.sleep(sleep_time)
                retries += 1
            else:
                return response
    raise Exception("Max retries exceeded")

async def get_videos_from_youtube(query: str) -> List[Dict[str, Any]]:
    url = "https://youtube-v2.p.rapidapi.com/search/"
    querystring = {"query": query, "lang": "en", "order_by": "this_month", "country": "us"}
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"}
    response = await fetch_with_backoff(url, headers, querystring)
    return response.json().get("videos", [])

async def get_popular_videos(query: str) -> List[Dict[str, Any]]:
    videos = await get_videos_from_youtube(query)
    popular = []
    async with httpx.AsyncClient() as client:
        for video in videos:
            channel_id = video["channel_id"]
            url = f"https://youtube-v2.p.rapidapi.com/channel/videos?channel_id={channel_id}"
            headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"}
            response = await fetch_with_backoff(url, headers)
            video_json = response.json()
            channel_videos = video_json.get("videos", [])
            if channel_videos:
                total_views = sum(v["number_of_views"] for v in channel_videos)
                average = total_views / len(channel_videos)
                popular.extend(v for v in channel_videos if v["number_of_views"] > average * 2)
    return popular
