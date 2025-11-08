"""Test video variety - verify different videos are selected each time"""
import sys
import codecs
import asyncio
from app.services.media_sourcing_service import MediaSourcingService
from app.config import settings

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

async def test_video_variety():
    """Test that different videos are selected for the same business type"""

    service = MediaSourcingService(
        unsplash_key=settings.UNSPLASH_API_KEY,
        pexels_key=settings.PEXELS_API_KEY
    )

    business_type = "health_medical"

    print(f"\n{'='*80}")
    print(f"Testing Video Variety for Business Type: {business_type}")
    print(f"{'='*80}\n")

    # Generate 5 videos to show variety
    videos = []
    for i in range(5):
        print(f"\n--- Attempt {i+1} ---")
        video = await service.get_hero_video(
            business_type=business_type,
            min_duration=10,
            max_duration=30
        )

        if video:
            videos.append(video)
            print(f"✓ Video {i+1} URL: {video.url[:80]}...")
            print(f"  Duration: {video.duration}s")
            print(f"  Attribution: {video.attribution}")
        else:
            print(f"✗ No video found for attempt {i+1}")

    # Check for variety
    print(f"\n{'='*80}")
    print(f"RESULTS:")
    print(f"{'='*80}")
    print(f"Total videos fetched: {len(videos)}")

    unique_urls = set(v.url for v in videos)
    print(f"Unique videos: {len(unique_urls)}")

    if len(unique_urls) == len(videos):
        print(f"\n✅ SUCCESS! All {len(videos)} videos are DIFFERENT!")
        print("Video randomization is working perfectly!")
    elif len(unique_urls) > 1:
        print(f"\n⚠️  Got {len(unique_urls)} unique videos out of {len(videos)} attempts")
        print("Some variety achieved, but could be improved")
    else:
        print(f"\n❌ FAILED! All videos are the same")
        print("Video randomization is NOT working")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(test_video_variety())
