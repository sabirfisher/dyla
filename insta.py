# -*- coding: utf-8 -*-
import instaloader
import os
import logging
import re
import time
from tqdm import tqdm
from dotenv import load_dotenv 
import os
load_dotenv()

# Configure Logging
logging.basicConfig(filename='instaloader_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Instaloader Setup
L = instaloader.Instaloader(download_comments=True,
                             download_video_thumbnails=False,
                             download_geotags=True,
                             save_metadata=True,
                             download_videos=True,
                             post_metadata_txt_pattern="",
                             quiet=True)

# Login Credentials
username = ""
password = os.getenv('PASSWORD')
target_profile = os.getenv('TARGET_PROFILE')


# Function to sanitize and shorten the caption for use in a filename
def sanitize_caption(caption, max_length=80):
    sanitized = re.sub(r'[\\/*?:"<>|]', '', caption)  # Remove special characters
    return sanitized[:max_length]

# Login
try:
    print("\"We all have secrets, but how well can you keep them from the person you love?\"")
    L.login(username, password)
    print("Login Successful.")
    logging.info("Logged in successfully.")
except Exception as e:
    logging.error(f"Login failed: {e}")
    exit("Login failed, check credentials or network status.")

# Download Function
def download_profile(target, L):
    try:
        print("\"Hello, You\"")
        profile = instaloader.Profile.from_username(L.context, target)
        print("Target Found, Downloading...")
        os.makedirs(target, exist_ok=True)
        os.chdir(target)

        posts = profile.get_posts()
        num_posts = profile.mediacount
        with tqdm(total=num_posts, desc="Downloading Posts") as pbar:
            for post in posts:
                caption = sanitize_caption(post.caption) if post.caption else ""
                filename = f"{post.shortcode}_{caption}"
                filename = filename[:250]  
                L.download_post(post, target=filename)
                time.sleep(1)  
                pbar.update(1)

        with open('captions.txt', 'w', encoding='utf-8') as caption_file:
            for post in profile.get_posts():
                caption = sanitize_caption(post.caption) if post.caption else "No caption"
                caption_file.write(f"Shortcode: {post.shortcode}\nCaption: {caption}\n\n")
                if post.caption_hashtags:
                    caption_file.write(f"Shortcode: {post.shortcode}\nHashtags: {post.caption_hashtags}\n\n")
                else:
                    caption_file.write("No hashtag found\n\n")
        
        os.chdir("..")
        print(f"Downloaded profile: {target}")
        logging.info(f"Downloaded profile: {target}")
    except Exception as e:
        print(f"Error downloading profile {target}: {e}")
        logging.error(f"Error downloading profile {target}: {e}")
        os.chdir("..")  # Ensure to change back to the original directory

# Function to get relationships data
def get_relationships(profile, target_profile, L):
    try:
        print("Extracting follower data...")
        followers = [follower.username for follower in profile.get_followers()]
        following = [followee.username for followee in profile.get_followees()]

        os.makedirs(target_profile, exist_ok=True)  # Ensure the target directory exists

        with open(f'{target_profile}/{target_profile}_followers.txt', 'w') as f:
            f.writelines(f"{follower}\n" for follower in followers)
        with open(f'{target_profile}/{target_profile}_following.txt', 'w') as f:
            f.writelines(f"{followee}\n" for followee in following)
        print("Follower data extracted successfully.")
    except Exception as e:
        print(f"Error extracting follower data: {e}")
        logging.error(f"Error extracting follower data: {e}")

# Main execution
if __name__ == "__main__":
    try:
        profile = instaloader.Profile.from_username(L.context, target_profile)
        download_profile(target_profile, L)
        get_relationships(profile, target_profile, L)
        print('Sometimes we have to search for the wrong things for the right reasons.')
    except Exception as e:
        logging.error(f"Error with the profile {target_profile}: {e}")
