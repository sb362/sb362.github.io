#!/usr/bin/env python

import sys

import markdown

from flask import Flask, render_template, render_template_string
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask_flatpages import pygments_style_defs

def custom_renderer(template_str):
    markdown_text = render_template_string(template_str)
    pygmented_text = markdown.markdown(markdown_text, extensions=["codehilite", "fenced_code"])
    return pygmented_text

DEBUG = True

FLATPAGES_ROOT = "content"
FLATPAGES_EXTENSION = ".md"
FLATPAGES_HTML_RENDERER = custom_renderer

app = Flask(__name__)
app.config.from_object(__name__)

flat_pages = FlatPages(app)
freezer = Freezer(app)

def sorted_posts():
    unsorted_posts = (page for page in flat_pages if set(("date", "title")) <= page.meta.keys())
    return sorted(unsorted_posts, key=lambda post: post.meta["date"], reverse=True)

@app.route("/")
def index():
    return render_template("index.html", posts=sorted_posts())

@app.route("/posts")
def posts():
    return render_template("posts.html", posts=sorted_posts())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/posts/<path:post_path>")
def post(post_path):
    post = flat_pages.get_or_404(f"posts/{post_path}")
    
    unsorted_posts = (page for page in flat_pages if set(("date", "title")) <= page.meta.keys())
    sorted_posts = sorted(unsorted_posts, key=lambda post: post.meta["date"])
    
    path_parts = post_path.split("/")
    series_path = len(path_parts) > 1 and path_parts[0]
    is_in_series = bool(series_path)

    if is_in_series:
        other_posts = [post for post in sorted_posts if post.path.startswith("posts/" + series_path)]
    else:
        other_posts = sorted_posts[:3]

    i = sorted_posts.index(post)
    prev_post = i > 0 and sorted_posts[i - 1]
    next_post = i < (len(sorted_posts) - 1) and sorted_posts[i + 1]

    return render_template("post.html", post=post, prev_post=prev_post, next_post=next_post,
                           other_posts=other_posts, is_in_series=is_in_series)

@app.route('/pygments.css')
def pygments_theme():
    return pygments_style_defs("colorful"), 200, {"Content-Type": "text/css"}

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(debug=DEBUG)
