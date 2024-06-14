from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import instaloader

app = FastAPI()

# Store sessions in a dictionary
sessions = {}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    L = instaloader.Instaloader()
    try:
        L.login(request.username, request.password)
        sessions[request.username] = L
        return {"message": "Login successful"}
    except instaloader.exceptions.BadCredentialsException:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Instagram Profile Data API!",
        "endpoints": {
            "/profile/{username}": "Fetches Instagram profile data for the given username."
        },
        "example_usage": {
            "url": "/profile/instagram",
            "description": "Fetches the profile data for the username 'instagram'."
        }
    }

@app.get("/profile/{username}")
async def get_profile(username: str, current_user: str = Depends(lambda: None)):
    if current_user not in sessions:
        raise HTTPException(status_code=401, detail="User not logged in")
    
    L = sessions[current_user]
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
    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail="Profile not found")
    except instaloader.exceptions.LoginRequiredException:
        raise HTTPException(status_code=403, detail="Login required to access this profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
