from fastapi import FastAPI, HTTPException
import instaloader

app = FastAPI()

@app.get("/profile/{username}")
async def get_profile(username: str):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        profile_data = {
            "username": profile.username,
            "full_name": profile.full_name,
            "bio": profile.biography,
            "profile_pic_url": profile.profile_pic_url,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount
        }
        return profile_data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
