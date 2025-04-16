import os
import json
import praw
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Create Reddit instance
def reddit_instance():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

# Sort options menu
sort_by_options = {
    1: "best",
    2: "new",
    3: "top",
    4: "rising",
    5: "hot"
}

# Get user input for subreddit and sorting
def get_user_input():
    subreddit_name = input("Enter a subreddit name (without r/): ")
    print("\nChoose a sort method:")
    for key, value in sort_by_options.items():
        print(f"{key}. {value.capitalize()}")
    try:
        choice = int(input("Enter a number (1-5): "))
    except ValueError:
        choice = 5  # default to hot
    sort_by = sort_by_options.get(choice, "hot")
    return subreddit_name, sort_by

# Fetch posts based on sorting method
def fetch_posts(subreddit, sort_by, limit=10):
    if sort_by == "best":
        return subreddit.best(limit=limit)
    elif sort_by == "new":
        return subreddit.new(limit=limit)
    elif sort_by == "top":
        return subreddit.top(limit=limit)
    elif sort_by == "rising":
        return subreddit.rising(limit=limit)
    else:
        return subreddit.hot(limit=limit)

# Get top 3 comments and first reply for each
def extract_comments(post, max_comments=3):
    post.comments.replace_more(limit=0)
    comments_data = []

    for comment in post.comments[:max_comments]:
        comment_info = {
            "comment_author": str(comment.author),
            "comment_text": comment.body,
            "replies": []
        }

        if comment.replies:
            for reply in comment.replies[:1]:  # First reply only
                comment_info["replies"].append({
                    "reply_author": str(reply.author),
                    "reply_text": reply.body
                })

        comments_data.append(comment_info)

    return comments_data

# Parse all post data
def parse_posts(posts):
    results = []

    for idx, post in enumerate(posts, start=1):
        post_data = {
            "id": idx,
            "url": post.url,
            "author": str(post.author),
            "title": post.title,
            "text": post.selftext,
            "upvotes": post.score,
            "comments": extract_comments(post)
        }
        results.append(post_data)

    return results

# Save to JSON file
def save_to_json(data, folder="reddit_outputs"):
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Create a unique file name based on the current timestamp
    timestamp = int(time.time())  # Or use a more fancy way like UUID
    filename = f"{folder}/output_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\nOutput saved to '{filename}'.")


# Main runner
def main():
    reddit = reddit_instance()
    subreddit_name, sort_by = get_user_input()
    subreddit = reddit.subreddit(subreddit_name)

    try:
        posts = fetch_posts(subreddit, sort_by)
        parsed_data = parse_posts(posts)
        save_to_json(parsed_data)
        print(f"\n✅ Done! {len(parsed_data)} posts saved to 'output.json'.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
